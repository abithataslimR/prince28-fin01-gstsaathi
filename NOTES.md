
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
