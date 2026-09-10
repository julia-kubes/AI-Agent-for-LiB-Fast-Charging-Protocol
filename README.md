# AI Agent for Li-ion Battery Fast-Charging Protocols

This branch contains the application, retrieval code, evaluation assets, tests,
and the complete pipeline used to build the literature vector database.

## Repository organization

```text
app/                         Streamlit UI, agent, prompts, and app adapters
data_pipeline/
├── parse_pdf/               Convert source PDFs to Markdown and Docling JSON
├── chunk/                   Create reviewed, RAG-ready JSONL chunks
├── embedding/               Embed chunks and store them in PostgreSQL/pgvector
└── metadata/                Import curated paper metadata
retrieval/                   Shared runtime vector retrieval and reranking
evaluation/                  Evaluation queries, runners, and results
tests/                       Offline application and retrieval tests
```

`retrieval/` remains at the repository root because the running application
imports it directly. The scripts that create or populate the database are
grouped under `data_pipeline/`.

## Python environment

From the repository root, create and activate a virtual environment and install
the application and retrieval dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-app.txt
```

PDF parsing and chunk creation also require Docling. It is intentionally
installed separately because users who only run the application do not need the
document-processing dependency:

```powershell
python -m pip install docling
```

Without Docling, the embedding script can display `--help`, but the parsing and
chunking scripts stop during import with `ModuleNotFoundError`.

## Vector database workflow

The source collection is separate from this repository. It contains PDFs,
`battery_paper_metadata.csv`, and generated directories such as
`Docling_Files/`, `MD_Files/`, and `chunk_files/`.

From the repository root, process a collection in this order:

```powershell
# 1. Convert PDFs to Markdown and lossless Docling JSON.
python .\data_pipeline\parse_pdf\docling-convert.py `
  --root "C:\path\to\Knowledge Database"

# 2. Create RAG-ready chunks.
python .\data_pipeline\chunk\create-chunks.py `
  --root "C:\path\to\Knowledge Database" `
  --corrections .\data_pipeline\chunk\corrections.json

# 3. Validate, embed, and store the chunks.
python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files" `
  --dry-run

python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files"
```

The metadata importer currently reads
`data_pipeline/metadata/battery_paper_metadata.csv`. Copy the reviewed CSV to
that location before running:

```powershell
python .\data_pipeline\metadata\import-paper-metadata.py
```

Set `DATABASE_URL` in the same terminal before database storage, metadata
import, or live retrieval. Never commit database credentials or a populated
`.env` file.

See the component documentation for details:

- [PDF conversion](data_pipeline/parse_pdf/README.md)
- [Chunk creation](data_pipeline/chunk/README.md)
- [Embedding and storage](data_pipeline/embedding/README.md)
- [Retrieval and reranking](retrieval/README.md)

Collection files are resolved from the current folder or an explicit `--root`,
so the workflow does not depend on a particular user's directory layout.
