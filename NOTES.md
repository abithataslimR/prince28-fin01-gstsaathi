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

## D09 · Prompts and Structured Output

### Router prompt versions compared

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---:|---:|---:|---:|
| classify_v1 | 12/20 | 60% | 1 | 107 |
| classify_v2 | 18/20 | 90% | 1 | 272 |
| classify_v3 | 18/20 | 90% | 0 | 390 |
| classify_v4 | 20/20 | 100% | 0 | 392 |

- My best router prompt: `classify_v4` with 20/20.
- What I changed in v4, and what happened to the score: Clarified the boundaries between `docs`, `personal` and `off_topic`. Accuracy improved from 18/20 to 20/20 compared with v3.
- The question my best version still gets wrong: None in the 20-question test set.
- A label in my test set that I changed after seeing the results: None.
- Input tokens per question: v1 107, best version 392.
- The best version achieved 100% accuracy on the 20-question test set, with a higher input-token count than v1. The extra accuracy is worth the additional tokens for this test set.

### My contract (DocMeta)

Common fields:

- `doc_kind`
- `year`
- `language`
- `summary`
- `topics`

Project-specific fields kept:

- `number`
- `date`
- `hsn_code`
- `rate`
- `subject`
- `effective_from`

Contract details:

- Fields I kept from my project card: `number`, `date`, `hsn_code`, `rate`, `subject`, `effective_from`.
- Fields I deleted, and why they make no sense per document: No project-specific fields were deleted.
- The field I tightened, and how: `doc_kind` was restricted using `Literal` to ten allowed document kinds.
- The `year` field is optional and restricted to the range 1950–2027.
- The `language` field is restricted to `en`, `ta`, `hi`, or `other`.
- The `summary` field must contain between 20 and 300 characters.
- The `topics` field requires 1–6 values, with duplicates removed and values converted to lowercase.
- Unknown fields are rejected using Pydantic's `extra="forbid"`.

### Extraction run

- Prompt version: `extract_v1`.
- Documents: 14 successfully extracted, 5 repaired, 0 failed (of 14 parsed PDFs).
- Not finished? Why, and how many are left: All 14 content-bearing PDFs were processed. None remain among the 14 parsed PDFs. Five notification entries had no parsed page content and were excluded after correcting the pending-document selection.
- Most common failure reason, and what I did about it: Pydantic validation errors involving summary length, invalid `doc_kind` values and subject length. The extraction retry mechanism repaired the responses.
- A record that was valid but wrong (document, field, what it said, what is true): No confirmed valid-but-wrong record was identified during the checks performed.
- Cost at list price: Approximately Rs 0.8747 in total for the 14 parsed PDFs, approximately Rs 0.0625 per document.

### Corpus coverage

The database contains 34 document rows:

| Document type | Total documents | Documents with content | Rows with extraction metadata |
|---|---:|---:|---:|
| Central Tax Rate Notification | 20 | 0 | 5 |
| PDF | 14 | 14 | 14 |
| **Total** | **34** | **14** | **19** |

Observations:

- All 14 PDFs with parsed page content were processed using `extract_v1`.
- No extraction failures remained for those 14 PDFs.
- Five Central Tax Rate Notification entries had no parsed page content.
- Those five entries were processed during the initial run before the pending-document selection was corrected.
- The five empty entries are not counted among the 14 successfully extracted parsed PDFs.

### Live API filter verification

Tested the document endpoint using the development server.

**Language filter**

URL:

```text
http://localhost:8000/v1/documents?language=en&limit=3
```

Result:

- Total matching documents: 14.
- Three matching documents were returned.
- The `language=en` filter worked.

**Document kind filter**

URL:

```text
http://localhost:8000/v1/documents?doc_kind=notice&limit=3
```

Result:

- Total matching documents: 19.
- Three matching documents were returned.
- The `doc_kind=notice` filter worked.
- The count includes the five empty notification entries that had earlier received extraction metadata.

**Year filter**

URL:

```text
http://localhost:8000/v1/documents?year=2025&limit=3
```

Result:

- Total matching documents: 10.
- Three matching documents were returned.
- The `year=2025` filter worked.

**URL tracking parameter observation**

- Opening a ChatGPT-generated link added `utm_source=chatgpt.com` to the request.
- The API treated this as an additional metadata filter, resulting in zero matches.
- Typing the URL manually without the tracking parameter returned the expected results.
- No code change was required for this issue.

### Manual verification status

The D09 instructions require checking at least five extracted records against their original documents by hand.

- Manual source verification of five extracted records: Not yet confirmed.
- Do not mark this requirement complete until five records have been checked against their original PDFs.

### One thing that went wrong today, and how I fixed it

- The extraction pending-document query initially selected documents based only on `doc_type`.
- This included notification entries that had no parsed page content.
- Those empty entries were incorrectly sent for extraction and received a summary stating that no content was available.
- Inspected the database and confirmed that the 20 notification entries had zero documents with page content.
- Updated the pending-document selection in `extract.py` to require at least one non-empty page of text.
- Re-ran the tests successfully.
- The corrected extraction run processed the 14 actual PDFs with content and left the empty notification entries out of subsequent extraction runs.
