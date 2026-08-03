"""bench.py — chạy benchmark retrieval cho Lab 7 (Giai đoạn 2 / CHECKPOINT 6).

Mỗi thành viên chỉ đổi DÒNG CHỌN CHUNKER bên dưới (mục 1). Mọi thứ khác giữ
nguyên để so sánh công bằng: cùng corpus, cùng 5 query, cùng embedder, cùng top_k.

Đầu ra gồm: strategy + params, số chunk đã nạp, với mỗi query:
  - top-3 chunk (score, doc_id, NỘI DUNG ĐẦY ĐỦ — để chấm ở mức chunk)
  - auto-check "chuỗi đặc trưng" (evidence string) xuất hiện trong top-1/top-3
  - gợi ý điểm 2/1/0
  - câu trả lời agent
  - Q5: A/B có/không metadata_filter

Cách chạy:
    python bench.py                  # mock embedder (ko có ý nghĩa ngữ nghĩa)
    EMBEDDING_PROVIDER=local python bench.py   # sentence-transformers đa ngữ (cài requirements-local.txt)
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    LocalEmbedder,
    _mock_embed,
)

DATA_DIR = "data/university_services_retrieval"

# =====================================================================
# 1. CHỌN CHIẾN LƯỢC CỦA BẠN — DÒNG DUY NHẤT KHÁC NHAU GIỮA CÁC THÀNH VIÊN
# =====================================================================
chunker = RecursiveChunker(chunk_size=400)
# =====================================================================

# 5 benchmark query đã chốt của nhóm + "chuỗi đặc trưng" phải có trong top-3 để tính điểm.
QUERIES = [
    {
        "id": "Q1",
        "query": "Danh hiệu 'Tập thể Tiên tiến' yêu cầu tối thiểu bao nhiêu phần trăm sinh "
                 "viên đạt kết quả học tập và rèn luyện loại Khá trở lên?",
        "filter": None,
        "evidence": ["70%"],
    },
    {
        "id": "Q2",
        "query": "Điều kiện để sinh viên đạt danh hiệu 'Sinh viên Xuất sắc' tại Trường Đại "
                 "học Công nghệ là gì?",
        "filter": None,
        "evidence": ["C+"],
    },
    {
        "id": "Q3",
        "query": "Sinh viên Đại học Bách khoa Hà Nội phúc tra hoặc khiếu nại điểm học phần "
                 "trong thời hạn bao lâu?",
        "filter": None,
        "evidence": ["7 ngày", "phúc tra"],
    },
    {
        "id": "Q4",
        "query": "Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường "
                 "Đại học Công nghệ.",
        "filter": None,
        "evidence": ["Sinh viên Xuất sắc", "Sinh viên Giỏi", "Tập thể Xuất sắc", "Thủ khoa"],
    },
    {
        "id": "Q5",
        "query": "Quy định tạo điều kiện tham gia hoạt động nghiên cứu khoa học, trao đổi học "
                 "thuật và công nhận tín chỉ áp dụng cho đối tượng nào?",
        "filter": {"audience": "student"},
        "evidence": ["Tài năng", "ELITECH"],
    },
]


def _select_embedder():
    """Chọn backend nhúng theo EMBEDDING_PROVIDER (mock | local | openai)."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
    return _mock_embed


def demo_llm(prompt: str) -> str:
    """LLM giả lập (thay bằng LLM thật khi cần đánh giá chất lượng câu trả lời)."""
    return f"[DEMO LLM] {prompt.split('Answer:', 1)[-1].strip()[:400]}..."


def evidence_hits(results, evidence: list[str]) -> dict:
    """Trả về danh sách (rank, evidence_hit) cho top-k. 0-based rank."""
    hits = []
    for rank, result in enumerate(results, start=1):
        content = result["content"]
        found = [ev for ev in evidence if ev.lower() in content.lower()]
        hits.append((rank, found))
    return hits


def suggest_score(hits) -> int:
    """2: evidence ở top-1 · 1: evidence trong top-3 (không phải top-1) · 0: không có."""
    for rank, found in hits:
        if rank == 1 and found:
            return 2
    for rank, found in hits:
        if found:
            return 1
    return 0


def run_query(store, agent, qid, query, evidence, metadata_filter, top_k=3):
    """Chạy 1 query và in kết quả + gợi ý điểm. Trả (qid, suggest_score)."""
    label = f"{qid}" + (f" [filter={metadata_filter}]" if metadata_filter else "")
    print(f"\n--- {label}: {query}")

    if metadata_filter:
        results = store.search_with_filter(query, top_k=top_k, metadata_filter=metadata_filter)
    else:
        results = store.search(query, top_k=top_k)

    for index, result in enumerate(results, start=1):
        doc_id = result["metadata"].get("doc_id", "?")
        print(f"    [{index}] score={result['score']:.4f} doc={doc_id}")
        for line in result["content"].splitlines():
            print(f"        | {line}")

    hits = evidence_hits(results, evidence)
    print(f"    evidence cần: {evidence}")
    for rank, found in hits:
        print(f"    top-{rank}: {'TÌM THẤY ' + str(found) if found else 'không có evidence'}")

    score = suggest_score(hits)
    print(f"    => gợi ý điểm: {score}/2")
    print(f"    agent: {agent.answer(query, top_k=top_k)}")
    return qid, score


def main() -> int:
    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print(f"== Chiến lược: {chunker.__class__.__name__} "
          f"params={getattr(chunker, '__dict__', {})}")
    print(f"== Embedder: {backend} | Corpus: {DATA_DIR}")
    if backend == "mock embeddings fallback":
        print("== LƯU Ý: mock không phản ánh ngữ nghĩa — chỉ đánh giá luồng kỹ thuật, "
              "số chunk, coherence, provenance.")

    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    print(f"== Số chunk đã nạp: {store.get_collection_size()}")
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    scores = []
    for item in QUERIES:
        if item["id"] == "Q5":
            # A/B: không filter vs có filter
            run_query(store, agent, item["id"] + "-NOFILTER", item["query"],
                      item["evidence"], None)
            qid, score = run_query(store, agent, item["id"] + "-FILTER", item["query"],
                                   item["evidence"], item["filter"])
            scores.append(("Q5 (có filter)", score))
        else:
            qid, score = run_query(store, agent, item["id"], item["query"],
                                   item["evidence"], item["filter"])
            scores.append((qid, score))

    print("\n== BẢNG TỔNG KẾT ĐIỂM (gợi ý, theo evidence string)")
    total = 0
    for qid, score in scores:
        total += score
        print(f"    {qid}: {score}/2")
    print(f"    Tổng: {total}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
