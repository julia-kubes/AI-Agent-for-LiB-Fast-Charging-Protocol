# Docling Chunk Creator

`create-chunks.py` creates RAG-ready chunks from the lossless Docling JSON files
produced by `parse_pdf/docling-convert.py`.

## Input and output layout

Place the script in the collection root beside `Docling_Files` and `MD_Files`:

```text
Knowledge Database/
├── create-chunks.py
├── Docling_Files/
│   └── smith_2024.json
├── MD_Files/
│   └── smith_2024.md
└── chunk_files/
    └── smith_2024/
        ├── chunks.jsonl
        ├── quarantine.jsonl
        ├── quality_report.json
        └── manifest.json
```

One JSONL file per paper is preferable to one file per chunk: it avoids creating
thousands of tiny files while retaining independent, replaceable paper outputs.
Chunk IDs use `<record_id>::chunk::<zero-padded index>`, for example
`smith_2024::chunk::0001`. Each record also includes a SHA-256 content hash.

## Setup

Use the same environment as the PDF converter and install the chunking/tokenizer
dependencies if needed:

```powershell
python -m pip install "docling-core[chunking]" transformers
```

The default tokenizer is `Alibaba-NLP/gte-modernbert-base`. The tokenizer
is downloaded from Hugging Face on first use and should match the embedding model
used later in the RAG pipeline.

## Run

From the Knowledge Database folder:

```powershell
python create-chunks.py
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

Options can be changed explicitly:

```powershell
python create-chunks.py --max-tokens 350 --overlap-percent 10
```

When running the repository copy from another directory, specify the collection:

```powershell
python create-chunks.py --root "C:\path\to\Knowledge Database"
```

## Chunk record fields

Each line in `chunks.jsonl` is one JSON object containing:

- `chunk_id`, `record_id`, and `chunk_index` for addressing and filtering.
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
