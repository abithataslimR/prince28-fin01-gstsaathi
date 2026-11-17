
# GSTSaathi

Answers GST questions for small manufacturers: rate on a given date, input tax credit, invoice reconciliation, and compliance.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates).

## Who it's for

Accountant at a 40-employee pump-set manufacturer in Coimbatore who files GSTR-1 and GSTR-3B monthly and handles e-invoices.

## The problem

GST rules are available across many government documents, such as Acts, Rules, notifications, circulars, and FAQs. Finding the correct information takes time, especially when GST rates change over time. Accountants need to know which rate was applicable to a particular HSN code on a particular date. GSTSaathi aims to make this information easier to find using official government sources.

## Data sources

CBIC GST Acts and Rules, central tax and rate notifications, circulars, FAQs, and GST Council decisions.

- https://cbic-gst.gov.in/
- https://gstcouncil.gov.in/
- https://www.gst.gov.in/
- Terms: Public government documents. Cite notification number and date.

## Hardest problem (my interview story)

Time-bound rates: the same HSN code has different rates on different dates. Answers must use the rate applicable on the requested date, not just the latest rate.

## Signature feature

HSN rate timeline: enter an HSN code and see its rate history with notification references and effective dates.

## Target metric

Rate-on-date correctness of 95%+ on 50 HSN-date tests.

## Run it locally

```bash
uv sync
cp .env.example .env
uv run uvicorn gstsaathi.api.main:create_app --factory --reload
```

On Windows, use `copy .env.example .env` instead of `cp`.

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```

