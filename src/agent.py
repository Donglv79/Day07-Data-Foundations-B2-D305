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

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy ngữ cảnh liên quan trong cơ sở tri thức để trả lời."

        context_lines = []
        for index, result in enumerate(results, start=1):
            source = result["metadata"].get("doc_id") or result["id"]
            context_lines.append(f"[{index}] (doc: {source}) {result['content']}")
        context = "\n".join(context_lines)

        prompt = (
            "Chỉ trả lời dựa trên ngữ cảnh (context) dưới đây. "
            "Nếu ngữ cảnh không đủ thông tin, hãy nói rõ điều đó.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
