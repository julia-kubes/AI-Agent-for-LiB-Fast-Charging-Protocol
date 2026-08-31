# Retrieval integration contract (implemented)

The application layer deliberately does not import `embedding/embed-and-store.py`.
The revised implementation is connected through `app/retrieval_adapter.py`
without coupling the agent, UI, or provider client to retrieval internals.

## Required methods

### `search_chunks(query, filters, top_k)`

Return `list[EvidenceChunk]`, ordered best-first. The adapter must use
`Alibaba-NLP/gte-modernbert-base` by default so query vectors remain compatible
with the stored Neon vectors. Apply `SearchFilters.record_id` when present and
exclude section names case-insensitively. Use parameterized SQL.

Required fields per result:

- `chunk_id`
- `record_id`
- `text`

Strongly preferred fields:

- `title`
- `section`
- `page_numbers`
- `similarity`
- remaining source metadata

### `fetch_neighbors(chunk_id, before, after)`

Resolve the chunk's `record_id` and `chunk_index`, then return at most two
preceding and two following chunks from that record. Do not cross document
boundaries.

### `get_paper_metadata(record_id)`

Return a JSON-serializable mapping containing available citation metadata such
as title, authors, publication year, DOI, and source filename.

## Important invariants

- Never expose `DATABASE_URL` or raw SQL to the language model.
- Never accept table or column identifiers from model-generated arguments.
- Preserve stable chunk IDs exactly as stored.
- Return page numbers as integers.
- Return an empty list for no search results, not `None`.
- Do not silently substitute a different embedding model.

## Integration verification

After implementing the adapter:

1. Run one known semantic query directly against `search_chunks`.
2. Confirm every returned chunk ID exists in Neon.
3. Confirm introduction and abstract filters work.
4. Confirm neighboring chunks stay within one record.
5. Run `python -m app.cli --question "..."` with Parley configured.
6. Run the evaluation harness with the live adapters enabled.
