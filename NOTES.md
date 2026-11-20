
# Engineering notes: GSTSaathi

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
$ uv run alembic downgrade -1
Running downgrade cfd1990bf356 -> a74d77e851a0, add gin index on metadata

$ uv run alembic current
a74d77e851a0

$ uv run alembic upgrade head
Running upgrade a74d77e851a0 -> cfd1990bf356, add gin index on metadata

$ uv run alembic history
a74d77e851a0 -> cfd1990bf356 (head), add gin index on metadata
<base> -> a74d77e851a0, create documents and pages tables
```

### The loader is idempotent

```text
run 1: records=20 inserted=20 updated=0 unchanged=0

run 2: records=20 inserted=0 updated=0 unchanged=20

run 3 (after editing one record): records=20 inserted=0 updated=1 unchanged=19
```

### EXPLAIN for ?hsn_code=8406

```text
$ uv run python scripts/explain.py hsn_code 8406

-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=2.564..2.565 rows=1.00 loops=1)
  Filter: (metadata @> '{"hsn_code": "8406"}'::jsonb)
  Rows Removed by Filter: 19
  Buffers: shared read=2 dirtied=2
Planning:
  Buffers: shared hit=143 read=8 dirtied=1
Planning Time: 10.662 ms
Execution Time: 2.598 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=12.81..16.82 rows=1 width=36) (actual time=2.387..2.389 rows=1.00 loops=1)
  Recheck Cond: (metadata @> '{"hsn_code": "8406"}'::jsonb)
  Heap Blocks: exact=2
  Buffers: shared hit=3 read=2
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.81 rows=1 width=0) (actual time=2.352..2.353 rows=4.00 loops=1)
        Index Cond: (metadata @> '{"hsn_code": "8406"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=1 read=2
Planning:
  Buffers: shared hit=1
Planning Time: 0.072 ms
Execution Time: 2.438 ms
```

Why did the planner choose a Seq Scan on my table?

The table contains only 20 rows, so scanning all rows is cheaper than using an index. The planner estimates that a sequential scan has lower cost for this small table.

When would it switch to the GIN index?

When the table becomes larger and the planner estimates that using the GIN index is cheaper.

## D04 · Docker, Compose and tests

### The image

```text
docker images gstsaathi:dev

IMAGE           ID             DISK USAGE   CONTENT SIZE
gstsaathi:dev   c7f529ca1492        300MB           70MB

docker run --rm gstsaathi:dev id

uid=999(app) gid=999(app) groups=999(app)

```

### The stack

```text
docker compose ps -a

gstsaathi-api-1       Up (healthy)
gstsaathi-db-1        Up (healthy)
gstsaathi-migrate-1   Exited (0)
gstsaathi-redis-1     Up (healthy)

```

Migration and loader output:

records=20 inserted=0 updated=0 unchanged=20

db stopped: /health → status: ok

db stopped: /ready → not_ready, database: false

db started: /ready → ready, database: true

A load balancer should stop sending traffic when the API is not ready,
but it should not restart the application because the API process is
still alive. Once the database recovers, the API becomes ready again.

### Tests and coverage

```text
uv run poe test             → 16 passed
uv run poe test-integration → 7 passed
coverage TOTAL, unit only   → 73%
coverage TOTAL, with integration tests → 81%
```

## D05 · CI/CD and production

### Deployment

- Application: https://gstsaathi.onrender.com
- Health endpoint: https://gstsaathi.onrender.com/health
- API documentation: https://gstsaathi.onrender.com/docs
- CI workflow: GitHub Actions
- CD workflow: GitHub Actions
- Production hosting: Render
- Database: Neon PostgreSQL

### Rollback drill

Manual rollback was triggered through GitHub Actions → CD → Run workflow.

- Previous successful deployment SHA:
  `b2d48a0e6a6c6f72cb82a390143954a3e5afa46a`
- Rollback result: Success
- Smoke test: Passed
- Database migrations: Skipped during manual rollback.

### Roll-forward drill

The latest version was restored through GitHub Actions → CD → Run workflow.

- Latest deployment SHA:
  `85e6f366cffef34bb5ada25bdacb07f8bfab5f19`
- Roll-forward result: Success
- Smoke test: Passed

### Production monitoring

- Monitor: UptimeRobot
- Endpoint: https://gstsaathi.onrender.com/health
- Check interval: 5 minutes
- Alert notification: Email
