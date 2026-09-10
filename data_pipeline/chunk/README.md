# Docling Chunk Creator

`create-chunks.py` creates RAG-ready chunks from the lossless Docling JSON files
produced by `data_pipeline/parse_pdf/docling-convert.py`.

## Input and output layout

Keep the collection data outside the repository. A collection has this layout:

```text
Knowledge Database/
├── Docling_Files/
│   └── 10.1016j.apenergy.2024.124538.json
├── MD_Files/
│   └── 10.1016j.apenergy.2024.124538.md
└── chunk_files/
    └── 10.1016j.apenergy.2024.124538/
        ├── chunks.jsonl
        ├── quarantine.jsonl
        ├── quality_report.json
        └── manifest.json
```

One JSONL file per paper is preferable to one file per chunk: it avoids creating
thousands of tiny files while retaining independent, replaceable paper outputs.
Local filenames and directories use the filesystem-safe `paper_id`. The script
reads the canonical DOI-based `record_id` from the matching Markdown front matter.
Chunk IDs use `<record_id>::chunk::<zero-padded index>`, for example
`10.1016/j.apenergy.2024.124538::chunk::0001`. Each record also includes a SHA-256
content hash. Processing stops for a paper if its Markdown front matter does not
contain `record_id`; the filename stem is never silently substituted.

## Setup

Use the repository virtual environment and install Docling and the tokenizer
dependencies if needed:

```powershell
python -m pip install docling transformers
```

The default tokenizer is `Alibaba-NLP/gte-modernbert-base`. The tokenizer
is downloaded from Hugging Face on first use and should match the embedding model
used later in the RAG pipeline.

## Run

From the repository root, provide the collection root and the repository's
reviewed corrections file:

```powershell
python .\data_pipeline\chunk\create-chunks.py `
  --root "C:\path\to\Knowledge Database" `
  --corrections .\data_pipeline\chunk\corrections.json
```

The defaults are a 350-token final limit and 10% overlap. HybridChunker itself
does not implement overlap, so the script reserves 35 tokens for the preceding
chunk and configures HybridChunker with a 315-token base budget. The final `text`
field never exceeds 350 tokenizer tokens.

Before writing chunks, the script checks for invalid PDF control characters.
High-confidence NUL characters occurring between mathematical/text tokens are
converted to `-` and recorded in `quality_report.json`. Chunks containing other
ambiguous controls are excluded from `chunks.jsonl` and described in
`quarantine.jsonl` rather than being silently altered or embedded.
The terminal identifies papers requiring review and prints the corresponding
report paths after each paper is processed.

`corrections.json` contains document-scoped replacements that were manually
verified against source PDF pages. Keep it beside `create-chunks.py`; applied
and unmatched corrections are audited in each `quality_report.json`. Add a new
entry only after checking the original PDF—unknown controls will continue to be
quarantined instead of guessed.

Options can be changed explicitly:

```powershell
python .\data_pipeline\chunk\create-chunks.py `
  --root "C:\path\to\Knowledge Database" `
  --corrections .\data_pipeline\chunk\corrections.json `
  --max-tokens 350 --overlap-percent 10
```

To regenerate only selected papers, repeat `--record` with the filesystem-safe
`paper_id`/filename stem:

```powershell
python .\data_pipeline\chunk\create-chunks.py `
  --root "C:\path\to\Knowledge Database" `
  --corrections .\data_pipeline\chunk\corrections.json `
  --record 10.1016j.apenergy.2024.124538
```

The script can also be invoked by absolute path from another directory:

```powershell
python "C:\path\to\repository\data_pipeline\chunk\create-chunks.py" `
  --root "C:\path\to\Knowledge Database" `
  --corrections "C:\path\to\repository\data_pipeline\chunk\corrections.json"
```

## Chunk record fields

Each line in `chunks.jsonl` is one JSON object containing:

- `chunk_id`, `record_id`, and `chunk_index` for addressing and filtering.
- `paper_id` in the per-paper manifest and quality report for the local source
  filename/directory association.
- `text`: the final context-enriched, overlapped text intended for embedding.
- `content_text`: Docling's original chunk body.
- `contextualized_text`: the body enriched by Docling with headings/captions.
- `overlap_text`: the preceding context added to `text`.
- `token_count` and `content_sha256` for validation and deduplication.
- `metadata`: Markdown YAML metadata plus page numbers and the complete native
  Docling chunk metadata.

Docling automatically supplies structural chunk metadata, headings, captions,
and provenance through `chunk.meta` and `HybridChunker.contextualize()`. It does
not know about the custom YAML front matter added to the Markdown export, so this
script reads the matching Markdown file and merges that metadata into every
chunk record.
