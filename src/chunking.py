from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if sentence.strip()
        ]
        return [
            " ".join(sentences[index : index + self.max_sentences_per_chunk])
            for index in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        return [chunk.strip() for chunk in self._split(text, self.separators) if chunk.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        lower_priority = remaining_separators[1:]
        if separator == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        if separator not in current_text:
            return self._split(current_text, lower_priority)

        chunks: list[str] = []
        current_parts: list[str] = []
        current_length = 0
        for part in current_text.split(separator):
            if not part:
                continue
            piece_length = len(part)
            separator_length = len(separator) if current_parts else 0
            projected_length = current_length + separator_length + piece_length

            if current_parts and projected_length > self.chunk_size:
                chunks.append(separator.join(current_parts))
                current_parts = [part]
                current_length = piece_length
            else:
                current_parts.append(part)
                current_length = projected_length

        if current_parts:
            chunks.append(separator.join(current_parts))

        result: list[str] = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                result.extend(self._split(chunk, lower_priority))
            else:
                result.append(chunk)
        return result


class ArticleChunker:
    """
    Split Vietnamese regulation documents by article headings such as
    "Điều 4:" or "Điều 6. ...".

    If an article is too long, split its body recursively and prefix the article
    heading to every sub-chunk so later chunks keep their legal context.
    """

    ARTICLE_HEADING = re.compile(r"(?im)^Điều\s+\d+[.:]\s+.*$")
    TOC_DOTS = re.compile(r"\.{5,}")

    def __init__(self, chunk_size: int = 900, overlap: int = 100, fallback_chunk_size: int | None = None) -> None:
        self.chunk_size = chunk_size
        self.overlap = max(0, overlap)
        self.fallback = RecursiveChunker(chunk_size=fallback_chunk_size or chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        matches = [
            match
            for match in self.ARTICLE_HEADING.finditer(text)
            if not self.TOC_DOTS.search(match.group(0))
        ]
        if not matches:
            return self.fallback.chunk(text)

        chunks: list[str] = []
        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.extend(self.fallback.chunk(preamble))

        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section = text[start:end].strip()
            if not section:
                continue
            chunks.extend(self._chunk_article(section))
        return chunks

    def _chunk_article(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]

        lines = section.splitlines()
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            return self.fallback.chunk(section)

        max_body_size = max(1, self.chunk_size - len(heading) - 2)
        overlap = min(self.overlap, max(0, max_body_size - 1))
        body_chunks = FixedSizeChunker(chunk_size=max_body_size, overlap=overlap).chunk(body)
        return [f"{heading}\n{body_chunk}".strip() for body_chunk in body_chunks if body_chunk.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(chunk) for chunk in chunks) / count if count else 0
            comparison[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return comparison
