# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy chế đào tạo đại học + chính sách học vụ (định hướng NCKH, quy chế đào tạo, thi đua khen thưởng) của Đại học Bách khoa Hà Nội (HUST) và Đại học Công nghệ – ĐHQGHN (UET) — nguồn công khai (văn bản PDF hợp lệ, đã chuyển sang Markdown).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Định hướng nghiên cứu khoa học | https://cdnportal.vnu.edu.vn/data/upload/2022/02/30316/Signed_Signed_286.pdf | 2026-08-03 / not-stated | 14,249 | doc_id, title, source_url, retrieved_at, document_version, audience=teacher, institution=uet, department=nckh, category=nckh-policy, language=vi |
| 2 | Quy chế đào tạo đại học HUST (QCDT 2025) | https://ctt.hust.edu.vn/Upload/Nguyễn Quốc Đạt/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf | 2026-08-03 / not-stated | 78,453 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=hust, department=ctsv, category=ctsv-policy, language=vi |
| 3 | Quy chế đào tạo đại học UET (QĐ 66) | https://cdnportal.vnu.edu.vn/data/upload/vanban/2014/12/29/Final_QC-dH-_2014_Ban-hanh-25-12-2014.pdf | 2026-08-03 / not-stated | 76,809 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=uet, department=ctsv, category=ctsv-policy, language=vi |
| 4 | Quy định chuẩn đầu ra ngoại ngữ (từ K70) | https://ctt.hust.edu.vn/Upload/Nguyễn Quốc Đạt/files/DTDH_QDQC/Hoctap/06_%20Quy%20định%20ngoại%20ngữ%20từ%20K70_chính%20quy_final.pdf | 2026-08-03 / not-stated | 29,358 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=hust, department=ctsv, category=ctsv-policy, language=vi |
| 5 | Quy định khen thưởng UET 2023 | https://handbook.uet.vnu.edu.vn/Quy%20dinh%20khen%20thuong%20tai%20Truong%20DHCN%202023.pdf | 2026-08-03 / not-stated | 7,764 | doc_id, title, source_url, retrieved_at, document_version, audience=student, institution=uet, department=ctsv, category=scholarship-policy, language=vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata.
- [x] `data/university_services_retrieval/sources.csv` khớp một-một với 5 file `.md`; đã chạy CHECKPOINT 2: 5/5 file OK, `csv: khop`, `audience` phân bố {student: 4, teacher: 1}.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `quy-che-dao-tao-dai-hoc-uet-66` | Định danh duy nhất, dùng cho `delete_document()` và lọc theo tài liệu |
| `title` | string | `QuyCheDaoTaoDaiHocUET66` | Hiển thị + truy vết nguồn câu trả lời |
| `source_url` | string | `https://uet.vnu.edu.vn/...` | Truy vết (provenance) câu trả lời về nguồn gốc |
| `retrieved_at` | date | `2026-08-03` | Kiểm tra độ mới của dữ liệu |
| `document_version` | string | `not-stated` | Truy vết phiên bản/ngày hiệu lực |
| `audience` | string | `student` / `teacher` | **Trường lọc chính** cho `search_with_filter()` (yêu cầu K3) |
| `institution` | string | `hust` / `uet` | Phân biệt tài liệu giữa 2 trường, lọc theo cơ sở đào tạo |
| `department` | string | `ctsv` / `nckh` | Lọc theo phòng ban/đơn vị phụ trách |
| `category` | string | `ctsv-policy` / `nckh-policy` / `scholarship-policy` | Nhóm chủ đề con, tăng độ chính xác khi lọc |
| `language` | string | `vi` | Ngôn ngữ corpus (tiếng Việt) |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu (đã bỏ YAML front matter, `chunk_size=500`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| quy-che-dao-tao-dai-hoc-hust (78,453 ký tự) | FixedSizeChunker (`fixed_size`) | 175 | 498.0 | Chunk dài đều nhưng có thể cắt giữa ý/mục |
| quy-che-dao-tao-dai-hoc-hust | SentenceChunker (`by_sentences`) | 244 | 319.4 | Mạch lạc theo câu nhưng số chunk cao, vỡ cấu trúc điều khoản |
| quy-che-dao-tao-dai-hoc-hust | RecursiveChunker (`recursive`) | 214 | 364.3 | Cân bằng: ưu tiên theo đoạn/mục, câu là dự phòng |
| quy-che-dao-tao-dai-hoc-uet-66 (76,809 ký tự) | FixedSizeChunker (`fixed_size`) | 171 | 498.9 | Như trên |
| quy-che-dao-tao-dai-hoc-uet-66 | SentenceChunker (`by_sentences`) | 205 | 372.4 | Như trên |
| quy-che-dao-tao-dai-hoc-uet-66 | RecursiveChunker (`recursive`) | 231 | 330.1 | Như trên |
| thi-dua-khen-thuong-uet-2023 (7,764 ký tự) | FixedSizeChunker (`fixed_size`) | 18 | 478.6 | Như trên |
| thi-dua-khen-thuong-uet-2023 | SentenceChunker (`by_sentences`) | 10 | 773.3 | Chunk rất dài do mỗi điều là 1 câu dài → tràn ngưỡng |
| thi-dua-khen-thuong-uet-2023 | RecursiveChunker (`recursive`) | 23 | 335.4 | Như trên |

> Nhận xét baseline: văn bản quy định được biên soạn theo điều/mục (mỗi điều là một đơn vị ngữ nghĩa). `SentenceChunker` với `max_sentences=3` bó các điều dài thành chunk quá lớn (thi-dua avg 773 ký tự) vì mỗi điều thường là 1–2 câu rất dài; `RecursiveChunker` giữ ranh giới tự nhiên tốt hơn.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** RecursiveChunker, `chunk_size=400` (baseline: `500`)
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(chunk_size=400)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Danh hiệu "Tập thể Tiên tiến" yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên? *(số liệu)* | Có **70%** sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên; không có sinh viên xếp loại Yếu trở xuống (không tính sinh viên đã tự ý nghỉ/bỏ học hoặc thuộc diện không tương tác). | `thi-dua-khen-thuong-uet-2023`, Điều 8 |
| 2 | Điều kiện để sinh viên đạt danh hiệu "Sinh viên Xuất sắc" tại Trường Đại học Công nghệ là gì? *(điều kiện)* | Kết quả học tập và rèn luyện trong năm học/toàn khóa đạt loại **Xuất sắc** và **không có học phần nào có điểm dưới C+**; được tặng Giấy khen của Hiệu trưởng + tiền thưởng theo quy định. | `thi-dua-khen-thuong-uet-2023`, Điều 4 |
| 3 | Sinh viên Đại học Bách khoa Hà Nội phúc tra hoặc khiếu nại điểm học phần trong thời hạn bao lâu? *(quy trình)* | Được đề nghị phúc tra/khiếu nại điểm trong thời hạn **7 ngày** kể từ khi điểm được cập nhật vào tài khoản học tập. **Ngoại lệ:** không áp dụng với học phần thi theo hình thức vấn đáp hoặc đánh giá trước hội đồng. | `quy-che-dao-tao-dai-hoc-hust`, Điều 6.4 |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường Đại học Công nghệ. *(liệt kê)* | 7 danh hiệu: Thủ khoa ngành học; Sinh viên Xuất sắc; Sinh viên Giỏi; Sinh viên có đóng góp cho công tác tập thể; Sinh viên bảo vệ khóa luận/đồ án tốt nghiệp Xuất sắc; Tập thể Tiên tiến; Tập thể Xuất sắc. | `thi-dua-khen-thuong-uet-2023`, Điều 3–9 |
| 5 | Quy định tạo điều kiện tham gia hoạt động nghiên cứu khoa học, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào? *(ngoại lệ + BẮT BUỘC lọc đối tượng)* | Áp dụng cho **sinh viên thuộc các CTĐT Tài năng** (nhóm ELITECH) của ĐHBK Hà Nội: được tạo điều kiện tham gia hoạt động NCKH, trao đổi học thuật, công nhận tín chỉ đã tích lũy từ cơ sở đào tạo đối tác. Cần `metadata_filter={"audience": "student"}` để loại doc `dinh-huong-nghien-cuu-khoa-hoc` (audience=teacher) vốn chứa nhiều từ khóa "nghiên cứu khoa học". | `quy-che-dao-tao-dai-hoc-hust`, Điều 2.5 |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
