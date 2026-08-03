# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Viết Huy (2A202601081)
**Nhóm:** B2
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding trỏ về gần như cùng một hướng trong không gian vector, tức hai đoạn văn bản có ngữ nghĩa gần nhau (bất kể độ dài/độ lớn vector).

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên đăng ký học phần thông qua cổng học vụ.
- Câu B: Học phần được đăng ký trên hệ thống học vụ của trường.
- Tại sao tương đồng: Từ vựng khác nhau nhưng cùng mô tả một hành động và một đối tượng (đăng ký học phần qua cổng học vụ) → embedding nằm gần nhau về hướng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên đăng ký học phần thông qua cổng học vụ.
- Câu B: Thư viện mở cửa lúc 8 giờ sáng các ngày trong tuần.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau (học vụ vs. thư viện), không chia sẻ ngữ nghĩa → vector gần như vuông góc, cosine thấp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ so sánh hướng (góc) giữa hai vector nên bỏ qua độ dài; text embedding thường bị ảnh hưởng bởi số token (văn bản dài → vector dài), nên Euclid sẽ đánh giá thấp hai câu cùng ý nhưng khác độ dài. Cosine phản ánh "sự tương tự về ngữ nghĩa" tốt hơn và không bị phồng theo độ lớn vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23
> *Đáp án:* **23 chunks** (khớp vòng lặp `range(0, 10000, 450)` của `FixedSizeChunker`).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Overlap tăng → số chunk **tăng**: ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = **25**. Đánh đổi: overlap lớn hơn giữ được nhiều ngữ cảnh liên tục hơn giữa các chunk liền kề (giảm nguy cơ cắt đứt ý), nhưng làm tăng số chunk, tăng chi phí nhúng (embedding) và độ trùng lặp dữ liệu lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r"(?<=[.!?])\s+", text)` — lookbehind giữ dấu câu ở phần đứng trước và tách tại khoảng trắng sau dấu câu (bao gồm cả `.\n`). Mỗi câu được `strip()` và bỏ rỗng, sau đó gom từng nhóm `max_sentences_per_chunk` câu ghép bằng dấu cách. Edge case: text rỗng → `[]`, text không có dấu câu → trả nguyên cả text như một chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` xử lý text rỗng rồi gọi đệ quy `_split(text, separators)` và bỏ chunk rỗng. `_split` có 2 base case: text đã ≤ `chunk_size` → trả `[text]`; hết separator hoặc separator rỗng → cắt cố định bằng `_cut_fixed`. Separator không xuất hiện → thử separator kế tiếp. Nếu split được: gom các phần liền kề cho tới khi vượt `chunk_size` (chunk hợp lệ được giữ), phần quá dài → đệ quy lại với danh sách separator còn lại — nhờ đó luôn tiến tới điều kiện dừng, không lặp vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu in-memory vào `_store`: `add_documents` gọi `_make_record` cho từng `Document` (record gồm `id` = `doc.id::<index>` đảm bảo duy nhất, `content`, bản sao `metadata` + luôn có `doc_id` chỉ file gốc, và `embedding`). `search` nhúng query một lần, dùng helper `_search_records` tính dot product với từng record, sort giảm dần theo `score` rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Filter **trước**, rank sau: `search_with_filter` lọc `_store` theo từng cặp key/value trong `metadata_filter` (nếu `None` thì dùng toàn bộ store, đúng bằng `search`) rồi mới đưa vào `_search_records` — tránh tình trạng lấy top-k xong mới lọc còn 0 kết quả. `delete_document` lọc lại `_store`, bỏ mọi record có `metadata["doc_id"] == doc_id`, so sánh độ dài trước/sau để trả `True`/`False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search(question, top_k)` để lấy top-k chunk. Nếu store rỗng → trả thông báo rõ ràng, không gọi LLM vô ích. Ngược lại, ghép các chunk thành `Context` có đánh số `[1]`, `[2]` kèm `doc_id` (từ metadata) để truy vết, rồi build prompt gồm hướng dẫn "chỉ dùng context, nói rõ khi thiếu", `Context`, `Question`, nhãn `Answer:` và gọi `llm_fn(prompt)`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên phải đạt điểm trung bình tích lũy từ 2,0 trở lên để được xét tốt nghiệp. | Điều kiện tốt nghiệp yêu cầu GPA tích lũy tối thiểu 2,0. | cao | 0.518 | ✔ (cao) |
| 2 | Danh hiệu Sinh viên Xuất sắc yêu cầu không có học phần nào dưới C+. | Sinh viên Xuất sắc không được có điểm học phần dưới C+. | cao | 0.860 | ✔ (cao) |
| 3 | Thư viện mở cửa từ 8 giờ sáng đến 9 giờ tối. | Quy chế đào tạo quy định tín chỉ và điểm trung bình tích lũy. | thấp | 0.681 | ✘ (cao) |
| 4 | Sinh viên được phép phúc tra điểm trong thời hạn 7 ngày. | Khiếu nại điểm học phần phải thực hiện trong thời hạn 7 ngày. | cao | 0.897 | ✔ (cao) |
| 5 | Đăng ký học phần được thực hiện trên cổng học vụ. | Thư viện cho mượn tối đa 5 cuốn sách trong thời hạn 1 tháng. | thấp | 0.710 | ✘ (cao) |

> Điểm tính bằng `compute_similarity()` trên embedding local `paraphrase-multilingual-MiniLM-L12-v2` (chuẩn hóa). Đúng/✔ với ngưỡng cao ≥ 0.6, thấp < 0.6.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 3 và 5**: dự đoán "thấp" nhưng thực tế lên tới ~0.68–0.71. Nguyên nhân: cả 5 cặp đều là câu tiếng Việt cùng lĩnh vực học thuật nên dùng chung nhiều từ vựng (thư viện, đào tạo, học phần, quy chế…); embedding đa ngữ MiniLM đo **độ gần về chủ đề/từ vựng** chứ không phân biệt "đúng nghĩa đối lập". Với câu ngắn, số chiều "khác biệt" ít nên cosine bị đẩy cao. Điều này cho thấy cosine similarity ≠ nghĩa tương đương tuyệt đối — nó phản ánh sự gần nhau trong không gian vector, vốn chịu ảnh hưởng của lĩnh vực và độ dài văn bản.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **Chiến lược của tôi:** `RecursiveChunker(chunk_size=400)`. **Embedder:** local multilingual `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`, 384 chiều, chuẩn hóa). Số chunk nạp được: **726**. Agent dùng `demo_llm` (giả lập) nên phần "agent trả lời đúng" đánh giá tay từ context; chấm chính theo **evidence string** trong top-3.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Danh hiệu "Tập thể Tiên tiến" cần bao nhiêu % sinh viên loại Khá? | `quy-che-hust` — khối lượng chuyển đổi tín chỉ tối đa 50% | 0.7895 | ❌ (không chứa "70%"; doc gold `thi-dua` không vào top-3) | [DEMO LLM] — trả nội dung học vụ không đúng số liệu |
| 2 | Điều kiện đạt danh hiệu "Sinh viên Xuất sắc"? | `thi-dua` — phạm vi áp dụng quy định | 0.8321 | ⚠️ Có nhưng không top-1 (chunk chứa "C+" ở **top-2**) | [DEMO LLM] — context đủ ở top-2 |
| 3 | Phúc tra/khiếu nại điểm trong bao lâu? | `quy-che-hust` — Điều 6.4 "7 ngày"/phúc tra | 0.8018 | ✅ Có (top-1 chứa đúng "7 ngày" + "phúc tra") | [DEMO LLM] — trả đúng 7 ngày |
| 4 | Kể tên các danh hiệu khen thưởng SV? | `thi-dua` — Điều 10 "thủ khoa" (+ top-3 "Sinh viên Xuất sắc") | 0.7643 | ✅ Có (top-1 chứa danh hiệu) | [DEMO LLM] — liệt kê được phần danh hiệu |
| 5 | Quy định NCKH/trao đổi học thuật áp dụng cho ai? *(filter `{"audience":"student"}`)* | `quy-che-uet-66` — Điều 28 tổ chức NCKH sinh viên | 0.7029 | ❌ (không chứa "Tài năng"/"ELITECH" — gold ở `quy-che-hust` Điều 2.5) | [DEMO LLM] — lạc sang NCKH sinh viên |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (Q2, Q3, Q4)

**Gợi ý điểm theo evidence:** Q1=0 · Q2=1 · Q3=2 · Q4=2 · Q5=0 → **5/10**

**Phân tích A/B filter (Q5):** không filter và có filter `{"audience":"student"}` cho **top-3 giống hệt nhau** (đều là doc student: `quy-che-uet-66`, `quy-che-hust`; doc teacher `dinh-huong-nghien-cuu-khoa-hoc` không lọt top-3 ở cả 2 lần). → **Filter không làm thay đổi kết quả** → với query/corpus này, filter `audience` chưa thực sự cần thiết (tài liệu dành cho đối tượng khác không cạnh tranh top-3). Đây là tín hiệu để nhóm xem lại thiết kế query filter.

**Failure case 1 (Q1 — đúng chủ đề, sai section):** query hỏi tỉ lệ **70%** của "Tập thể Tiên tiến" (`thi-dua`, Điều 8). Top-3 thực tế: (1) `quy-che-hust` mục chuyển đổi tín chỉ 50%, (2) `quy-che-uet-66` mục rút bớt học phần, (3) `quy-che-uet-66` mục điều kiện tốt nghiệp. Cả 3 **cùng chủ đề học tập/rèn luyện** nhưng **không chunk nào chứa "70%"**; tài liệu gold `thi-dua` (nhỏ, ~7.7k ký tự) bị lấn bởi 2 quy chế lớn (78k/77k). **Nguyên nhân:** cosine đo độ giống chủ đề, không đo mật độ thông tin trả lời; doc nhỏ có ít chunk → ít "phiếu" cạnh tranh top-3. **Đề xuất:** tăng overlap để cụm "70%..." không bị cắt; hoặc dùng chunker theo heading (mỗi Điều = 1 chunk, Điều 8 có cơ hội đứng riêng); hoặc kết hợp keyword (BM25) bù cho semantic.

**Failure case 2 (Q5 — query mơ hồ + filter không hiệu quả):** gold là `quy-che-hust` Điều 2.5 (sinh viên CTĐT Tài năng/ELITECH được tạo điều kiện NCKH), nhưng top-1 lại là `quy-che-uet-66` Điều 28 (tổ chức NCKH sinh viên). **Nguyên nhân:** câu hỏi dùng cụm "nghiên cứu khoa học" chạm rất nhiều đoạn khác nhau trong cả 2 quy chế; filter `audience=student` không loại được gì vì tất cả doc cạnh tranh đều là student. **Đề xuất:** viết lại query nêu rõ đối tượng/điều kiện (vd "sinh viên chương trình Tài năng…"), hoặc chấp nhận chunk NCKH sinh viên là relevant và điều chỉnh gold answer.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Chưa có demo nhóm — sẽ bổ sung sau khi tổng hợp benchmark của các thành viên.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |
