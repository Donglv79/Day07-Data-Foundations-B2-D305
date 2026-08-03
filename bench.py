from __future__ import annotations

import argparse
import os
import sys
from textwrap import shorten
from typing import Any

from dotenv import load_dotenv

from ingest import build_knowledge_base
from query_benchmark import BENCHMARK_QUERIES, BenchmarkQuery
from src.agent import KnowledgeBaseAgent
from src.chunking import ArticleChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    LocalEmbedder,
    _mock_embed,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DEFAULT_DATA_DIR = "data/university_services_retrieval"


def select_embedder(provider: str):
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception as error:
            print(f"Local embedder unavailable ({error}); falling back to mock.")
    return _mock_embed


def demo_llm(prompt: str) -> str:
    """Cheap deterministic stand-in for an LLM while benchmarking retrieval."""
    context_start = prompt.find("Context:")
    question_start = prompt.find("Question:")
    context = prompt[context_start:question_start].strip() if context_start != -1 and question_start != -1 else prompt
    return "[MOCK LLM] Inspect retrieved context before trusting this answer. " + shorten(
        context.replace("\n", " "), width=360, placeholder="..."
    )


def contains_required_snippet(results: list[dict[str, Any]], benchmark: BenchmarkQuery) -> bool:
    context = "\n".join(result["content"] for result in results).lower()
    return any(snippet.lower() in context for snippet in benchmark.required_snippets)


def print_results(benchmark: BenchmarkQuery, results: list[dict[str, Any]]) -> None:
    print(f"\nQ{benchmark.id}: {benchmark.query}")
    print(f"Gold doc: {benchmark.expected_doc_id} ({benchmark.expected_location})")
    print(f"Gold answer: {benchmark.gold_answer}")
    if benchmark.metadata_filter:
        print(f"metadata_filter: {benchmark.metadata_filter}")
    print(f"Relevant snippet in top-3: {'yes' if contains_required_snippet(results, benchmark) else 'no'}")

    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})
        preview = shorten(result["content"].replace("\n", " "), width=220, placeholder="...")
        print(
            f"  Top {index}: score={result['score']:.3f} "
            f"doc_id={metadata.get('doc_id')} chunk_index={metadata.get('chunk_index')}"
        )
        print(f"    {preview}")


def run_benchmark(data_dir: str, provider: str, chunk_size: int, overlap: int, include_ab_filter: bool) -> int:
    load_dotenv(override=False)
    os.environ.setdefault(EMBEDDING_PROVIDER_ENV, provider)
    embedder = select_embedder(provider)
    backend = getattr(embedder, "_backend_name", "mock embeddings fallback")

    # This is the only strategy line expected to differ across team members.
    chunker = ArticleChunker(chunk_size=chunk_size, overlap=overlap)

    store = build_knowledge_base(data_dir, embedding_fn=embedder, chunker=chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    print("=== Benchmark ===")
    print(f"Data dir: {data_dir}")
    print(f"Embedder: {backend}")
    print(f"Strategy: ArticleChunker(chunk_size={chunk_size}, overlap={overlap})")
    print(f"Loaded chunks: {store.get_collection_size()}")
    if backend == "mock embeddings fallback":
        print("Note: mock embeddings check pipeline behavior, not semantic retrieval quality.")

    for benchmark in BENCHMARK_QUERIES:
        results = (
            store.search_with_filter(benchmark.query, top_k=3, metadata_filter=benchmark.metadata_filter)
            if benchmark.metadata_filter
            else store.search(benchmark.query, top_k=3)
        )
        print_results(benchmark, results)
        print("  Agent:", agent.answer(benchmark.query, top_k=3, metadata_filter=benchmark.metadata_filter))

        if include_ab_filter and benchmark.metadata_filter:
            unfiltered = store.search(benchmark.query, top_k=3)
            print("  A/B without filter:")
            print_results(benchmark, unfiltered)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the 5-query retrieval benchmark.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--embedding-provider", choices=["mock", "local"], default=os.getenv(EMBEDDING_PROVIDER_ENV, "mock"))
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=100)
    parser.add_argument("--ab-filter", action="store_true", help="Also run unfiltered search for filtered queries.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_benchmark(
        data_dir=args.data_dir,
        provider=args.embedding_provider,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        include_ab_filter=args.ab_filter,
    )


if __name__ == "__main__":
    raise SystemExit(main())
