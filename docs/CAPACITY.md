# Capacity plan

<!-- generated:start -->
## Measured on my start corpus (2026-11-27 05:51 UTC)

| What | Value |
|---|---|
| Files | 300 |
| Size on disk | 115.9 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 1,562 |
| Characters of text | 3,297,705 |
| Estimated tokens (characters / 4) | 824,426 |
| Tokens per page | 528 |
| PDFs with almost no text (scanned? OCR is Day 7) | 4 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 8,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 5.1 |
| Tokens | measured tokens x scale | 4.22 M |
| Raw files | measured MB x scale | 594 MB |
| Chunks | tokens / 400 x 1.15 overlap | 12,139 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.73 = Rs 69 |
| Vector storage | chunks x 768 numbers x 4 bytes | 37 MB |
| Text in Postgres | characters x scale x 1.2 | 20 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->


## What I conclude

1. Embedding cost is not a major problem: the estimated one-time cost for 8,000 pages is approximately Rs 69.

2. Estimated vector storage is 37 MB and PostgreSQL text storage is 20 MB, totalling approximately 57 MB. I need to compare this with my free Postgres storage limit.

3. The least certain number is the estimated 824,426 tokens, because it uses characters divided by 4 rather than an actual tokenizer. I will measure actual tokens when the embedding pipeline is ready.

4. If the corpus grows 10 times, tokens, chunks, storage and embedding costs will grow approximately 10 times. The estimated embedding cost will become approximately Rs 690, with around 370 MB of vector storage and 200 MB of text storage.
