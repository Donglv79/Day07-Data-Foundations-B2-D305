# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Văn Đông
**Nhóm:** B2-D305
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding có hướng gần nhau, nên mô hình biểu diễn chúng như các nội dung có ý nghĩa hoặc ngữ cảnh tương tự. Giá trị càng gần 1 thì mức tương đồng theo hướng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể đăng ký môn học trên cổng thông tin.
- Câu B: Người học dùng hệ thống trực tuyến để ghi danh học phần.
- Tại sao tương đồng: Cả hai câu đều nói về hành động đăng ký học phần bằng hệ thống trực tuyến.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thư viện mở cửa từ 8 giờ sáng.
- Câu B: Học phí được thanh toán theo từng học kỳ.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau: dịch vụ thư viện và quy trình học phí.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine so sánh hướng của hai vector và ít bị ảnh hưởng bởi độ lớn vector, vì vậy phù hợp với việc so sánh ý nghĩa giữa các embedding. Euclid nhạy với độ lớn tuyệt đối, nên hai vector cùng hướng nhưng khác độ dài có thể bị xem là xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks. Overlap lớn hơn giữ được ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số vector, chi phí lưu trữ và khả năng kết quả bị lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+` để tách sau dấu kết thúc câu, vẫn giữ dấu câu trong nội dung. Sau đó loại bỏ đoạn rỗng và gom tối đa `max_sentences_per_chunk` câu bằng dấu cách. Hàm trả về danh sách rỗng với chuỗi rỗng hoặc chỉ có khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên tách lần lượt theo đoạn trống, xuống dòng, dấu chấm, khoảng trắng và cuối cùng là theo ký tự. Mỗi đoạn vượt `chunk_size` sẽ được đệ quy với separator ưu tiên thấp hơn; các đoạn ngắn được gom lại nếu không vượt giới hạn. Base case là đoạn rỗng, đoạn đã đủ ngắn, hoặc hết separator thì cắt theo kích thước cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành record gồm id duy nhất, content, metadata và embedding. Với memory store, truy vấn được embed bằng cùng hàm rồi xếp hạng giảm dần theo dot product; kết quả có `content`, `metadata` và `score`. Nếu có ChromaDB, store dùng collection ChromaDB và trả về cùng cấu trúc kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record theo tất cả cặp khóa–giá trị metadata trước, rồi chỉ xếp hạng các record còn lại. Khi thêm dữ liệu, `doc_id` gốc luôn được gắn vào metadata; `delete_document` dùng trường này để xóa toàn bộ chunk của một tài liệu và báo lại có xóa được hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent truy xuất top-k chunk, gắn từng chunk với `doc_id`/nguồn và ghép chúng thành phần Context của prompt. Prompt yêu cầu LLM chỉ trả lời dựa trên context và phải nói rõ khi context không đủ; sau đó agent gọi `llm_fn` với prompt đã tạo.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
collected 42 items

tests/test_solution.py ..........................................       [100%]

============================= 42 passed in 0.07s =============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is used to write software. | Python is a programming language. | cao | 0.0502 | Không |
| 2 | Students pay tuition fees online. | The university library lends books. | thấp | -0.1264 | Có |
| 3 | Machine learning learns patterns from data. | Algorithms can learn from training data. | cao | 0.1212 | Có |
| 4 | Dormitory residents must follow quiet hours. | Course registration opens next Monday. | thấp | -0.0471 | Có |
| 5 | Vector databases search similar embeddings. | A vector store retrieves related document chunks. | cao | 0.0309 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 có ý nghĩa rất gần nhau nhưng điểm chỉ 0.0309, trong khi cặp 3 đạt điểm cao nhất. Các điểm trên được tính bằng `_mock_embed`, là embedding xác định phục vụ unit test chứ không biểu diễn ngữ nghĩa thật; vì vậy chúng xác nhận công thức cosine hoạt động nhưng không thể dùng để đánh giá chất lượng truy xuất. Khi đánh giá chiến lược của nhóm, cần dùng local multilingual embedder.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Điều kiện 70% cho danh hiệu Tập thể Tiên tiến là gì? | `thi-dua-khen-thuong-uet-2023`, chunk 12; context thuộc phần danh hiệu/khen thưởng. | 0.7603 | Có trong Top-3 | Chưa cấu hình LLM sinh đáp án; evidence gold có trong context Top-3. |
| 2 | Điều kiện đạt danh hiệu Sinh viên Xuất sắc tại UET là gì? | `thi-dua-khen-thuong-uet-2023`, chunk 14; context về danh hiệu Tập thể Tiên tiến, gold evidence xuất hiện ở chunk 9 trong Top-3. | 0.8217 | Có trong Top-3, không ở Top-1 | Chưa cấu hình LLM sinh đáp án; context Top-3 chứa Điều 4. |
| 3 | Thời hạn phúc tra/khiếu nại điểm học phần tại HUST là bao lâu? | `quy-che-dao-tao-dai-hoc-hust`, chunk 50; có Điều 6.4 về phúc tra/khiếu nại. | 0.7684 | Có, Top-1 | Chưa cấu hình LLM sinh đáp án; context Top-1 có evidence 7 ngày và ngoại lệ. |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng tại UET. | `thi-dua-khen-thuong-uet-2023`, chunk 15; nói về khen thưởng tuyển sinh, không liệt kê đủ 7 danh hiệu. | 0.7816 | Không | Context chưa đủ để trả lời danh sách 7 danh hiệu. |
| 5 | Đối tượng được tạo điều kiện NCKH, trao đổi học thuật và công nhận tín chỉ là ai? | Không filter và filter `audience=student` đều trả `quy-che-dao-tao-dai-hoc-uet-66`, chunk 1; không chứa đáp án ELITECH/HUST. | 0.6664 | Không | Context không đủ; A/B filter chưa cải thiện retrieval. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5. Q1, Q2 và Q3 có evidence gold; Q4 và Q5 không có evidence gold trong Top-3.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Local multilingual embedding cho kết quả tốt hơn rõ rệt so với mock, nhưng score cao không bảo đảm chunk chứa đáp án. Ở Q4, đúng tài liệu được truy xuất nhưng sai section; ở Q5, metadata filter `audience=student` không thay đổi Top-3, cho thấy query hoặc schema metadata cần được điều chỉnh để filter thực sự hữu ích.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 5 / 10 (tự đánh giá theo evidence Top-3) |
| **Tổng phần cá nhân hiện có** | **55 / 60** |
