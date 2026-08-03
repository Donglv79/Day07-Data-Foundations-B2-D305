#!/usr/bin/env python3
"""Fetch a small, permitted set of public PDF files into Markdown files.

This helper mirrors fetch_public_pages.py for PDF sources: it checks robots.txt,
waits between requests, accepts only PDF responses, extracts text/Markdown with
an installed PDF library, and writes one cleaned .md file plus sources.csv.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import tempfile
import time
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


DEFAULT_USER_AGENT = "Day7DataFoundationsCourse/1.0 (+educational-lab)"
MANIFEST_FIELDS = [
    "doc_id",
    "file_path",
    "title",
    "source_url",
    "retrieved_at",
    "document_version",
    "license_or_permission",
]
SAFE_METADATA_KEY = re.compile(r"^[a-z][a-z0-9_]*$")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "document"


def yaml_value(value: str) -> str:
    """Return one safe, quoted YAML scalar without needing PyYAML."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        if not reader.fieldnames or "url" not in reader.fieldnames:
            raise ValueError("Input CSV must have a 'url' column.")
        rows = []
        for number, row in enumerate(reader, start=2):
            cleaned = {key.strip(): (value or "").strip() for key, value in row.items() if key}
            if not cleaned.get("url"):
                print(f"Skipping row {number}: missing url", file=sys.stderr)
                continue
            rows.append(cleaned)
    return rows


def robots_allowed(url: str, user_agent: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print(f"Skipping unsupported URL: {url}", file=sys.stderr)
        return False

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser(robots_url)
    try:
        parser.read()
    except (HTTPError, URLError, OSError) as error:
        print(f"Skipping {url}: cannot verify {robots_url} ({error})", file=sys.stderr)
        return False
    if not parser.can_fetch(user_agent, url):
        print(f"Skipping {url}: disallowed by robots.txt", file=sys.stderr)
        return False
    return True


def looks_like_pdf(url: str, content_type: str) -> bool:
    path = urlparse(url).path.lower()
    return content_type in {"application/pdf", "application/x-pdf"} or path.endswith(".pdf")


def fetch_pdf(url: str, user_agent: str, timeout: float, max_bytes: int) -> tuple[str, bytes]:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/pdf,*/*;q=0.1"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URL is supplied by the course user.
        final_url = response.geturl()
        content_type = response.headers.get_content_type().lower()
        if not looks_like_pdf(final_url, content_type):
            raise ValueError(f"unsupported content type for PDF fetch: {content_type}")

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_bytes:
            raise ValueError(f"PDF is larger than --max-mb ({content_length} bytes)")

        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("PDF is larger than --max-mb")
        if not body.lstrip().startswith(b"%PDF"):
            raise ValueError("downloaded content does not look like a PDF")
        return final_url, body


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def extract_with_pymupdf4llm(pdf_bytes: bytes) -> str:
    import pymupdf4llm  # type: ignore[import-not-found]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(pdf_bytes)
    try:
        return str(pymupdf4llm.to_markdown(str(temp_path)))
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass


def extract_with_pymupdf(pdf_bytes: bytes) -> str:
    import fitz  # type: ignore[import-not-found]

    parts: list[str] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_index, page in enumerate(document, start=1):
            page_text = clean_text(page.get_text("text"))
            if page_text:
                parts.append(f"## Page {page_index}\n\n{page_text}")
    return "\n\n".join(parts)


def extract_with_pypdf(pdf_bytes: bytes) -> str:
    from pypdf import PdfReader  # type: ignore[import-not-found]

    reader = PdfReader(BytesIO(pdf_bytes))
    parts = []
    for page_index, page in enumerate(reader.pages, start=1):
        page_text = clean_text(page.extract_text() or "")
        if page_text:
            parts.append(f"## Page {page_index}\n\n{page_text}")
    return "\n\n".join(parts)


def extract_pdf_content(pdf_bytes: bytes) -> str:
    extractors: list[tuple[str, Any]] = [
        ("pymupdf4llm", extract_with_pymupdf4llm),
        ("PyMuPDF", extract_with_pymupdf),
        ("pypdf", extract_with_pypdf),
    ]
    import_errors = []
    extraction_errors = []
    for name, extractor in extractors:
        try:
            return clean_text(extractor(pdf_bytes))
        except ImportError as error:
            import_errors.append(f"{name}: {error}")
        except Exception as error:  # PDF parsers expose many exception types.
            extraction_errors.append(f"{name}: {error}")

    details = "; ".join(extraction_errors or import_errors)
    raise RuntimeError(
        "No PDF extractor succeeded. Install one option, for example: "
        "python -m pip install pymupdf4llm  (or PyMuPDF / pypdf). "
        f"Details: {details}"
    )


def existing_manifest(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as manifest_file:
        return {row["doc_id"]: row for row in csv.DictReader(manifest_file) if row.get("doc_id")}


def write_manifest(path: Path, records: dict[str, dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for doc_id in sorted(records):
            writer.writerow({field: records[doc_id].get(field, "") for field in MANIFEST_FIELDS})


def markdown_document(metadata: dict[str, str], content: str) -> str:
    front_matter = "\n".join(f"{key}: {yaml_value(value)}" for key, value in metadata.items())
    return f"---\n{front_matter}\n---\n\n# {metadata['title']}\n\n{content}\n"


def title_from_url(url: str) -> str:
    path = unquote(urlparse(url).path)
    stem = Path(path).stem
    return re.sub(r"[_-]+", " ", stem).strip()


def build_metadata(row: dict[str, str], final_url: str) -> dict[str, str]:
    fallback_title = title_from_url(final_url)
    document_id = slugify(row.get("doc_id") or fallback_title)
    metadata = {
        "doc_id": document_id,
        "title": row.get("title") or fallback_title or document_id.replace("-", " ").title(),
        "source_url": final_url,
        "retrieved_at": date.today().isoformat(),
        "document_version": row.get("document_version") or "not-stated",
    }
    for key, value in row.items():
        if key not in {"url", "doc_id", "title", "document_version", "license_or_permission"} and value and SAFE_METADATA_KEY.match(key):
            metadata[key] = value
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch a small list of allowed public PDFs into Markdown.")
    parser.add_argument("input_csv", type=Path, help="CSV with a required 'url' column")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for .md files and sources.csv")
    parser.add_argument("--delay", type=float, default=1.0, help="Minimum seconds between requests (default: 1.0)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout in seconds (default: 30)")
    parser.add_argument("--max-mb", type=float, default=50.0, help="Maximum PDF size in MiB (default: 50)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP User-Agent")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing Markdown file with the same doc_id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.delay < 1:
        print("--delay must be at least 1 second to respect source websites.", file=sys.stderr)
        return 2
    if args.max_mb <= 0:
        print("--max-mb must be greater than 0.", file=sys.stderr)
        return 2
    if not args.input_csv.is_file():
        print(f"Input file not found: {args.input_csv}", file=sys.stderr)
        return 2

    try:
        rows = load_rows(args.input_csv)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "sources.csv"
    manifest = existing_manifest(manifest_path)
    max_bytes = int(args.max_mb * 1024 * 1024)
    successful = 0
    failed = 0

    for index, row in enumerate(rows):
        url = row["url"]
        if not robots_allowed(url, args.user_agent):
            failed += 1
            continue
        if index:
            time.sleep(args.delay)
        try:
            final_url, pdf_bytes = fetch_pdf(url, args.user_agent, args.timeout, max_bytes)
            content = extract_pdf_content(pdf_bytes)
            if len(content) < 80:
                raise ValueError("extracted content is too short; the PDF may be scanned or protected")
            metadata = build_metadata(row, final_url)
            output_path = args.output_dir / f"{metadata['doc_id']}.md"
            if output_path.exists() and not args.overwrite:
                raise FileExistsError(f"{output_path} exists (use --overwrite to replace it)")
            output_path.write_text(markdown_document(metadata, content), encoding="utf-8")
            manifest[metadata["doc_id"]] = {
                "doc_id": metadata["doc_id"],
                "file_path": str(output_path),
                "title": metadata["title"],
                "source_url": metadata["source_url"],
                "retrieved_at": metadata["retrieved_at"],
                "document_version": metadata["document_version"],
                "license_or_permission": row.get("license_or_permission") or "public-pdf",
            }
            successful += 1
            print(f"Saved {output_path}")
        except (HTTPError, URLError, TimeoutError, UnicodeError, ValueError, RuntimeError, OSError) as error:
            failed += 1
            print(f"Skipping {url}: {error}", file=sys.stderr)

    write_manifest(manifest_path, manifest)
    print(f"Finished: {successful} saved, {failed} skipped. Manifest: {manifest_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
