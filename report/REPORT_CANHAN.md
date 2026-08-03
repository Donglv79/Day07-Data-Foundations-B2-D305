# BÃ¡o CÃ¡o CÃ¡ NhÃ¢n - Lab 7: Embedding & Vector Store

**Há» tÃªn:** [TÃªn sinh viÃªn]
**NhÃ³m:** [TÃªn nhÃ³m]
**NgÃ y:** [NgÃ y ná»™p]

> Ná»™p 1 báº£n / sinh viÃªn. Pháº§n nhÃ³m ná»™p chung trong `REPORT_NHOM.md`.

**Tá»•ng Ä‘iá»ƒm pháº§n cÃ¡ nhÃ¢n: 60** = Khá»Ÿi Ä‘á»™ng (5) + HÆ°á»›ng tiáº¿p cáº­n (10) + HoÃ n thiá»‡n code (30) + Dá»± Ä‘oÃ¡n Ä‘á»™ tÆ°Æ¡ng tá»± (5) + Káº¿t quáº£ truy xuáº¥t cá»§a tÃ´i (10).

---

## 1. Khá»Ÿi Ä‘á»™ng (Warm-up) - CÃ¡ nhÃ¢n (5 Ä‘iá»ƒm)

### Äá»™ tÆ°Æ¡ng tá»± Cosine (Cosine Similarity)

**Äá»™ tÆ°Æ¡ng tá»± cosine cao nghÄ©a lÃ  gÃ¬?**
Cosine similarity cao nghÄ©a lÃ  hai vector embedding cÃ³ hÆ°á»›ng gáº§n nhau, nÃªn hai Ä‘oáº¡n text cÃ³ xu hÆ°á»›ng gáº§n nhau vá» ngá»¯ nghÄ©a hoáº·c má»¥c Ä‘Ã­ch há»i/Ä‘Ã¡p. NÃ³ khÃ´ng yÃªu cáº§u hai cÃ¢u dÃ¹ng Ä‘Ãºng cÃ¹ng tá»«, miá»…n lÃ  mÃ´ hÃ¬nh embedding biá»ƒu diá»…n chÃºng gáº§n nhau trong khÃ´ng gian vector.

**VÃ­ dá»¥ cÃ³ Ä‘á»™ tÆ°Æ¡ng tá»± CAO:**
- CÃ¢u A: Sinh viÃªn cáº§n Ä‘Äƒng kÃ½ há»c pháº§n trÆ°á»›c háº¡n cá»§a há»c ká»³.
- CÃ¢u B: NgÆ°á»i há»c pháº£i hoÃ n táº¥t chá»n mÃ´n trong thá»i gian Ä‘Äƒng kÃ½ quy Ä‘á»‹nh.
- Táº¡i sao tÆ°Æ¡ng Ä‘á»“ng: Hai cÃ¢u dÃ¹ng tá»« khÃ¡c nhau nhÆ°ng cÃ¹ng nÃ³i vá» nghÄ©a vá»¥ Ä‘Äƒng kÃ½ mÃ´n Ä‘Ãºng thá»i háº¡n.

**VÃ­ dá»¥ cÃ³ Ä‘á»™ tÆ°Æ¡ng tá»± THáº¤P:**
- CÃ¢u A: Sinh viÃªn cáº§n Ä‘Äƒng kÃ½ há»c pháº§n trÆ°á»›c háº¡n cá»§a há»c ká»³.
- CÃ¢u B: ThÆ° viá»‡n má»Ÿ cá»­a cuá»‘i tuáº§n theo lá»‹ch phá»¥c vá»¥ riÃªng.
- Táº¡i sao khÃ¡c: Hai cÃ¢u thuá»™c hai chá»§ Ä‘á» khÃ¡c nhau: Ä‘Äƒng kÃ½ há»c pháº§n vÃ  giá» phá»¥c vá»¥ thÆ° viá»‡n.

**Táº¡i sao cosine similarity Ä‘Æ°á»£c Æ°u tiÃªn hÆ¡n Euclidean distance cho text embeddings?**
Cosine táº­p trung vÃ o hÆ°á»›ng cá»§a vector, phÃ¹ há»£p hÆ¡n Ä‘á»ƒ so sÃ¡nh Ã½ nghÄ©a cá»§a text embedding. Khoáº£ng cÃ¡ch Euclid dá»… bá»‹ áº£nh hÆ°á»Ÿng bá»Ÿi Ä‘á»™ lá»›n vector, trong khi retrieval thÆ°á»ng cáº§n biáº¿t hai Ä‘oáº¡n vÄƒn gáº§n nhau vá» ngá»¯ nghÄ©a hÆ¡n lÃ  vector dÃ i hay ngáº¯n.

### BÃ i toÃ¡n tÃ­nh toÃ¡n Chunking

**TÃ i liá»‡u 10,000 kÃ½ tá»±, chunk_size=500, overlap=50. Bao nhiÃªu chunks?**
PhÃ©p tÃ­nh: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`
ÄÃ¡p Ã¡n: **23 chunks**.

**Náº¿u overlap tÄƒng lÃªn 100, sá»‘ lÆ°á»£ng chunk thay Ä‘á»•i tháº¿ nÃ o?**
Khi overlap tÄƒng lÃªn 100, bÆ°á»›c nháº£y cÃ²n 400 nÃªn sá»‘ chunk tÄƒng lÃªn: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lá»›n hÆ¡n giÃºp giá»¯ ngá»¯ cáº£nh á»Ÿ ranh giá»›i chunk, nhÆ°ng lÃ m tÄƒng sá»‘ record cáº§n embed vÃ  tÃ¬m kiáº¿m.

---

## 2. HÆ°á»›ng tiáº¿p cáº­n cá»§a tÃ´i (My Approach) - CÃ¡ nhÃ¢n (10 Ä‘iá»ƒm)

### CÃ¡c hÃ m chia nhá» (Chunking Functions)

**`SentenceChunker.chunk`**
TÃ´i dÃ¹ng regex `(?<=[.!?])\s+` Ä‘á»ƒ tÃ¡ch táº¡i khoáº£ng tráº¯ng sau dáº¥u káº¿t thÃºc cÃ¢u, nhá» Ä‘Ã³ dáº¥u cÃ¢u váº«n náº±m á»Ÿ cÃ¢u phÃ­a trÆ°á»›c. Text rá»—ng tráº£ vá» `[]`; tá»«ng cÃ¢u Ä‘Æ°á»£c `strip()` vÃ  bá» pháº§n rá»—ng trÆ°á»›c khi gá»™p tá»‘i Ä‘a `max_sentences_per_chunk` cÃ¢u vÃ o má»™t chunk.

**`RecursiveChunker.chunk` / `_split`**
TÃ´i tÃ¡ch theo separator Æ°u tiÃªn tá»« tá»± nhiÃªn Ä‘áº¿n nhá» hÆ¡n: Ä‘oáº¡n, dÃ²ng, cÃ¢u, tá»«, rá»“i kÃ½ tá»±. Base case lÃ  text Ä‘Ã£ ngáº¯n hÆ¡n `chunk_size`, hoáº·c háº¿t separator thÃ¬ cáº¯t cá»‘ Ä‘á»‹nh; náº¿u má»™t pháº§n sau khi tÃ¡ch váº«n quÃ¡ dÃ i, pháº§n Ä‘Ã³ Ä‘Æ°á»£c xá»­ lÃ½ tiáº¿p báº±ng separator Æ°u tiÃªn tháº¥p hÆ¡n.

**Chiáº¿n lÆ°á»£c benchmark riÃªng: `ArticleChunker`**
TÃ´i viáº¿t thÃªm `ArticleChunker` Ä‘á»ƒ tÃ¡ch tÃ i liá»‡u quy Ä‘á»‹nh tiáº¿ng Viá»‡t theo heading `Äiá»u <sá»‘>.` hoáº·c `Äiá»u <sá»‘>:`. LÃ½ do chá»n chiáº¿n lÆ°á»£c nÃ y lÃ  corpus cá»§a nhÃ³m chá»§ yáº¿u lÃ  quy cháº¿/quy Ä‘á»‹nh, trong Ä‘Ã³ má»—i Äiá»u thÆ°á»ng lÃ  má»™t Ä‘Æ¡n vá»‹ ngá»¯ nghÄ©a hoÃ n chá»‰nh. Cáº¥u hÃ¬nh benchmark cuá»‘i cÃ¹ng lÃ  `ArticleChunker(chunk_size=900, overlap=100)`: cÃ¡c Äiá»u ngáº¯n hÆ¡n 900 kÃ½ tá»± Ä‘Æ°á»£c giá»¯ nguyÃªn; Äiá»u dÃ i hÆ¡n ngÆ°á»¡ng sáº½ Ä‘Æ°á»£c cáº¯t nhá» vÃ  gáº¯n láº¡i tiÃªu Ä‘á» Äiá»u vÃ o tá»«ng sub-chunk.

### Lá»›p EmbeddingStore

**`add_documents` + `search`**
TÃ´i dÃ¹ng in-memory store: má»—i `Document` Ä‘Æ°á»£c chuáº©n hÃ³a thÃ nh record gá»“m `id`, `content`, báº£n sao `metadata` vÃ  embedding. Khi search, query chá»‰ Ä‘Æ°á»£c embed má»™t láº§n, sau Ä‘Ã³ tÃ­nh dot product vá»›i tá»«ng record embedding, sáº¯p xáº¿p giáº£m dáº§n theo `score` vÃ  tráº£ vá» `top_k`.

**`search_with_filter` + `delete_document`**
`search_with_filter` lá»c metadata trÆ°á»›c rá»“i má»›i rank báº±ng embedding, Ä‘á»ƒ khÃ´ng máº¥t tÃ i liá»‡u há»£p lá»‡ chá»‰ vÃ¬ nÃ³ khÃ´ng náº±m trong top-k ban Ä‘áº§u. `delete_document` xÃ³a má»i record cÃ³ `metadata["doc_id"]` khá»›p vá»›i tÃ i liá»‡u gá»‘c vÃ  tráº£ `True` náº¿u cÃ³ Ã­t nháº¥t má»™t chunk bá»‹ xÃ³a.

### TÃ¡c tá»­ KnowledgeBaseAgent

**`answer`**
Agent gá»i `store.search()` hoáº·c `store.search_with_filter()` Ä‘á»ƒ láº¥y cÃ¡c chunk liÃªn quan, sau Ä‘Ã³ ghÃ©p context cÃ³ Ä‘Ã¡nh sá»‘ `[1]`, `[2]` kÃ¨m `doc_id` vÃ  nguá»“n Ä‘á»ƒ truy váº¿t. Prompt yÃªu cáº§u chá»‰ dÃ¹ng context, nÃ³i rÃµ khi context khÃ´ng Ä‘á»§, rá»“i truyá»n prompt vÃ o `llm_fn`; náº¿u store rá»—ng thÃ¬ tráº£ thÃ´ng bÃ¡o thiáº¿u context thay vÃ¬ gá»i LLM.

---

## 3. HoÃ n thiá»‡n code (Core Implementation) - CÃ¡ nhÃ¢n (30 Ä‘iá»ƒm)

### Káº¿t Quáº£ Kiá»ƒm Thá»­

```text
.\.venv\Scripts\python.exe -m pytest tests -v

42 passed, 1 warning
```

Warning cÃ²n láº¡i lÃ  `PytestCacheWarning` do khÃ´ng ghi Ä‘Æ°á»£c `.pytest_cache`; test váº«n pass Ä‘áº§y Ä‘á»§.

```text
.\.venv\Scripts\python.exe main.py "Chunking lÃ  gÃ¬?"

ÄÃ£ náº¡p 225 chunk vÃ o EmbeddingStore, search top-3 cháº¡y Ä‘Æ°á»£c,
KnowledgeBaseAgent tráº£ vá» chuá»—i demo tá»« prompt cÃ³ context.
```

**Sá»‘ lÆ°á»£ng bÃ i test vÆ°á»£t qua (pass):** 42 / 42

---

## 4. Dá»± Ä‘oÃ¡n Ä‘á»™ tÆ°Æ¡ng tá»± (Similarity Predictions) - CÃ¡ nhÃ¢n (5 Ä‘iá»ƒm)

Äiá»ƒm thá»±c táº¿ Ä‘Æ°á»£c tÃ­nh báº±ng `LocalEmbedder` vá»›i model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Cáº·p | CÃ¢u A | CÃ¢u B | Dá»± Ä‘oÃ¡n | Äiá»ƒm thá»±c táº¿ | ÄÃºng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viÃªn cáº§n Ä‘Äƒng kÃ½ há»c pháº§n trÆ°á»›c háº¡n. | NgÆ°á»i há»c pháº£i hoÃ n táº¥t chá»n mÃ´n trong thá»i gian quy Ä‘á»‹nh. | cao | 0.741 | ÄÃºng |
| 2 | ThÆ° viá»‡n cho phÃ©p mÆ°á»£n sÃ¡ch trong thá»i háº¡n quy Ä‘á»‹nh. | NgÆ°á»i dÃ¹ng cÃ³ thá»ƒ gia háº¡n tÃ i liá»‡u thÆ° viá»‡n trÆ°á»›c ngÃ y Ä‘áº¿n háº¡n. | cao | 0.728 | ÄÃºng |
| 3 | Sinh viÃªn Ä‘Æ°á»£c phÃºc tra Ä‘iá»ƒm trong 7 ngÃ y. | Äiá»ƒm há»c pháº§n cÃ³ thá»ƒ Ä‘Æ°á»£c khiáº¿u náº¡i trong thá»i háº¡n má»™t tuáº§n. | cao | 0.717 | ÄÃºng |
| 4 | Sinh viÃªn cáº§n Ä‘Ã³ng há»c phÃ­ Ä‘Ãºng háº¡n. | MÃ´ hÃ¬nh embedding biáº¿n vÄƒn báº£n thÃ nh vector sá»‘. | tháº¥p | 0.538 | TÆ°Æ¡ng Ä‘á»‘i Ä‘Ãºng |
| 5 | Danh hiá»‡u táº­p thá»ƒ tiÃªn tiáº¿n yÃªu cáº§u 70% sinh viÃªn Ä‘áº¡t loáº¡i khÃ¡ trá»Ÿ lÃªn. | Luáº­n Ã¡n tiáº¿n sÄ© pháº£i trÃ­ch dáº«n Ä‘áº§y Ä‘á»§ nguá»“n tham kháº£o. | tháº¥p | 0.693 | Sai |

**Káº¿t quáº£ báº¥t ngá» nháº¥t**
Cáº·p 5 báº¥t ngá» nháº¥t vÃ¬ tÃ´i dá»± Ä‘oÃ¡n tháº¥p nhÆ°ng Ä‘iá»ƒm láº¡i khÃ¡ cao. Äiá»u nÃ y cho tháº¥y embedding local váº«n cÃ³ thá»ƒ kÃ©o hai cÃ¢u láº¡i gáº§n nhau khi chÃºng cÃ¹ng thuá»™c vÄƒn phong há»c vá»¥/quy Ä‘á»‹nh, dÃ¹ ná»™i dung tráº£ lá»i cá»¥ thá»ƒ khÃ¡c nhau. VÃ¬ váº­y khi Ä‘Ã¡nh giÃ¡ retrieval khÃ´ng nÃªn chá»‰ nhÃ¬n score cao, mÃ  pháº£i kiá»ƒm chunk cÃ³ chá»©a báº±ng chá»©ng tráº£ lá»i hay khÃ´ng.

---

## 5. Káº¿t quáº£ truy xuáº¥t cá»§a tÃ´i (Competition Results) - CÃ¡ nhÃ¢n (10 Ä‘iá»ƒm)

### Cáº¥u hÃ¬nh benchmark

```text
Data dir: data/university_services_retrieval
Embedder: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Strategy: ArticleChunker(chunk_size=900, overlap=100)
Loaded chunks: 379
```

`query_benchmark.md` Ä‘Ã£ Ä‘Æ°á»£c chuyá»ƒn ra `report/`, nÃªn file cÃ¢u há»i/gold answer khÃ´ng cÃ²n bá»‹ ingest vÃ o corpus. `bench.py` dÃ¹ng dá»¯ liá»‡u query tá»« `query_benchmark.py`.

| # | CÃ¢u há»i | Top-1 Chunk truy xuáº¥t Ä‘Æ°á»£c | Score | Relevant trong top-3? | Agent answer / nháº­n xÃ©t |
|---|-------|-----------------------------|-------|------------------------|--------------------------|
| 1 | Danh hiá»‡u "Táº­p thá»ƒ TiÃªn tiáº¿n" yÃªu cáº§u tá»‘i thiá»ƒu bao nhiÃªu pháº§n trÄƒm sinh viÃªn Ä‘áº¡t loáº¡i KhÃ¡ trá»Ÿ lÃªn? | `thi-dua-khen-thuong-uet-2023`, Äiá»u 8, chá»©a "CÃ³ 70% sinh viÃªn..." | 0.761 | CÃ³ | Tá»‘t: gold chunk Ä‘á»©ng top-1, context Ä‘á»§ Ä‘á»ƒ tráº£ lá»i. |
| 2 | Äiá»u kiá»‡n Ä‘á»ƒ sinh viÃªn Ä‘áº¡t danh hiá»‡u "Sinh viÃªn Xuáº¥t sáº¯c" lÃ  gÃ¬? | `thi-dua-khen-thuong-uet-2023`, Äiá»u 9 | 0.825 | CÃ³ | Gold chunk Äiá»u 4 Ä‘á»©ng top-2 vá»›i score 0.790; top-1 cÃ¹ng tÃ i liá»‡u nhÆ°ng sai Äiá»u. |
| 3 | Sinh viÃªn ÄHBK HÃ  Ná»™i phÃºc tra/khiáº¿u náº¡i Ä‘iá»ƒm trong thá»i háº¡n bao lÃ¢u? | `quy-che-dao-tao-dai-hoc-uet-66`, Äiá»u 35 | 0.772 | CÃ³ | Gold chunk HUST Äiá»u 6 Ä‘á»©ng top-2 vá»›i score 0.760; top-1 cÃ¹ng chá»§ Ä‘á» thi/Ä‘iá»ƒm nhÆ°ng sai trÆ°á»ng. |
| 4 | Ká»ƒ tÃªn cÃ¡c danh hiá»‡u thi Ä‘ua, khen thÆ°á»Ÿng dÃ nh cho sinh viÃªn táº¡i UET. | `thi-dua-khen-thuong-uet-2023`, Äiá»u 10 | 0.786 | CÃ³ | Top-3 Ä‘á»u liÃªn quan tá»›i tÃ i liá»‡u khen thÆ°á»Ÿng, nhÆ°ng chÆ°a gom Ä‘á»§ Äiá»u 3-9 nÃªn cÃ¢u tráº£ lá»i cÃ³ nguy cÆ¡ thiáº¿u danh sÃ¡ch 7 danh hiá»‡u. |
| 5 | Quy Ä‘á»‹nh táº¡o Ä‘iá»u kiá»‡n tham gia NCKH, trao Ä‘á»•i há»c thuáº­t vÃ  cÃ´ng nháº­n tÃ­n chá»‰ Ã¡p dá»¥ng cho Ä‘á»‘i tÆ°á»£ng nÃ o? | `quy-che-dao-tao-dai-hoc-hust`, Äiá»u 40 | 0.672 | KhÃ´ng | Fail: top-3 bá»‹ kÃ©o vá» cÃ¡c Äiá»u cÃ³ nhiá»u tá»« khÃ³a "nghiÃªn cá»©u khoa há»c", khÃ´ng láº¥y Ä‘Æ°á»£c Äiá»u 2.5 vá» CTÄT TÃ i nÄƒng/ELITECH. |

**Bao nhiÃªu cÃ¢u há»i tráº£ vá» chunk cÃ³ liÃªn quan trong top-3?** 4 / 5

### A/B filter vÃ  failure case

Query 5 cÃ³ `metadata_filter={"audience": "student"}`. Káº¿t quáº£ cÃ³ filter vÃ  khÃ´ng filter Ä‘á»u khÃ´ng retrieve Ä‘Æ°á»£c Äiá»u 2.5:

- CÃ³ filter: top-3 lÃ  Äiá»u 40 HUST, Äiá»u 29 UET, Äiá»u 28 UET.
- KhÃ´ng filter: káº¿t quáº£ váº«n giá»‘ng nhÆ° trÃªn.
- Relevant snippet trong top-3: `no`.

**PhÃ¢n tÃ­ch lá»—i**
Lá»—i khÃ´ng náº±m á»Ÿ overlap hay ranh giá»›i chunk. `ArticleChunker` Ä‘Ã£ giá»¯ Äiá»u theo Ä‘Æ¡n vá»‹ ngá»¯ nghÄ©a, vÃ  tÄƒng `overlap=100` khÃ´ng lÃ m thay Ä‘á»•i káº¿t quáº£ vÃ¬ Äiá»u 2.5 khÃ´ng bá»‹ máº¥t do cáº¯t ranh giá»›i. NguyÃªn nhÃ¢n chÃ­nh lÃ  ranking: query chá»©a cÃ¡c cá»¥m "nghiÃªn cá»©u khoa há»c", "trao Ä‘á»•i há»c thuáº­t", "cÃ´ng nháº­n tÃ­n chá»‰", nÃªn embedding Æ°u tiÃªn cÃ¡c Äiá»u nÃ³i trá»±c tiáº¿p vá» nghiÃªn cá»©u khoa há»c/luáº­n Ã¡n/Ä‘iá»ƒm thÆ°á»Ÿng NCKH hÆ¡n lÃ  Äiá»u 2.5, dÃ¹ Äiá»u 2.5 má»›i chá»©a Ä‘Ã¡p Ã¡n "CTÄT TÃ i nÄƒng / ELITECH".

Filter `audience=student` cÅ©ng chÆ°a Ä‘á»§ háº¹p vÃ¬ trong corpus váº«n cÃ³ nhiá»u tÃ i liá»‡u `student` nÃ³i vá» nghiÃªn cá»©u khoa há»c. CÃ¡ch cáº£i thiá»‡n lÃ  thÃªm filter háº¹p hÆ¡n nhÆ° `institution=hust`, hoáº·c bá»• sung cÆ¡ cháº¿ rerank/snippet check Æ°u tiÃªn cÃ¡c cá»¥m "ELITECH", "CTÄT TÃ i nÄƒng", "ChÆ°Æ¡ng trÃ¬nh Ä‘Ã o táº¡o TÃ i nÄƒng".

**Äiá»u hay nháº¥t tÃ´i há»c Ä‘Æ°á»£c**
CÃ¹ng má»™t model embedding vÃ  cÃ¹ng corpus, cÃ¡ch chia chunk áº£nh hÆ°á»Ÿng trá»±c tiáº¿p Ä‘áº¿n kháº£ nÄƒng truy váº¿t. Chunk theo Äiá»u giÃºp nhiá»u cÃ¢u há»i quy Ä‘á»‹nh cÃ³ context rÃµ hÆ¡n, nhÆ°ng vá»›i cÃ¢u há»i mÆ¡ há»“ hoáº·c nhiá»u tá»« khÃ³a nhiá»…u, váº«n cáº§n metadata filter háº¹p hÆ¡n hoáº·c reranking Ä‘á»ƒ láº¥y Ä‘Ãºng section chá»©a Ä‘Ã¡p Ã¡n.

---

## Tá»± ÄÃ¡nh GiÃ¡ (Pháº§n CÃ¡ NhÃ¢n)

| TiÃªu chÃ­ | Äiá»ƒm tá»± Ä‘Ã¡nh giÃ¡ |
|----------|-------------------|
| Khá»Ÿi Ä‘á»™ng (Warm-up) | 5 / 5 |
| HÆ°á»›ng tiáº¿p cáº­n cá»§a tÃ´i (My Approach) | 10 / 10 |
| HoÃ n thiá»‡n code (Core Implementation - tests) | 30 / 30 |
| Dá»± Ä‘oÃ¡n Ä‘á»™ tÆ°Æ¡ng tá»± (Similarity Predictions) | 4 / 5 |
| Káº¿t quáº£ truy xuáº¥t cá»§a tÃ´i (Competition Results) | 7 / 10 |
| **Tá»•ng pháº§n cÃ¡ nhÃ¢n** | **56 / 60** |
