# Capacity plan

<!-- generated:start -->
## Measured on my start corpus (2026-11-25 06:05 UTC)

| What | Value |
|---|---|
| Files | 15 |
| Size on disk | 8.2 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 128 |
| Characters of text | 311,958 |
| Estimated tokens (characters / 4) | 77,990 |
| Tokens per page | 609 |
| PDFs with almost no text (scanned? OCR is Day 7) | 1 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 3,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 23.4 |
| Tokens | measured tokens x scale | 1.83 M |
| Raw files | measured MB x scale | 193 MB |
| Chunks | tokens / 400 x 1.15 overlap | 5,255 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.32 = Rs 30 |
| Vector storage | chunks x 768 numbers x 4 bytes | 16 MB |
| Text in Postgres | characters x scale x 1.2 | 9 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. For the 3,000-page target, the estimated one-time embedding cost is Rs 30.
2. Estimated storage is approximately 25 MB (16 MB vector storage + 9 MB text in Postgres). I need to compare this with my free Postgres storage limit.
3. The current corpus contains 15 files and 128 pages, with an estimated 609 tokens per page. One PDF has almost no extractable text and may need OCR.
4. If the corpus grows, storage, tokens, chunks and embedding costs will increase approximately proportionally.
5. The current dataset is still incomplete. The target of 300 circulars has not yet been reached.
