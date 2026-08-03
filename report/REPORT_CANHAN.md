# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đàm Lê Minh Quân
**Nhóm:** B2
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding gần như cùng hướng trong không gian nhiều chiều — tức hai đoạn văn bản mang ý nghĩa/chủ đề gần nhau, bất kể độ dài hay số từ trùng nhau nhiều hay ít.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên phải đăng ký học phần trước khi bắt đầu học kỳ."
- Câu B: "Trước mỗi học kỳ, sinh viên cần đăng ký các học phần sẽ học."
- Tại sao tương đồng: Diễn đạt khác nhau (đổi trật tự, đổi từ) nhưng cùng một ý nghĩa — cùng nói về việc đăng ký học phần đầu kỳ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thư viện mở cửa từ 7 giờ sáng đến 9 giờ tối."
- Câu B: "Học bổng khuyến khích học tập được xét theo kết quả học kỳ."
- Tại sao khác: Hai chủ đề hoàn toàn khác nhau (giờ mở cửa thư viện vs. chính sách học bổng), không chia sẻ ý nghĩa hay từ vựng liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm đến *hướng* của vector (tức nội dung/ý nghĩa) chứ không quan tâm *độ lớn* (magnitude) — vốn thường bị ảnh hưởng bởi độ dài văn bản. Hai đoạn văn cùng ý nghĩa nhưng độ dài khác nhau vẫn có thể có magnitude khác xa nhau, khiến khoảng cách Euclid đánh giá sai mức độ tương đồng, trong khi cosine vẫn cho điểm cao.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* số_chunk = làm_tròn_lên((10000 − 50) / (500 − 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11)
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> số_chunk = làm_tròn_lên((10000 − 100) / (500 − 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = **25 chunks** — tăng overlap làm bước trượt (step = chunk_size − overlap) nhỏ lại nên cần nhiều chunk hơn để phủ hết tài liệu. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới chunk (câu/ý bị cắt ngang ở chunk này vẫn xuất hiện trọn vẹn ở chunk kế tiếp), đánh đổi bằng nhiều vector hơn và tăng chi phí lưu trữ/tính toán.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=\.)[ \n]|(?<=[!?]) ` để tách câu — lookbehind giữ lại dấu câu (`.`/`!`/`?`) ở cuối câu trước đó, chỉ loại bỏ khoảng trắng/newline ngăn cách, đúng 4 pattern trong docstring (`". "`, `"! "`, `"? "`, `".\n"`). Sau khi tách, lọc câu rỗng và `.strip()` từng câu, rồi gom mỗi `max_sentences_per_chunk` câu thành 1 chunk bằng `" ".join(...)`. Edge case: văn bản rỗng trả về `[]` ngay từ đầu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy thử tách theo từng separator trong danh sách ưu tiên (`\n\n` → `\n` → `. ` → `" "` → `""`): với mỗi separator, gom các phần nhỏ lại thành buffer cho tới khi gần chạm `chunk_size`, phần nào ghép vào vẫn vượt quá `chunk_size` thì đệ quy xuống separator tiếp theo. Base case: `len(text) <= chunk_size` (trả về nguyên văn bản) hoặc hết separator/gặp `""` (cắt cứng theo `chunk_size`).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa qua `_make_record()` thành 1 dict gồm `id`, `doc_id` (lấy từ `metadata["doc_id"]` nếu có, không thì fallback về `doc.id`), `content`, `metadata`, `embedding` — rồi append vào `self._store` (in-memory) hoặc `collection.add()` nếu có ChromaDB. `search()` nhúng câu query, tính **dot product** giữa vector query và từng embedding đã lưu (dùng lại `_dot` từ `chunking.py`), sắp xếp giảm dần theo score và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc **trước**: chỉ giữ lại các record có `metadata` khớp toàn bộ `metadata_filter` (AND theo từng key), rồi mới chạy chung logic similarity search ở trên tập đã lọc — tránh phải tính điểm cho các chunk chắc chắn không liên quan. `delete_document` xóa mọi record có `doc_id` khớp `doc_id` truyền vào (dùng đúng field `doc_id` đã chuẩn hóa ở `_make_record`, nên hoạt động cả khi gọi trực tiếp với `Document` đơn lẻ lẫn khi nạp qua `ingest.py` — nơi mỗi chunk mang `metadata["doc_id"]` trỏ về tài liệu gốc).

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Theo đúng pattern RAG: gọi `self.store.search(question, top_k=top_k)` để lấy các chunk liên quan, nối nội dung (`content`) của chúng bằng `"\n"` thành 1 khối `context`, rồi ghép vào prompt dạng `"Context:\n{context}\n\nQuestion: {question}\nAnswer:"` trước khi gọi `self.llm_fn(prompt)` và trả thẳng kết quả về. `__init__` chỉ lưu `store`/`llm_fn` vào instance để `answer()` dùng lại.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument (3 tests) PASSED

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên phải đăng ký học phần trước khi bắt đầu học kỳ. | Trước mỗi học kỳ, sinh viên cần đăng ký các học phần sẽ học. | cao | 0.8948 | ✅ |
| 2 | Điểm trung bình chung tích lũy được tính theo trọng số tín chỉ. | GPA tích lũy được tính dựa trên số tín chỉ của từng học phần. | cao | 0.5817 | ✅ (đúng hướng, nhưng thấp hơn dự kiến) |
| 3 | Sinh viên vi phạm quy chế thi sẽ bị đình chỉ học. | Sinh viên nghỉ học quá 20% số tiết sẽ không đủ điều kiện dự thi. | thấp | 0.4347 | ✅ |
| 4 | Thư viện mở cửa từ 7 giờ sáng đến 9 giờ tối. | Học bổng khuyến khích học tập được xét theo kết quả học kỳ. | thấp | 0.1691 | ✅ |
| 5 | Sinh viên đạt loại Xuất sắc sẽ được khen thưởng. | Sinh viên bị kỷ luật do gian lận thi cử sẽ bị xử lý nghiêm khắc. | thấp | 0.4323 | ✅ (đúng hướng, nhưng cao hơn dự kiến) |

*(Đo bằng `LocalEmbedder` — `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — vì mock embedder không phản ánh ngữ nghĩa thật.)*

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là Cặp 5: hai câu **trái ngược hoàn toàn về ý nghĩa** (khen thưởng vs. kỷ luật) nhưng vẫn đạt điểm 0.43 — cao hơn cả Cặp 3 (hai câu cùng chiều nhưng khác chủ đề cụ thể). Điều này cho thấy embedding sentence-level không chỉ mã hóa "ý nghĩa đối lập hay không" mà còn bị chi phối mạnh bởi *chủ đề/từ vựng chung* (cùng nói về "sinh viên", cùng khung quy chế kỷ luật/khen thưởng) — mô hình nắm bắt sự tương đồng về **chủ đề** tốt hơn là phân biệt tinh vi về **cực tính ngữ nghĩa** (semantic polarity). Ngược lại, Cặp 2 dù là paraphrase gần như hoàn hảo lại chỉ đạt 0.58 vì hai câu dùng từ vựng khác nhau nhiều (GPA vs. điểm trung bình chung, trọng số vs. số tín chỉ) — mô hình đa ngữ vẫn nhạy với cách diễn đạt/từ vựng bề mặt hơn là chỉ thuần túy nắm ý nghĩa trừu tượng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Chiến lược cá nhân dùng để chạy: `ArticleChunker` (custom, chia theo "Điều N") + `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`), nạp qua `build_knowledge_base()` trên `data/university_services_retrieval/` (489 chunk).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tập thể Tiên tiến cần tối thiểu bao nhiêu % sinh viên loại Khá trở lên? | Điều 8 (thi-dua-khen-thuong-uet-2023): "Có 70% sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên..." | 0.7611 | Có — khớp đúng gold answer ngay top-1 | *(chưa chạy qua `KnowledgeBaseAgent.answer` — không có `OPENAI_API_KEY` trong môi trường; mới đánh giá tầng retrieval)* |
| 2 | Điều kiện đạt "Sinh viên Xuất sắc"? | Điều 9: "Tập thể Xuất sắc..." (top-1); chunk gold — Điều 4 "Sinh viên Xuất sắc" — nằm ở **top-2** (0.7897) | 0.8253 (top-1) | Có, nhưng chunk đúng nhất chưa xếp hạng 1 | *(chưa chạy)* |
| 3 | Thời hạn phúc tra/khiếu nại điểm HUST? | Điều 35 (quy-che-dao-tao-dai-hoc-**uet-66**) — sai tài liệu; chunk gold ("7 ngày...") ở **top-2** (0.7719, đúng doc HUST) | 0.7722 (top-1) | Có ở top-2, top-1 sai doc | *(chưa chạy)* |
| 4 | Liệt kê các danh hiệu thi đua, khen thưởng sinh viên | Điều 10 (thi-dua-khen-thuong-uet-2023) | 0.7857 | Một phần — top-3 đúng chủ đề/doc nhưng mỗi chunk chỉ chứa 1 Điều, không đủ liệt kê hết 7 danh hiệu | *(chưa chạy)* |
| 5 | Quy định NCKH/trao đổi học thuật áp dụng cho đối tượng nào? (cần `metadata_filter={"audience":"student"}`) | Điều học bổng (quy-che-dao-tao-dai-hoc-uet-66) — sai doc; 2 kết quả còn lại đúng doc HUST nhưng sai Điều (nói về NCS/luận án tiến sĩ, không phải Điều 2.5 ELITECH) | 0.7038 (top-1) | Không — chunk gold (Điều 2.5) không xuất hiện trong top-3 | *(chưa chạy)* |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (câu 1, 2, 3 có; câu 4 một phần; câu 5 không)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *(Điền sau buổi demo nhóm — ví dụ: so sánh xem `RecursiveChunker`/`FixedSizeChunker` của các thành viên khác có xử lý tốt hơn Câu 4 và Câu 5 — hai câu mà `ArticleChunker` gặp khó vì câu trả lời trải rộng nhiều Điều hoặc dùng từ vựng khác với đoạn gốc — hay không.)*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
