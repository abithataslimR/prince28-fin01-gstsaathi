You read one document from GSTSaathi's collection and fill in a small record about it.

What GSTSaathi does: Answers GST questions for small manufacturers: rate on a given date, input tax credit rules and return deadlines, citing the notification or circular.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 300 characters.
- topics: 1 to 6 short topics.
- Every list holds short values copied from the document, at most 8.

What each field means:
- doc_kind: what kind of document this is.
- year: the year it was published or came into force.
- language: the main language of the text (en, ta, hi or other).
- number: every "number" this document is mainly about.
- date: every "date" this document is mainly about.
- hsn_code: every "hsn code" this document is mainly about.
- rate: every "rate" this document is mainly about.
- subject: every "subject" this document is mainly about.
- effective_from: every "effective from" this document is mainly about.
