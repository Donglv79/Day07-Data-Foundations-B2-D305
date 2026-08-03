"""Run the shared University Services Retrieval benchmark.

All team members use the same corpus, five frozen queries, and embedding
backend. Change only ``--strategy`` when comparing chunking approaches.

Example (Git Bash):
    export EMBEDDING_PROVIDER=local
    python bench.py --strategy recursive400
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    FixedSizeChunker,
    LocalEmbedder,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = Path("data/university_services_retrieval")

# Git Bash and modern terminals already use UTF-8; this also keeps the script
# usable in Windows consoles that still default to a legacy code page.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class BenchmarkQuery:
    number: int
    question: str
    gold_answer: str
    expected_doc_id: str
    evidence_phrase: str
    metadata_filter: dict[str, str] | None = None


BENCHMARKS = [
    BenchmarkQuery(
        1,
        'Danh hiệu "Tập thể Tiên tiến" yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên?',
        "70%; không có sinh viên xếp loại Yếu trở xuống, trừ các trường hợp được nêu trong quy định.",
        "thi-dua-khen-thuong-uet-2023",
        "70%",
    ),
    BenchmarkQuery(
        2,
        'Điều kiện để sinh viên đạt danh hiệu "Sinh viên Xuất sắc" tại Trường Đại học Công nghệ là gì?',
        "Học tập và rèn luyện loại Xuất sắc, không có học phần nào dưới C+.",
        "thi-dua-khen-thuong-uet-2023",
        "điểm dưới C+",
    ),
    BenchmarkQuery(
        3,
        "Sinh viên Đại học Bách khoa Hà Nội phúc tra hoặc khiếu nại điểm học phần trong thời hạn bao lâu?",
        "Trong 7 ngày từ khi điểm được cập nhật; không áp dụng cho thi vấn đáp hoặc đánh giá trước hội đồng.",
        "quy-che-dao-tao-dai-hoc-hust",
        "7 ngày",
    ),
    BenchmarkQuery(
        4,
        "Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường Đại học Công nghệ.",
        "Thủ khoa ngành học; Sinh viên Xuất sắc; Sinh viên Giỏi; Sinh viên có đóng góp cho công tác tập thể; Sinh viên bảo vệ khóa luận/đồ án tốt nghiệp Xuất sắc; Tập thể Tiên tiến; Tập thể Xuất sắc.",
        "thi-dua-khen-thuong-uet-2023",
        "Thủ khoa ngành học",
    ),
    BenchmarkQuery(
        5,
        "Quy định tạo điều kiện tham gia hoạt động nghiên cứu khoa học, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào?",
        "Sinh viên thuộc các chương trình đào tạo Tài năng, nhóm ELITECH, của ĐHBK Hà Nội.",
        "quy-che-dao-tao-dai-hoc-hust",
        "CTĐT Tài năng",
        metadata_filter={"audience": "student"},
    ),
]


def select_embedder():
    """Use local multilingual embeddings when configured, otherwise mock."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(
                model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL)
            )
        except Exception as error:
            print(f"Local embedder không sẵn sàng ({error}); dùng mock embeddings.")
    return _mock_embed


def choose_chunker(strategy: str):
    """Return one of the agreed strategy configurations."""
    strategies = {
        "recursive400": ("RecursiveChunker(chunk_size=400)", RecursiveChunker(chunk_size=400)),
        "fixed500": (
            "FixedSizeChunker(chunk_size=500, overlap=50)",
            FixedSizeChunker(chunk_size=500, overlap=50),
        ),
        "sentence3": ("SentenceChunker(max_sentences_per_chunk=3)", SentenceChunker(3)),
        "fixed300": (
            "FixedSizeChunker(chunk_size=300, overlap=60)",
            FixedSizeChunker(chunk_size=300, overlap=60),
        ),
        "recursive650": ("RecursiveChunker(chunk_size=650)", RecursiveChunker(chunk_size=650)),
    }
    return strategies[strategy]


def preview(text: str, limit: int = 180) -> str:
    return " ".join(text.split())[:limit]


def has_evidence(results: list[dict], query: BenchmarkQuery) -> bool:
    phrase = query.evidence_phrase.casefold()
    return any(
        result["metadata"].get("doc_id") == query.expected_doc_id
        and phrase in result["content"].casefold()
        for result in results
    )


def print_results(label: str, results: list[dict], query: BenchmarkQuery) -> None:
    print(f"  {label}")
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(
            f"    {rank}. score={result['score']:.4f} "
            f"doc_id={metadata.get('doc_id')} chunk={metadata.get('chunk_index')}"
        )
        print(f"       {preview(result['content'])}")
    print(f"    Bằng chứng gold xuất hiện trong Top-3: {has_evidence(results, query)}")


def run_benchmark(strategy: str) -> int:
    if not DATA_DIR.exists():
        print(f"Không tìm thấy corpus: {DATA_DIR}")
        return 1

    label, chunker = choose_chunker(strategy)
    embedding_fn = select_embedder()
    backend = getattr(embedding_fn, "_backend_name", embedding_fn.__class__.__name__)
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedding_fn, chunker=chunker)

    print("=== University Services Retrieval Benchmark ===")
    print(f"Corpus: {DATA_DIR}")
    print(f"Strategy: {label}")
    print(f"Embedding backend: {backend}")
    print(f"Chunks indexed: {store.get_collection_size()}")
    if backend == "mock embeddings fallback":
        print("WARNING: mock embeddings chỉ xác minh luồng kỹ thuật, không dùng để kết luận chất lượng ngữ nghĩa.")

    for query in BENCHMARKS:
        print(f"\n=== Q{query.number}: {query.question} ===")
        print(f"Gold answer: {query.gold_answer}")
        if query.metadata_filter:
            unfiltered = store.search(query.question, top_k=3)
            filtered = store.search_with_filter(
                query.question, top_k=3, metadata_filter=query.metadata_filter
            )
            print_results("A. Không filter", unfiltered, query)
            print_results(f"B. Filter {query.metadata_filter}", filtered, query)
        else:
            print_results("Top-3", store.search(query.question, top_k=3), query)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategy",
        choices=["recursive400", "fixed500", "sentence3", "fixed300", "recursive650"],
        default="recursive400",
        help="Only this value should differ between team members.",
    )
    args = parser.parse_args()
    return run_benchmark(args.strategy)


if __name__ == "__main__":
    raise SystemExit(main())
