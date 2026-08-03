# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [B2- D305]
**Thành viên:** [
    Lê Văn Đông - 2A202601851
    Đào Đức Mạnh - 2A202601833
    Nguyễn Viết Huy - 2A202601081
    Đàm Lê Minh Quân - 2A202601451
    Trần Văn Dũng - 2A202601859
]
**Ngày:** [3/8/2026]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Học vụ (đăng ký học phần, thi & điểm, quy chế đào tạo đại học) + dịch vụ thư viện (giờ mở, mượn/gia hạn/trả, phạt, mượn thiết bị, phòng học nhóm) — nguồn công khai của VinUniversity (registrar.vinuni.edu.vn, library.vinuni.edu.vn, policy.vinuni.edu.vn).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Library Access & Services Policy | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | 2026-08-03 / POL-LLR-001-V4.0 | 8,444 | doc_id, title, source_url, retrieved_at, document_version, audience=all, department=library, category=library-policy, language=en |
| 2 | Circulation – mượn/gia hạn/trả | https://library.vinuni.edu.vn/borrow-renew-return/ | 2026-08-03 / not-stated | 2,832 | doc_id, title, source_url, retrieved_at, document_version, audience=all, department=library, category=circulation, language=en |
| 3 | Library Borrowing Privilege | https://library.vinuni.edu.vn/borrowing-priviledge/ | 2026-08-03 / not-stated | 2,555 | doc_id, title, source_url, retrieved_at, document_version, audience=all, department=library, category=borrowing-policy, language=en |
| 4 | Library Hours and Access | https://library.vinuni.edu.vn/about-us/hours-and-access/ | 2026-08-03 / not-stated | 1,087 | doc_id, title, source_url, retrieved_at, document_version, audience=all, department=library, category=access-policy, language=en |
| 5 | Library services cho graduate/faculty | https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/ | 2026-08-03 / not-stated | 8,276 | doc_id, title, source_url, retrieved_at, document_version, audience=faculty, department=library, category=borrowing-policy, language=en |
| 6 | Class Schedule & Course Registration | https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/ | 2026-08-03 / not-stated | 3,559 | doc_id, title, source_url, retrieved_at, document_version, audience=student, department=academic-affairs, category=course-registration, language=en |
| 7 | Exams & Grades | https://registrar.vinuni.edu.vn/academics/exams-grades/ | 2026-08-03 / not-stated | 1,613 | doc_id, title, source_url, retrieved_at, document_version, audience=student, department=academic-affairs, category=grading, language=en |
| 8 | Academic Regulations (Undergrad) | https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergraduate-programs/ | 2026-08-03 / VU_HT03 | 71,180 | doc_id, title, source_url, retrieved_at, document_version, audience=student, department=academic-affairs, category=academic-regulations, language=en |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata.
- [x] `data/university-academic-library-services/sources.csv` khớp một-một với 8 file `.md`; đã chạy CHECKPOINT 2: 8/8 file OK, `csv: khop`, `audience` phân bố {all: 4, faculty: 1, student: 3}.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `library-access-policy` | Định danh duy nhất, dùng cho `delete_document()` và lọc theo tài liệu |
| `title` | string | `Library Access and Services Policy` | Hiển thị + truy vết nguồn câu trả lời |
| `source_url` | string | `https://policy.vinuni.edu.vn/...` | Truy vết (provenance) câu trả lời về nguồn gốc |
| `retrieved_at` | date | `2026-08-03` | Kiểm tra độ mới của dữ liệu |
| `document_version` | string | `POL-LLR-001-V4.0` / `not-stated` | Truy vết phiên bản/ngày hiệu lực |
| `audience` | string | `student` / `faculty` / `all` | **Trường lọc chính** cho `search_with_filter()` (yêu cầu K3) |
| `department` | string | `library` / `academic-affairs` | Lọc theo bộ phận phụ trách (query mượn thư viện vs. học vụ) |
| `category` | string | `library-policy` / `course-registration` | Nhóm chủ đề con, tăng độ chính xác khi lọc |
| `language` | string | `en` | Phân biệt ngôn ngữ nếu mở rộng corpus đa ngữ |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
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
>
> **Corpus benchmark cho 5 câu này:** `data/university_services_retrieval`.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Danh hiệu "Tập thể Tiên tiến" yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên? *(số liệu)* | Có **70%** sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên; không có sinh viên xếp loại Yếu trở xuống (không tính sinh viên đã tự ý nghỉ/bỏ học hoặc thuộc diện không tương tác). | `thi-dua-khen-thuong-uet-2023`, Điều 8. |
| 2 | Điều kiện để sinh viên đạt danh hiệu "Sinh viên Xuất sắc" tại Trường Đại học Công nghệ là gì? *(điều kiện)* | Kết quả học tập và rèn luyện trong năm học/toàn khóa đạt loại **Xuất sắc** và **không có học phần nào có điểm dưới C+**; được tặng Giấy khen của Hiệu trưởng cùng tiền thưởng theo quy định. | `thi-dua-khen-thuong-uet-2023`, Điều 4. |
| 3 | Sinh viên Đại học Bách khoa Hà Nội phúc tra hoặc khiếu nại điểm học phần trong thời hạn bao lâu? *(quy trình)* | Được đề nghị phúc tra/khiếu nại điểm trong thời hạn **7 ngày** kể từ khi điểm được cập nhật vào tài khoản học tập. **Ngoại lệ:** không áp dụng với học phần thi theo hình thức vấn đáp hoặc đánh giá trước hội đồng. | `quy-che-dao-tao-dai-hoc-hust`, Điều 6.4. |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường Đại học Công nghệ. *(liệt kê)* | 7 danh hiệu: Thủ khoa ngành học; Sinh viên Xuất sắc; Sinh viên Giỏi; Sinh viên có đóng góp cho công tác tập thể; Sinh viên bảo vệ khóa luận/đồ án tốt nghiệp Xuất sắc; Tập thể Tiên tiến; Tập thể Xuất sắc. | `thi-dua-khen-thuong-uet-2023`, Điều 3–9. |
| 5 | Quy định tạo điều kiện tham gia hoạt động nghiên cứu khoa học, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào? *(ngoại lệ + BẮT BUỘC lọc đối tượng)* | Áp dụng cho **sinh viên thuộc các CTĐT Tài năng** (nhóm ELITECH) của ĐHBK Hà Nội: được tạo điều kiện tham gia hoạt động NCKH, trao đổi học thuật, công nhận tín chỉ đã tích lũy từ cơ sở đào tạo đối tác. Chạy với `metadata_filter={"audience": "student"}` để loại tài liệu `dinh-huong-nghien-cuu-khoa-hoc` có `audience=teacher`. | `quy-che-dao-tao-dai-hoc-hust`, Điều 2.5. |

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
