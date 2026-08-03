# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Trần Văn Dũng]
**Nhóm:** [B2]
**Ngày:** 03/08/2026

**Embedding đã dùng:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` trong `.venv`, vector 384 chiều. Không dùng MockEmbedder trong các bảng similarity và retrieval dưới đây.

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

Cosine similarity đo góc giữa hai embedding, nên tập trung vào hướng ngữ nghĩa thay vì độ lớn vector như Euclidean distance. Điểm gần 1 thường là gần nghĩa, gần 0 ít liên quan. `compute_similarity` trả `0.0` nếu một vector có norm bằng 0.

Ví dụ cao: “Điều kiện Sinh viên Xuất sắc UET là gì?” và “Sinh viên cần học tập và rèn luyện Xuất sắc, không có học phần dưới C+.” Ví dụ thấp: “Thời hạn phúc tra điểm HUST?” và “Danh hiệu thi đua UET gồm những gì?”

Với tài liệu 10,000 ký tự, `chunk_size=500`, `overlap=50`: `ceil((10000-50)/(500-50)) = 23` chunks. Overlap 100 cho 25 chunks; giữ ngữ cảnh ranh giới tốt hơn nhưng tăng số vector.

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

- Sentence chunker dùng `(?<=[.!?])\s+`, tách sau dấu câu để không làm câu cụt.
- Recursive chunker có hai chiều: đệ quy xuống separator nhỏ hơn khi mảng còn dài và gom mảnh kề nhau vào buffer khi còn vừa kích thước.
- Store lưu `id`, `content`, `metadata`, embedding; filter trước khi ranking và xóa theo `doc_id`.
- Agent ghép top-k source vào prompt. Local embedding đã chạy thật; LLM provider chưa được cấu hình nên agent chưa sinh câu trả lời ngôn ngữ tự do.

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Đã xử lý ba lỗi trọng tâm: regex không mất dấu câu, recursive có cơ chế gom mảnh, zero vector trả `0.0`. Comparator trả đúng ba key `fixed_size`, `by_sentences`, `recursive`.

```text
.\.venv\Scripts\python.exe -m pytest tests\ -q
42 passed in 0.05s
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

Corpus có 5 Markdown, 5 dòng manifest, front matter hợp lệ; sau làm sạch marker trang PDF, Recursive 500 tạo 480 chunks.

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Danh hiệu “Tập thể Tiên tiến” yêu cầu bao nhiêu phần trăm sinh viên Khá trở lên? | Tập thể Tiên tiến cần 70% sinh viên đạt học tập và rèn luyện loại Khá trở lên. | cao | 0.5787 | Có |
| 2 | Điều kiện Sinh viên Xuất sắc UET là gì? | Học tập và rèn luyện Xuất sắc, không có học phần dưới C+. | cao | 0.4698 | Có |
| 3 | Thời hạn phúc tra điểm học phần HUST? | Sinh viên có 7 ngày từ khi điểm cập nhật để khiếu nại. | cao | 0.4308 | Có |
| 4 | Danh hiệu thi đua UET gồm những gì? | Thủ khoa, Sinh viên Xuất sắc, Sinh viên Giỏi và các danh hiệu tập thể. | cao | 0.3944 | Có |
| 5 | Hoạt động NCKH áp dụng đối tượng nào? | Sinh viên CTĐT Tài năng (ELITECH) được tạo điều kiện NCKH và trao đổi học thuật. | cao | 0.4095 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Cặp 4 có cùng chủ đề nhưng score thấp nhất (0.3944), vì câu B chỉ liệt kê một phần danh hiệu và dùng ít từ trùng hơn câu A. Điều này cho thấy embedding đa ngữ nắm được ý nghĩa chung nhưng score còn phụ thuộc mức độ cụ thể, cấu trúc câu và các thực thể xuất hiện trong từng câu; không nên đặt một ngưỡng cố định để kết luận đúng/sai.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src`, với `RecursiveChunker(chunk_size=400)`, Sentence Transformers, `top_k=3`. Năm câu hỏi trùng `REPORT_NHOM.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Danh hiệu “Tập thể Tiên tiến” yêu cầu bao nhiêu % sinh viên Khá trở lên? | `thi-dua-khen-thuong-uet-2023`, Điều 8: 70%; không có SV Yếu trở xuống theo ngoại lệ nêu trong quy định. | 0.7635 | Có, top-1 | Gold đối chiếu: 70% và điều kiện không có SV Yếu trở xuống. Agent đã nhận 3 source; LLM chưa cấu hình để sinh câu tự do. |
| 2 | Điều kiện đạt danh hiệu “Sinh viên Xuất sắc” UET? | `thi-dua-khen-thuong-uet-2023`, Điều 4: học tập/rèn luyện Xuất sắc, không có học phần dưới C+. | 0.8333 | Có, top-1 | Gold đối chiếu: đủ hai điều kiện, có Giấy khen và tiền thưởng theo quy định. |
| 3 | HUST phúc tra/khiếu nại điểm trong bao lâu? | `quy-che-dao-tao-dai-hoc-hust`, Điều 6.4: 7 ngày; trừ vấn đáp/hội đồng. | 0.8018 | Có, top-1 | Gold đối chiếu: 7 ngày từ khi cập nhật điểm; ngoại lệ vấn đáp hoặc hội đồng. |
| 4 | Kể tên danh hiệu thi đua, khen thưởng UET. | `thi-dua-khen-thuong-uet-2023`, Điều 3–9: nhóm 7 danh hiệu. | 0.7643 | Có, top-1 | Gold đối chiếu: Thủ khoa, SV Xuất sắc, SV Giỏi, đóng góp tập thể, đồ án xuất sắc, hai danh hiệu tập thể. |
| 5 | Quy định NCKH/trao đổi tín chỉ áp dụng đối tượng nào? | `quy-che-dao-tao-dai-hoc-hust`, Điều 2.5: sinh viên CTĐT Tài năng (ELITECH). | 0.7017 | Có, top-1 | Gold đối chiếu: được tạo điều kiện NCKH, trao đổi học thuật và công nhận tín chỉ đối tác. |

Filter sử dụng: Q1/Q2/Q4 `{"category":"scholarship-policy"}`; Q3 `{"institution":"hust"}`; Q5 bắt buộc `{"audience":"student"}` để loại tài liệu `dinh-huong-nghien-cuu-khoa-hoc` có `audience=teacher`.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Chỉ tăng `chunk_size` không tự động làm retrieval tốt hơn. Recursive split phù hợp với văn bản quy định vì tôn trọng ranh giới điều/mục, còn metadata filter cần được thiết kế theo đối tượng và chủ đề để loại nhiễu trước khi semantic ranking. Tôi cũng học được phải báo cáo cả hit@3, top-1 và số chunks, thay vì chỉ chọn cấu hình có score cao nhất.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |