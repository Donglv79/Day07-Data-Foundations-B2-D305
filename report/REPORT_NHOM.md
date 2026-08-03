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

> Các kết quả dưới đây được tổng hợp từ 5 báo cáo cá nhân thật trong thư mục `report/`. Tất cả dùng LocalEmbedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, nhưng cách chunk, số chunks và chi tiết filter khác nhau; vì vậy so sánh tập trung vào evidence trong top-3 thay vì chỉ so score tuyệt đối.

### Phân tích đường cơ sở (Baseline Analysis)

`ChunkingStrategyComparator(chunk_size=500)` cho thấy quy chế HUST/UET có cấu trúc điều–mục rõ ràng: Fixed Size tạo chunk dài đều (khoảng 497 ký tự), Sentence tạo nhiều chunk hơn và đôi khi một điều dài thành chunk lớn, Recursive ưu tiên ngắt đoạn/dòng nên giữ cấu trúc chính sách tốt hơn. Với văn bản thi đua UET, `SentenceChunker` chỉ tạo 10 chunks trung bình 766.3 ký tự, trong khi Recursive tạo 21 chunks trung bình 359.9 ký tự, phù hợp hơn với các điều khoản ngắn.

### Chiến lược của từng thành viên

**Trần Văn Dũng — `RecursiveChunker(chunk_size=400)`**

- 601 chunks; tách theo đoạn/dòng/câu rồi mới cắt cứng, gom mảnh liền kề để giữ điều khoản.
- Evidence gold ở top-3: **5/5**; gold ở top-1: **5/5**.
- Điểm mạnh: tốt cho câu số liệu, điều kiện, quy trình, liệt kê và đối tượng áp dụng. Điểm yếu: số vector lớn nhất.

**Nguyễn Viết Huy — `RecursiveChunker(chunk_size=400)`**

- 726 chunks trong run cá nhân; dùng LocalEmbedder 384 chiều.
- Evidence gold ở top-3: **3/5** (Q2, Q3, Q4); Q1 và Q5 thất bại.
- Điểm mạnh: Q3 lấy đúng Điều 6.4 ngay top-1. Điểm yếu: truy vấn số liệu 70% và truy vấn ELITECH bị các quy chế lớn lấn át.

**Đào Đức Mạnh — `ArticleChunker(chunk_size=900, overlap=100)` custom**

- 379 chunks; tách theo heading `Điều N`, giữ nguyên điều ngắn và gắn lại tiêu đề Điều cho sub-chunk dài.
- Evidence gold ở top-3: **4/5** (Q1–Q4); Q5 thất bại.
- Điểm mạnh: câu hỏi quy định theo từng Điều giữ được context tốt. Điểm yếu: Q4 trải qua Điều 3–9 nên một chunk không đủ toàn bộ danh sách; Q5 bị nhiễu từ khóa NCKH.

**Đàm Lê Minh Quân — `ArticleChunker` custom, chia theo `Điều N`**

- 489 chunks; mỗi Điều là một đơn vị ngữ nghĩa.
- Evidence gold ở top-3: **3/5** (Q1–Q3); Q4 chỉ một phần, Q5 không có gold.
- Điểm mạnh: Q1 lấy đúng Điều 8 ngay top-1. Điểm yếu: câu liệt kê trải qua nhiều Điều và query nhiều từ khóa NCKH không đưa đúng Điều 2.5 vào top-3.

**Lê Văn Đông — cấu hình chunking không ghi rõ trong báo cáo cá nhân**

- Evidence gold ở top-3: **3/5** (Q1–Q3); Q4 và Q5 không có evidence gold.
- Điểm mạnh: Q3 có Điều 6.4/7 ngày ở top-1. Điểm yếu: đúng tài liệu nhưng sai section ở Q2/Q4; filter `audience=student` không cải thiện Q5.
- Hạn chế báo cáo: cần bổ sung tên chunker, tham số và số chunks để so sánh trực tiếp công bằng.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược | Số chunks | Evidence gold trong top-3 | Mạnh nhất | Failure chính |
|---|---|---:|---:|---|---|
| Trần Văn Dũng | Recursive 400 | 601 | 5/5 | Đủ cả 5 dạng query | Chi phí vector cao |
| Nguyễn Viết Huy | Recursive 400 | 726 | 3/5 | Q3 đúng top-1 | Q1, Q5 |
| Đào Đức Mạnh | Article 900/o100 | 379 | 4/5 | Q1–Q4 | Q5 |
| Đàm Lê Minh Quân | Article theo Điều | 489 | 3/5 | Q1 đúng top-1 | Q4 một phần, Q5 |
| Lê Văn Đông | Chưa ghi rõ | Chưa ghi | 3/5 | Q3 đúng top-1 | Q4, Q5 |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> `RecursiveChunker(chunk_size=400)` của Dũng tốt nhất trên benchmark hiện có: gold xuất hiện top-1/top-3 ở cả 5 câu. Tuy nhiên, Huy cũng dùng Recursive 400 nhưng chỉ 3/5, cho thấy kết quả còn phụ thuộc pipeline chi tiết, cách làm sạch và cách đánh giá/filter; nhóm không nên suy luận rằng chỉ cần chọn cùng tên chunker là sẽ lặp lại kết quả. ArticleChunker là hướng đáng giá cho corpus quy định, nhưng cần gộp hoặc mở rộng context cho câu trả lời trải trên nhiều Điều.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| 1 | Danh hiệu “Tập thể Tiên tiến” yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên? | **70%** sinh viên đạt loại Khá trở lên; không có sinh viên xếp loại Yếu trở xuống, trừ các ngoại lệ trong quy định. | `thi-dua-khen-thuong-uet-2023`, Điều 8 |
| 2 | Điều kiện để sinh viên đạt danh hiệu “Sinh viên Xuất sắc” tại UET là gì? | Học tập và rèn luyện **Xuất sắc**, không có học phần dưới **C+**. | `thi-dua-khen-thuong-uet-2023`, Điều 4 |
| 3 | Sinh viên HUST phúc tra/khiếu nại điểm học phần trong thời hạn bao lâu? | **7 ngày** từ khi điểm cập nhật; trừ thi vấn đáp hoặc đánh giá trước hội đồng. | `quy-che-dao-tao-dai-hoc-hust`, Điều 6.4 |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên UET. | 7 danh hiệu từ Thủ khoa ngành đến Tập thể Xuất sắc. | `thi-dua-khen-thuong-uet-2023`, Điều 3–9 |
| 5 | Quy định NCKH, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào? | Sinh viên CTĐT Tài năng (**ELITECH**) HUST. | `quy-che-dao-tao-dai-hoc-hust`, Điều 2.5 |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Query | Số thành viên có evidence gold top-3 | Chiến lược tốt nhất thực tế | Nhận xét |
|---|---|---:|---|---|
| 1 | Điều kiện 70% Tập thể Tiên tiến | 4/5 | Recursive 400 (Dũng), Article 900 (Mạnh), Article theo Điều (Quân) | Huy bị nhiễu bởi số 50% ở quy chế HUST. |
| 2 | Điều kiện Sinh viên Xuất sắc | 5/5 | Recursive 400 (Dũng) | Một số run lấy đúng tài liệu nhưng gold ở top-2, không top-1. |
| 3 | Thời hạn phúc tra/khiếu nại điểm | 5/5 | Recursive 400 (Dũng/Huy) | Câu có cụm “7 ngày/phúc tra” rõ nên truy xuất ổn định nhất. |
| 4 | Liệt kê 7 danh hiệu UET | 3/5 đầy đủ, 1/5 một phần | Recursive 400 (Dũng) | Câu trả lời trải qua Điều 3–9; chunk theo một Điều có thể thiếu danh sách đầy đủ. |
| 5 | Đối tượng ELITECH | 1/5 | Recursive 400 (Dũng) | Failure case chính: `audience=student` loại doc teacher nhưng vẫn còn nhiều doc student chứa NCKH. |

**Kết quả nhóm:** tổng **18/25** lượt có evidence gold trong top-3 (**72%**). Dũng là run tốt nhất 5/5; Mạnh 4/5; Đông, Huy và Quân mỗi người 3/5.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Q1 hưởng lợi từ `category=scholarship-policy`, vì không filter có thể ưu tiên Quy chế UET 66 thay vì tài liệu khen thưởng. Q5 bắt buộc dùng `audience=student` để loại tài liệu NCKH dành cho giảng viên, nhưng filter này không đủ để lấy đúng Điều 2.5: nhiều tài liệu còn lại cũng có `audience=student` và chứa từ “nghiên cứu khoa học”. Nhóm đề xuất kết hợp thêm `institution=hust`, metadata CTĐT hoặc reranking theo các cụm “ELITECH/CTĐT Tài năng”.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Cùng local multilingual embedding nhưng chunking/pipeline khác nhau tạo kết quả từ 3/5 đến 5/5; không thể chỉ nhìn score cosine cao.
- Câu Q5 là failure case có giá trị: filter theo audience đúng về phạm vi nhưng không đủ phân biệt điều khoản ELITECH với các điều NCKH khác.
- ArticleChunker giữ điều khoản hoàn chỉnh tốt, nhưng truy vấn liệt kê trải qua nhiều Điều cần ghép nhiều chunks hoặc dùng parent context.

**Bài học rút ra khi so sánh trong nhóm:**

> Recursive 400 cho kết quả tốt nhất trong điều kiện chạy của Dũng, còn ArticleChunker của Mạnh cho 4/5 với ít vector hơn (379 so với 601). Chênh lệch giữa hai run Recursive 400 cho thấy nhóm phải chuẩn hóa chính xác corpus snapshot, filter, top_k và tiêu chí evidence trước khi kết luận một chiến lược tốt hơn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ bổ sung `effective_date`, `regulation_number`, `program_type` (ví dụ ELITECH) và metadata cấp Điều; lưu một benchmark manifest chung để mọi người dùng cùng query/filter/gold. Với Q4, sẽ ghép chunks liền kề hoặc parent-document retrieval; với Q5, thêm reranker/keyword boost cho “ELITECH” và “CTĐT Tài năng”.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **38 / 40** |