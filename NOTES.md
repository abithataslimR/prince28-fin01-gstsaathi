# Engineering Notes: GSTSaathi

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
$ uv run alembic downgrade -1
Running downgrade cfd1990bf356 -> a74d77e851a0, add gin index on metadata

$ uv run alembic current
a74d77e851a0

$ uv run alembic upgrade head
Running upgrade a74d77e851a0 -> cfd1990bf356, add gin index on metadata
```

### Verification

- Downgrade completed successfully.
- Current migration revision was verified.
- Upgrade completed successfully.
- The database schema is up to date.

## D04 · API and Testing

### Test results

```text
$ uv run poe test

36 passed
```

### Notes

- Existing tests passed.
- No test failures were reported.

## D05 · Data Collection

### Raw data and manifest

- Raw documents were checked under `data/raw/`.
- The manifest was checked for registered document entries.
- The raw-file count and manifest-entry count did not match, so this mismatch was noted for review.

## D06 · Corpus Preparation

### Collection notes

- Raw GST documents were collected and stored under `data/raw/`.
- The manifest was used to track document information.
- Sources used: URL list / manual collection.


### Kill and resume

- Run 1: Ctrl+C result was not recorded.
- Run 2: Downloaded and skipped counts were not recorded.
- Run 3: Downloaded and skipped counts were not recorded.
- Test counts were not recorded; existing corpus was preserved.

## D07 · Document Parsing

### Setup

Created a separate feature branch:

```text
git switch main
git pull
git switch -c feat/day-07-parse
```

Installed the parsing dependencies:

```text
uv add "pymupdf>=1.26,<2" trafilatura
```

- PyMuPDF version: 1.28.2
- Trafilatura version: 2.4.0

### Database changes

Updated the `Page` model with a `headings` field:

```python
headings: Mapped[list[str]] = mapped_column(JSONB, server_default="[]")
```

Added the `ParseFailure` model to track documents that could not be parsed.

Created the migration:

```text
uv run alembic revision --autogenerate -m "add page headings and parse_failures"
uv run alembic upgrade head
```

- Migration file: `8dcd20198586_add_page_headings_and_parse_failures.py`
- Upgrade completed successfully.
- Downgrade and upgrade operations were inspected.

### Parser implementation

Created the following files:

- `src/gstsaathi/ingest/parse.py`
- `src/gstsaathi/ingest/store.py`
- `tests/unit/test_parse.py`
- `tests/integration/test_parse_store.py`

Ran the tests:

```text
uv run poe test
```

Result:

```text
52 passed, 1 warning
```

Ran lint:

```text
uv run poe lint
```

- Initial lint run reported a formatting issue in `models.py`.
- Formatted the code using `uv run ruff format .`.
- Re-ran lint successfully.
- Ruff check passed.
- Ruff format check passed for all 42 files.

### First 20 files – initial parse

Command:

```text
uv run python scripts/parse_corpus.py --limit 20
```

Output:

```text
files=14 already_parsed=10 failed_before=1 parsed=3 pages=75 seconds=37.1
```

Observations:

- 14 files were considered by the script.
- 10 files were already parsed.
- 1 previous failure was recorded.
- 3 files were newly parsed.
- 75 pages were processed.
- Parsing took 37.1 seconds.

### Parsed-page inspection

Inspected the parsed document and page records using Neon SQL queries.

Observations:

- `notification-13-2025` contained extracted text and table content across its four pages.
- No headings were detected for those four pages.
- The `SCHEDULE` document had detected headings on page 15:
  - `SCHEDULE`
  - `Annexure-II`
  - `[See S. No. 161 of the Schedule]`
- The inspected `SCHEDULE` page had blank extracted text.
- Table content was represented using Markdown-style pipes and line breaks.
- Further inspection was required to evaluate extraction quality.

### Full corpus parse and repeatability

Ran the full parser:

```text
uv run python scripts/parse_corpus.py
```

First run:

```text
files=14 already_parsed=13 failed_before=1 pages=0 seconds=1.8
```

Second run:

```text
files=14 already_parsed=13 failed_before=1 pages=0 seconds=1.0
```

Observations:

- Both runs completed without parsing new files.
- The already-parsed count remained 13.
- One failed document remained.
- The second run did not create duplicate page records.
- The repeated run confirmed that successfully parsed documents were skipped.

### Parse failure investigation

Used the following SQL query:

```sql
select reason, count(*) as files, min(path) as example
from parse_failures
group by reason
order by files desc;
```

Result:

| reason | files | example |
|---|---:|---|
| no_text_layer | 1 | data/raw/gst-council/circular-no-247-04-2025-9ad85c95.pdf |

Investigation:

- Checked that the PDF existed.
- File size was approximately 1,067,938 bytes.
- Opened the PDF and confirmed that it was scanned.
- The document did not contain selectable text.
- Normal text extraction could not process it.

### OCR setup and retry

Installed Tesseract OCR for Windows.

Installation path:

```text
D:\Tools\Tesseract-OCR
```

Verified the installation:

```text
D:\Tools\Tesseract-OCR\tesseract.exe --version
```

Output:

```text
tesseract v5.5.3.20260724
```

Added Tesseract to the current PowerShell session PATH:

```powershell
$env:Path += ";D:\Tools\Tesseract-OCR"
```

Retried the failed document with English OCR:

```text
uv run python scripts/parse_corpus.py --retry-failed --ocr eng
```

Output:

```text
files=14 already_parsed=13 parsed=1 pages=4 seconds=10.4
```

Result:

- The previously failed scanned PDF was successfully parsed.
- OCR extracted all four pages.
- The `no_text_layer` failure was resolved.

### Parser comparison

Created:

```text
scripts/compare_parsers.py
```

Ran:

```text
uv run python scripts/compare_parsers.py
```

The script compared PyMuPDF and pypdf on 10 PDF files.

| File | Pages | PyMuPDF result | pypdf result | Time (PyMuPDF / pypdf) | Better, why |
|---|---:|---|---|---|---|
| circular-no-247-04-2025-9ad85c95.pdf | - | FAILED: no_text_layer | FAILED: no_text_layer | 0.04 s / 0.02 s | Neither; both require OCR for this scanned PDF. |
| circular-no-242-2024-597af1e2.pdf | 5 | 11,311 chars, 9 headings, 0 tables | 11,132 chars, 0 headings, 0 tables | 0.08 s / 0.27 s | PyMuPDF; more text and heading detection. |
| circular-no-243-2024-5852d706.pdf | 7 | 15,181 chars, 9 headings, 0 tables | 14,950 chars, 0 headings, 0 tables | 0.07 s / 0.30 s | PyMuPDF; more text and heading detection. |
| circular-no-250-2025-1-04359515.pdf | 3 | 4,424 chars, 2 headings, 0 tables | 4,352 chars, 0 headings, 0 tables | 0.04 s / 0.11 s | PyMuPDF; more text and heading detection. |
| circular-no-163-18-2021-gst-460463f5.pdf | 9 | 33,494 chars, 3 headings, 7 tables | 20,123 chars, 0 headings, 0 tables | 1.93 s / 0.43 s | PyMuPDF; substantially more text and table extraction. |
| notification-09-2025.pdf.pdf | 56 | 211,101 chars, 8 headings, 11 tables | 179,156 chars, 0 headings, 0 tables | 30.98 s / 2.16 s | PyMuPDF; more text, headings and tables. |
| cir-cgst-246-03-2025-2dc22a72.pdf | 4 | 7,810 chars, 4 headings, 0 tables | 7,699 chars, 0 headings, 0 tables | 0.08 s / 0.18 s | PyMuPDF; more text and heading detection. |
| notification-01-2026.pdf | 1 | 1,856 chars, 0 headings, 0 tables | 1,838 chars, 0 headings, 0 tables | 0.03 s / 0.04 s | PyMuPDF; slightly more extracted text. |
| notification-10-2025.pdf | 15 | 24,088 chars, 3 headings, 13 tables | 22,712 chars, 0 headings, 0 tables | 4.01 s / 0.56 s | PyMuPDF; more text and table extraction. |
| cir-245022025-cgst-9581e04d.pdf | 8 | 19,406 chars, 14 headings, 0 tables | 19,403 chars, 0 headings, 0 tables | 0.08 s / 0.27 s | PyMuPDF; heading detection and slightly more text. |

### Comparison observations

- Compared 10 PDF files using PyMuPDF and pypdf.
- PyMuPDF extracted more text in all nine files where native text extraction succeeded.
- PyMuPDF detected headings and tables in several documents.
- pypdf did not detect headings or tables in these comparisons.
- pypdf was faster on some larger PDFs.
- Neither parser could extract text from the scanned PDF without OCR.
- OCR successfully extracted all four pages of the scanned PDF.

### Parser decision

PyMuPDF is preferred because it supports heading detection and table extraction in addition to text extraction. Although pypdf was faster on some larger files, it did not detect headings or tables in these comparisons.

OCR is required for scanned PDFs that do not contain a text layer.

### Original PDF inspection

Inspected three original PDFs alongside the parser comparison results.

**1. circular-no-163-18-2021-gst-460463f5.pdf**

- Tables: No tables present.
- Headings: Clearly visible.
- Headers/footers: Present (circular number, date or page information).

**2. notification-10-2025.pdf**

- Tables: Present and properly aligned.
- Headings: Clearly visible.
- Headers: Gazette publication details and notification date visible.

**3. circular-no-242-2024-597af1e2.pdf**

- Tables: No tables present.
- Headings: Clearly visible.
- Headers/footers: Present.
