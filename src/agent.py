from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        if metadata_filter is None:
            results = self.store.search(question, top_k=top_k)
        else:
            results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
        if not results:
            return "I do not have enough context to answer this question."

        context_blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            doc_id = metadata.get("doc_id") or result.get("id", "unknown")
            source = metadata.get("source_url") or metadata.get("source") or "unknown-source"
            context_blocks.append(
                f"[{index}] doc_id={doc_id} source={source}\n{result['content']}"
            )

        prompt = (
            "Use only the context below to answer the question. "
            "If the context is not sufficient, say that the context is not sufficient. "
            "Cite the relevant context numbers like [1] when possible.\n\n"
            "Context:\n"
            f"{chr(10).join(context_blocks)}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
