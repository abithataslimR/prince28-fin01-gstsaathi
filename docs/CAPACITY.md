# Capacity plan

<!-- generated:start -->
## Measured on my start corpus (2026-11-24 04:35 UTC)

| What | Value |
|---|---|
| Files | 14 |
| Size on disk | 6.5 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 123 |
| Characters of text | 310,002 |
| Estimated tokens (characters / 4) | 77,500 |
| Tokens per page | 630 |
| PDFs with almost no text (scanned? OCR is Day 7) | 1 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 8,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 65.0 |
| Tokens | measured tokens x scale | 5.04 M |
| Raw files | measured MB x scale | 421 MB |
| Chunks | tokens / 400 x 1.15 overlap | 14,492 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.87 = Rs 83 |
| Vector storage | chunks x 768 numbers x 4 bytes | 45 MB |
| Text in Postgres | characters x scale x 1.2 | 24 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. Embedding cost is estimated at ₹83 for the 8,000-page target.
2. Estimated storage is 69 MB (45 MB vector storage + 24 MB text in Postgres). I need to compare it with my free Postgres storage limit.
3. I am least sure about the 630 tokens per page estimate because only 14 PDFs were measured.
4. If the corpus grows 10 times, storage, tokens, chunks and cost will also grow approximately 10 times.
