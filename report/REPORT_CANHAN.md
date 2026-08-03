# Báo Cáo Cá Nhân - Lab 7: Embedding & Vector Store

**Họ tên:** Đào Đức Mạnh
**Nhóm:** B2
**Ngày:** 03/08/2026

> Nộp 1 bản / sinh viên. Phần nhóm nộp chung trong `REPORT_NHOM.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) - Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity)

**Độ tương tự cosine cao nghĩa là gì?**
Cosine similarity cao nghĩa là hai vector embedding có hướng gần nhau, nên hai đoạn text có xu hướng gần nhau về ngữ nghĩa hoặc mục đích hỏi/đáp. Nó không yêu cầu hai câu dùng đúng cùng từ, miễn là mô hình embedding biểu diễn chúng gần nhau trong không gian vector.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần đăng ký học phần trước hạn của học kỳ.
- Câu B: Người học phải hoàn tất chọn môn trong thời gian đăng ký quy định.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng nói về nghĩa vụ đăng ký môn đúng thời hạn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên cần đăng ký học phần trước hạn của học kỳ.
- Câu B: Thư viện mở cửa cuối tuần theo lịch phục vụ riêng.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau: đăng ký học phần và giờ phục vụ thư viện.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
Cosine tập trung vào hướng của vector, phù hợp hơn để so sánh ý nghĩa của text embedding. Khoảng cách Euclid dễ bị ảnh hưởng bởi độ lớn vector, trong khi retrieval thường cần biết hai đoạn văn gần nhau về ngữ nghĩa hơn là vector dài hay ngắn.

### Bài toán tính toán Chunking

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Phép tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`
Đáp án: **23 chunks**.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào?**
Khi overlap tăng lên 100, bước nhảy còn 400 nên số chunk tăng lên: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới chunk, nhưng làm tăng số record cần embed và tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) - Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`**
Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, nhờ đó dấu câu vẫn nằm ở câu phía trước. Text rỗng trả về `[]`; từng câu được `strip()` và bỏ phần rỗng trước khi gộp tối đa `max_sentences_per_chunk` câu vào một chunk.

**`RecursiveChunker.chunk` / `_split`**
Tôi tách theo separator ưu tiên từ tự nhiên đến nhỏ hơn: đoạn, dòng, câu, từ, rồi ký tự. Base case là text đã ngắn hơn `chunk_size`, hoặc hết separator thì cắt cố định; nếu một phần sau khi tách vẫn quá dài, phần đó được xử lý tiếp bằng separator ưu tiên thấp hơn.

**Chiến lược benchmark riêng: `ArticleChunker`**
Tôi viết thêm `ArticleChunker` để tách tài liệu quy định tiếng Việt theo heading `Điều <số>.` hoặc `Điều <số>:`. Lý do chọn chiến lược này là corpus của nhóm chủ yếu là quy chế/quy định, trong đó mỗi Điều thường là một đơn vị ngữ nghĩa hoàn chỉnh. Cấu hình benchmark cuối cùng là `ArticleChunker(chunk_size=900, overlap=100)`: các Điều ngắn hơn 900 ký tự được giữ nguyên; Điều dài hơn ngưỡng sẽ được cắt nhỏ và gắn lại tiêu đề Điều vào từng sub-chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`**
Tôi dùng in-memory store: mỗi `Document` được chuẩn hóa thành record gồm `id`, `content`, bản sao `metadata` và embedding. Khi search, query chỉ được embed một lần, sau đó tính dot product với từng record embedding, sắp xếp giảm dần theo `score` và trả về `top_k`.

**`search_with_filter` + `delete_document`**
`search_with_filter` lọc metadata trước rồi mới rank bằng embedding, để không mất tài liệu hợp lệ chỉ vì nó không nằm trong top-k ban đầu. `delete_document` xóa mọi record có `metadata["doc_id"]` khớp với tài liệu gốc và trả `True` nếu có ít nhất một chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`**
Agent gọi `store.search()` hoặc `store.search_with_filter()` để lấy các chunk liên quan, sau đó ghép context có đánh số `[1]`, `[2]` kèm `doc_id` và nguồn để truy vết. Prompt yêu cầu chỉ dùng context, nói rõ khi context không đủ, rồi truyền prompt vào `llm_fn`; nếu store rỗng thì trả thông báo thiếu context thay vì gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) - Cá nhân (30 điểm)

### Kết Quả Kiểm Thử

```text
.\.venv\Scripts\python.exe -m pytest tests -v

42 passed, 1 warning
```

Warning còn lại là `PytestCacheWarning` do không ghi được `.pytest_cache`; test vẫn pass đầy đủ.

```text
.\.venv\Scripts\python.exe main.py "Chunking là gì?"

Đã nạp 225 chunk vào EmbeddingStore, search top-3 chạy được,
KnowledgeBaseAgent trả về chuỗi demo từ prompt có context.
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) - Cá nhân (5 điểm)

Điểm thực tế được tính bằng `LocalEmbedder` với model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên cần đăng ký học phần trước hạn. | Người học phải hoàn tất chọn môn trong thời gian quy định. | cao | 0.741 | Đúng |
| 2 | Thư viện cho phép mượn sách trong thời hạn quy định. | Người dùng có thể gia hạn tài liệu thư viện trước ngày đến hạn. | cao | 0.728 | Đúng |
| 3 | Sinh viên được phúc tra điểm trong 7 ngày. | Điểm học phần có thể được khiếu nại trong thời hạn một tuần. | cao | 0.717 | Đúng |
| 4 | Sinh viên cần đóng học phí đúng hạn. | Mô hình embedding biến văn bản thành vector số. | thấp | 0.538 | Tương đối đúng |
| 5 | Danh hiệu tập thể tiên tiến yêu cầu 70% sinh viên đạt loại khá trở lên. | Luận án tiến sĩ phải trích dẫn đầy đủ nguồn tham khảo. | thấp | 0.693 | Sai |

**Kết quả bất ngờ nhất**
Cặp 5 bất ngờ nhất vì tôi dự đoán thấp nhưng điểm lại khá cao. Điều này cho thấy embedding local vẫn có thể kéo hai câu lại gần nhau khi chúng cùng thuộc văn phong học vụ/quy định, dù nội dung trả lời cụ thể khác nhau. Vì vậy khi đánh giá retrieval không nên chỉ nhìn score cao, mà phải kiểm chunk có chứa bằng chứng trả lời hay không.

---

## 5. Kết quả truy xuất của tôi (Competition Results) - Cá nhân (10 điểm)

### Cấu hình benchmark

```text
Data dir: data/university_services_retrieval
Embedder: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Strategy: ArticleChunker(chunk_size=900, overlap=100)
Loaded chunks: 379
```

`query_benchmark.md` đã được chuyển ra `report/`, nên file câu hỏi/gold answer không còn bị ingest vào corpus. `bench.py` dùng dữ liệu query từ `query_benchmark.py`.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Score | Relevant trong top-3? | Agent answer / nhận xét |
|---|-------|-----------------------------|-------|------------------------|--------------------------|
| 1 | Danh hiệu "Tập thể Tiên tiến" yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt loại Khá trở lên? | `thi-dua-khen-thuong-uet-2023`, Điều 8, chứa "Có 70% sinh viên..." | 0.761 | Có | Tốt: gold chunk đứng top-1, context đủ để trả lời. |
| 2 | Điều kiện để sinh viên đạt danh hiệu "Sinh viên Xuất sắc" là gì? | `thi-dua-khen-thuong-uet-2023`, Điều 9 | 0.825 | Có | Gold chunk Điều 4 đứng top-2 với score 0.790; top-1 cùng tài liệu nhưng sai Điều. |
| 3 | Sinh viên ĐHBK Hà Nội phúc tra/khiếu nại điểm trong thời hạn bao lâu? | `quy-che-dao-tao-dai-hoc-uet-66`, Điều 35 | 0.772 | Có | Gold chunk HUST Điều 6 đứng top-2 với score 0.760; top-1 cùng chủ đề thi/điểm nhưng sai trường. |
| 4 | Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại UET. | `thi-dua-khen-thuong-uet-2023`, Điều 10 | 0.786 | Có | Top-3 đều liên quan tới tài liệu khen thưởng, nhưng chưa gom đủ Điều 3-9 nên câu trả lời có nguy cơ thiếu danh sách 7 danh hiệu. |
| 5 | Quy định tạo điều kiện tham gia NCKH, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào? | `quy-che-dao-tao-dai-hoc-hust`, Điều 40 | 0.672 | Không | Fail: top-3 bị kéo về các Điều có nhiều từ khóa "nghiên cứu khoa học", không lấy được Điều 2.5 về CTĐT Tài năng/ELITECH. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

### A/B filter và failure case

Query 5 có `metadata_filter={"audience": "student"}`. Kết quả có filter và không filter đều không retrieve được Điều 2.5:

- Có filter: top-3 là Điều 40 HUST, Điều 29 UET, Điều 28 UET.
- Không filter: kết quả vẫn giống như trên.
- Relevant snippet trong top-3: `no`.

**Phân tích lỗi**
Lỗi không nằm ở overlap hay ranh giới chunk. `ArticleChunker` đã giữ Điều theo đơn vị ngữ nghĩa, và tăng `overlap=100` không làm thay đổi kết quả vì Điều 2.5 không bị mất do cắt ranh giới. Nguyên nhân chính là ranking: query chứa các cụm "nghiên cứu khoa học", "trao đổi học thuật", "công nhận tín chỉ", nên embedding ưu tiên các Điều nói trực tiếp về nghiên cứu khoa học/luận án/điểm thưởng NCKH hơn là Điều 2.5, dù Điều 2.5 mới chứa đáp án "CTĐT Tài năng / ELITECH".

Filter `audience=student` cũng chưa đủ hẹp vì trong corpus vẫn có nhiều tài liệu `student` nói về nghiên cứu khoa học. Cách cải thiện là thêm filter hẹp hơn như `institution=hust`, hoặc bổ sung cơ chế rerank/snippet check ưu tiên các cụm "ELITECH", "CTĐT Tài năng", "Chương trình đào tạo Tài năng".

**Điều hay nhất tôi học được**
Cùng một model embedding và cùng corpus, cách chia chunk ảnh hưởng trực tiếp đến khả năng truy vết. Chunk theo Điều giúp nhiều câu hỏi quy định có context rõ hơn, nhưng với câu hỏi mơ hồ hoặc nhiều từ khóa nhiễu, vẫn cần metadata filter hẹp hơn hoặc reranking để lấy đúng section chứa đáp án.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation - tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |
