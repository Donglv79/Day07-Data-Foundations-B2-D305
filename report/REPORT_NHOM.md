# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [B2]
**Thành viên:** [Lê Văn Đông - 2A202601851 Đào Đức Mạnh - 2A202601833 Nguyễn Viết Huy - 2A202601081 Đàm Lê Minh Quân - 2A202601451 Trần Văn Dũng - 2A202601859]
**Ngày:** [3/8/2026]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy chế đào tạo đại học và chính sách học vụ (định hướng NCKH, quy chế đào tạo, thi đua–khen thưởng) của Đại học Bách khoa Hà Nội (HUST) và Đại học Công nghệ – ĐHQGHN (UET); tất cả là PDF công khai đã chuyển sang Markdown và dọn marker trang.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Định hướng nghiên cứu khoa học | https://cdnportal.vnu.edu.vn/data/upload/2022/02/30316/Signed_Signed_286.pdf | 2026-08-03 / not-stated | 14,001 | doc_id, title, source_url, retrieved_at, document_version, audience=teacher, institution=uet, department=nckh, category=nckh-policy, language=vi |
| 2 | Quy chế đào tạo đại học HUST (QCDT 2025) | https://ctt.hust.edu.vn/Upload/Nguyễn%20Quốc%20Đạt/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf | 2026-08-03 / not-stated | 77,788 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=hust, department=ctsv, category=ctsv-policy, language=vi |
| 3 | Quy chế đào tạo đại học UET (QĐ 66) | https://cdnportal.vnu.edu.vn/data/upload/vanban/2014/12/29/Final_QC-dH-_2014_Ban-hanh-25-12-2014.pdf | 2026-08-03 / not-stated | 75,930 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=uet, department=ctsv, category=ctsv-policy, language=vi |
| 4 | Quy định chuẩn đầu ra ngoại ngữ (từ K70) | https://ctt.hust.edu.vn/Upload/Nguyễn%20Quốc%20Đạt/files/DTDH_QDQC/Hoctap/06_%20Quy%20định%20ngoại%20ngữ%20từ%20K70_chính%20quy_final.pdf | 2026-08-03 / not-stated | 28,756 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=hust, department=ctsv, category=ctsv-policy, language=vi |
| 5 | Quy định khen thưởng UET 2023 | https://handbook.uet.vnu.edu.vn/Quy%20dinh%20khen%20thuong%20tai%20Truong%20DHCN%202023.pdf | 2026-08-03 / not-stated | 7,693 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=uet, department=ctsv, category=scholarship-policy, language=vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu chỉ chứa nguồn công khai/được phép dùng, không có dữ liệu cá nhân, thông tin đăng nhập hay tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata.
- [x] `data/university_services_retrieval/sources.csv` khớp một-một với 5 file `.md`; checkpoint nạp dữ liệu: 5/5 file hợp lệ, `audience={student: 4, teacher: 1}`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `quy-che-dao-tao-dai-hoc-uet-66` | Định danh duy nhất, truy vết gold document và xóa tài liệu. |
| `title` | string | `QuyCheDaoTaoDaiHocUET66` | Hiển thị và truy vết nguồn câu trả lời. |
| `source_url` | string | `https://uet.vnu.edu.vn/...` | Cung cấp provenance tới PDF gốc. |
| `retrieved_at` | date | `2026-08-03` | Kiểm tra độ mới dữ liệu. |
| `document_version` | string | `not-stated` | Ghi nhận tình trạng phiên bản/ngày hiệu lực. |
| `audience` | string | `student` / `teacher` | Trường lọc bắt buộc ở Q5. |
| `institution` | string | `hust` / `uet` | Loại quy định thuộc trường khác, dùng ở Q3. |
| `department` | string | `ctsv` / `nckh` | Lọc theo đơn vị phụ trách. |
| `category` | string | `ctsv-policy` / `scholarship-policy` | Khoanh vùng chính sách khen thưởng ở Q1, Q2, Q4. |
| `language` | string | `vi` | Ghi rõ ngôn ngữ corpus để chọn multilingual model. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây. Tất cả run dưới đây dùng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` trong `.venv` (384 chiều), không dùng MockEmbedder.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu, đã bỏ YAML front matter, `chunk_size=500`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| quy-che-dao-tao-dai-hoc-hust | FixedSizeChunker | 163 | 497.1 | Đều kích thước nhưng có thể cắt giữa ý/mục. |
| quy-che-dao-tao-dai-hoc-hust | SentenceChunker | 244 | 316.7 | Mạch lạc theo câu nhưng số chunk cao. |
| quy-che-dao-tao-dai-hoc-hust | RecursiveChunker | 169 | 452.3 | Cân bằng, ưu tiên đoạn/dòng trước khi cắt nhỏ. |
| quy-che-dao-tao-dai-hoc-uet-66 | FixedSizeChunker | 159 | 497.4 | Có thể cắt giữa điều khoản. |
| quy-che-dao-tao-dai-hoc-uet-66 | SentenceChunker | 205 | 368.2 | Giữ câu nhưng nhiều chunks hơn. |
| quy-che-dao-tao-dai-hoc-uet-66 | RecursiveChunker | 182 | 409.5 | Giữ ranh giới tự nhiên tốt hơn. |
| thi-dua-khen-thuong-uet-2023 | FixedSizeChunker | 16 | 499.6 | Một số điều có thể bị cắt giữa chừng. |
| thi-dua-khen-thuong-uet-2023 | SentenceChunker | 10 | 766.3 | Điều dài làm chunk quá lớn. |
| thi-dua-khen-thuong-uet-2023 | RecursiveChunker | 21 | 359.9 | Phù hợp hơn với cấu trúc điều/mục. |

> Nhận xét baseline: văn bản quy định được biên soạn theo điều/mục. `SentenceChunker(max_sentences=3)` có thể tạo chunk lớn khi một điều chỉ gồm 1–2 câu dài; RecursiveChunker giữ ranh giới tự nhiên tốt hơn nhờ separator theo đoạn/dòng và cơ chế gom mảnh kề nhau.

### Chiến lược của từng thành viên

**Thành viên 1 — [Trần Văn Dũng]**

- **Loại chiến lược:** RecursiveChunker, `chunk_size=400`.
- **Mô tả & lý do chọn:** Điều khoản thường chứa điều kiện, ngoại lệ và số liệu trong cùng đoạn. Ngưỡng 400 giúp giữ điều khoản gọn để truy xuất chính xác, đồng thời recursive split tránh cắt giữa tiêu đề/đoạn như fixed-size.
- **Code snippet:**

```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(chunk_size=400)
```

**Thành viên 2 — [Tên]**

- **Loại chiến lược:** FixedSizeChunker, `chunk_size=500`, `overlap=50`.
- **Mô tả & lý do chọn:** Đây là baseline ổn định, overlap giữ ngữ cảnh tại ranh giới và dễ so sánh với các chiến lược còn lại.

```python
from src.chunking import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

**Thành viên 3 — [Tên]**

- **Loại chiến lược:** SentenceChunker, `max_sentences_per_chunk=3`.
- **Mô tả & lý do chọn:** Mỗi chunk kết thúc ở ranh giới câu nên dễ đọc và dễ kiểm chứng evidence; đây là đối chứng cho giả thuyết “giữ câu” tốt hơn cắt theo ký tự.

```python
from src.chunking import SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 4 — [Tên]**

- **Loại chiến lược:** RecursiveChunker, `chunk_size=500`.
- **Mô tả & lý do chọn:** Tăng ngưỡng so với Thành viên 1 để kiểm tra đánh đổi giữa bối cảnh rộng hơn và số vector ít hơn.

```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(chunk_size=500)
```

**Thành viên 5 — [Tên]**

- **Loại chiến lược:** FixedSizeChunker, `chunk_size=700`, `overlap=100`.
- **Mô tả & lý do chọn:** Chunk lớn kết hợp overlap lớn nhằm giữ trọn các điều khoản dài, kiểm tra hướng tối ưu số vector.

```python
from src.chunking import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=700, overlap=100)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| 1 | Recursive 400 | 10/10 — top-1/top-3 gold: 5/5 | Chính xác nhất trong benchmark; giữ điều khoản ngắn. | 601 chunks, tốn nhiều vector nhất. |
| 2 | Fixed 500, overlap 50 | 10/10 — top-1: 4/5, top-3: 5/5 | Baseline đơn giản, ổn định. | Có thể cắt giữa ý. |
| 3 | Sentence 3 | 10/10 — top-1: 4/5, top-3: 5/5 | Dễ đọc, câu hoàn chỉnh. | 538 chunks; điều dài gây chunk lớn. |
| 4 | Recursive 500 | 10/10 — top-1: 4/5, top-3: 5/5 | Cân bằng ngữ cảnh/số chunk. | Q5 không đưa gold lên top-1. |
| 5 | Fixed 700, overlap 100 | 10/10 — top-1: 4/5, top-3: 5/5 | Ít chunks nhất (342), vẫn đạt hit@3. | Bối cảnh rộng hơn mức cần thiết. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Recursive 400 tốt nhất trên benchmark vì đưa tài liệu gold lên top-1 ở cả 5 câu, trong đó có câu số liệu, điều kiện, quy trình, liệt kê và ngoại lệ. Đổi lại nó tạo 601 chunks, nên với corpus lớn hơn cần kiểm tra thêm tốc độ/chi phí trước khi chọn làm cấu hình mặc định.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; Q5 bắt buộc lọc metadata theo đối tượng. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Danh hiệu “Tập thể Tiên tiến” yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên? *(số liệu)* | Có **70%** sinh viên đạt loại Khá trở lên; không có sinh viên xếp loại Yếu trở xuống (không tính tự ý nghỉ/bỏ học hoặc không tương tác). | `thi-dua-khen-thuong-uet-2023`, Điều 8 |
| 2 | Điều kiện để sinh viên đạt danh hiệu “Sinh viên Xuất sắc” tại Trường Đại học Công nghệ là gì? *(điều kiện)* | Học tập và rèn luyện **Xuất sắc**, không có học phần dưới **C+**; được tặng Giấy khen Hiệu trưởng và tiền thưởng theo quy định. | `thi-dua-khen-thuong-uet-2023`, Điều 4 |
| 3 | Sinh viên ĐHBK Hà Nội phúc tra hoặc khiếu nại điểm học phần trong thời hạn bao lâu? *(quy trình)* | **7 ngày** từ khi điểm cập nhật vào tài khoản. Ngoại lệ: không áp dụng với thi vấn đáp hoặc đánh giá trước hội đồng. | `quy-che-dao-tao-dai-hoc-hust`, Điều 6.4 |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường Đại học Công nghệ. *(liệt kê)* | 7 danh hiệu: Thủ khoa ngành; Sinh viên Xuất sắc; Sinh viên Giỏi; có đóng góp công tác tập thể; bảo vệ khóa luận/đồ án Xuất sắc; Tập thể Tiên tiến; Tập thể Xuất sắc. | `thi-dua-khen-thuong-uet-2023`, Điều 3–9 |
| 5 | Quy định tạo điều kiện tham gia NCKH, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào? *(ngoại lệ + bắt buộc lọc đối tượng)* | **Sinh viên CTĐT Tài năng (ELITECH) của ĐHBK Hà Nội**; được tạo điều kiện NCKH, trao đổi học thuật và công nhận tín chỉ từ cơ sở đối tác. | `quy-che-dao-tao-dai-hoc-hust`, Điều 2.5 |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm theo `docs/SCORING.md`: 2 điểm/câu khi top-3 có evidence liên quan và gold answer được đối chiếu đúng với chunk.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Điều kiện 70% Tập thể Tiên tiến | Recursive 400 | Có, top-1 | Score 0.7635; lọc `category=scholarship-policy`. |
| 2 | Điều kiện Sinh viên Xuất sắc | Recursive 400 | Có, top-1 | Score 0.8333; lọc `category=scholarship-policy`. |
| 3 | Thời hạn phúc tra/khiếu nại điểm | Recursive 400 | Có, top-1 | Score 0.8018; lọc `institution=hust`. |
| 4 | Danh sách danh hiệu UET | Recursive 400 | Có, top-1 | Score 0.7643; lọc `category=scholarship-policy`. |
| 5 | Đối tượng NCKH/trao đổi tín chỉ | Recursive 400 | Có, top-1 | Score 0.7017; bắt buộc lọc `audience=student`. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có. Q1 không filter có thể đưa Quy chế UET 66 lên kết quả đầu; `category=scholarship-policy` giới hạn đúng văn bản khen thưởng. Q5 dùng `audience=student` để loại tài liệu định hướng NCKH có đối tượng `teacher`; đây là lọc bắt buộc vì từ khóa “nghiên cứu khoa học” xuất hiện ở cả hai nguồn. Filter thu hẹp ứng viên nhưng vẫn cần embedding để xếp hạng các tài liệu còn lại.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Sentence Transformers đa ngữ trả vector 384 chiều và cho kết quả hợp lý hơn mock; Recursive 400 đạt top-1/top-3 5/5 trên benchmark.
- Metadata filter không thay thế semantic search, nhưng ngăn tài liệu sai đối tượng/sai chủ đề lấn át kết quả đúng.
- Kích thước chunk là đánh đổi: Recursive 400 chính xác nhất ở benchmark nhưng có 601 chunks, trong khi Fixed 700 chỉ có 342 chunks.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng corpus và query, năm chiến lược đều đạt gold trong top-3 khi dùng embedding đa ngữ thật, nhưng thứ hạng top-1 khác nhau. Văn bản quy định ưu tiên ranh giới điều/mục, do đó recursive split phù hợp hơn việc cắt ký tự thuần túy khi cần câu trả lời có điều kiện và ngoại lệ.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ bổ sung metadata `effective_date`/`regulation_number` thay cho `document_version=not-stated`, và thêm query ngoài benchmark để tránh chọn cấu hình bị overfit. Nếu triển khai RAG hoàn chỉnh, sẽ cấu hình LLM provider để agent sinh câu trả lời kèm `doc_id`, Điều/khoản trích dẫn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |