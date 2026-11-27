# Capacity plan

<!-- generated:start -->
## Measured on my start corpus (2026-11-26 04:52 UTC)

| What | Value |
|---|---|
| Files | 296 |
| Size on disk | 110.1 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 1,319 |
| Characters of text | 2,721,996 |
| Estimated tokens (characters / 4) | 680,499 |
| Tokens per page | 516 |
| PDFs with almost no text (scanned? OCR is Day 7) | 4 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 3,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 2.3 |
| Tokens | measured tokens x scale | 1.55 M |
| Raw files | measured MB x scale | 250 MB |
| Chunks | tokens / 400 x 1.15 overlap | 4,450 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.27 = Rs 25 |
| Vector storage | chunks x 768 numbers x 4 bytes | 14 MB |
| Text in Postgres | characters x scale x 1.2 | 7 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. For the 3,000-page target, the estimated one-time embedding cost is Rs 30.
2. Estimated storage is approximately 25 MB (16 MB vector storage + 9 MB text in Postgres). I need to compare this with my free Postgres storage limit.
3. The current corpus contains 15 files and 128 pages, with an estimated 609 tokens per page. One PDF has almost no extractable text and may need OCR.
4. If the corpus grows, storage, tokens, chunks and embedding costs will increase approximately proportionally.
5. The current dataset is still incomplete. The target of 300 circulars has not yet been reached.
