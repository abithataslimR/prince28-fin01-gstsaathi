# Ingestion report

<!-- generated:start -->
_Generated 27 Nov 2026 15:14 from the database._

| What | Count |
|---|---|
| Documents in the database | 98 |
| Pages | 369 |
| Tokens of text (characters ÷ 4) | 223,546 |
| Files the parser gave up on | 0 |
| Documents with an extracted record | 68 |
| Documents whose extraction failed | 0 |

| Queue | Count |
|---|---|
| Ingest jobs started | 7 |
| Items finished (done or skipped) | 55 |
| Items that needed more than one try | 47 |
| Items in the dead-letter list | 32 |

Model calls for extraction: 245 · tokens in 215,717 · tokens out 96,436 · cost at list price Rs 3.98

Last job `7e413521066f41fab495c52be9d886a7`: 17 requested, 2 ok, 15 failed, 5.2 minutes.

Dead-letter list by stage: gave up after 3 tries 32
<!-- generated:end -->

## What I learnt

1. Redis helps manage background jobs using a queue.
2. ARQ workers process ingestion jobs asynchronously and retry failed jobs.
3. A dead-letter queue helps track failed jobs without losing their status.
