# Embed and store Docling chunks

`embed-and-store.py` validates the JSONL files produced by `create-chunks.py`,
embeds each chunk's `text` field with
`Alibaba-NLP/gte-modernbert-base`, and upserts the results into PostgreSQL with
pgvector. The script also provides a plain-English command-line query for visual
verification.

The model produces 768-dimensional, normalized embeddings. The script stores
the original chunk fields, source/page metadata, and a `vector(768)` value. A
chunk's stable `chunk_id` is the primary key, so rerunning the script updates
existing rows instead of creating duplicates.

## Prerequisites

- Python 3.10 or newer
- An existing PostgreSQL database with pgvector already enabled
- A database user with permission to create tables and indexes
- Internet access on the first run to download the embedding model (about 149M
  parameters)

## 1. Create and activate a Python environment

From PowerShell in the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\data_pipeline\embedding\requirements.txt
```

`requirements.txt` installs Sentence Transformers, Transformers, PyTorch,
Psycopg, and the pgvector Python adapter. On the first embedding run, Sentence
Transformers downloads `Alibaba-NLP/gte-modernbert-base` automatically; the
model does not need to be downloaded manually.

CUDA is optional. Sentence Transformers will use a supported GPU automatically;
otherwise it runs on CPU. Force CPU mode with `--device cpu` if needed.

## 2. Set the connection URL

Provide the connection only in the PowerShell session that will run the script:

```powershell
$env:DATABASE_URL = "postgresql://USERNAME:URL_ENCODED_PASSWORD@HOST:PORT/DATABASE_NAME"
```

Keep credentials out of source files and Git. If a password contains URL-special
characters, URL-encode it before placing it in the connection URL. Do not put a
real password in this README. This environment variable lasts only for the
current PowerShell session.

## 3. Optional: validate chunks without embedding

This preflight check catches malformed JSON, missing fields, empty text, and
duplicate chunk IDs without downloading the model or changing the database:

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files" `
  --dry-run
```

This step is optional because the same validation runs automatically before
every actual embedding run.

## 4. Embed and store the chunks

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files"
```

The script now finishes embedding and saves `embedding_cache.npz` before it
opens the PostgreSQL connection. If Neon or the network disconnects during
storage, retry only the fast upload step:

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files" `
  --store-only
```

You can also run the two stages explicitly:

```powershell
python .\data_pipeline\embedding\embed-and-store.py --chunks-root "C:\path\to\Knowledge Database\chunk_files" --embed-only
python .\data_pipeline\embedding\embed-and-store.py --chunks-root "C:\path\to\Knowledge Database\chunk_files" --store-only
```

The cache records the model, chunk IDs, and content hashes. `--store-only`
refuses to upload if the chunk files changed after the cache was created; in
that case, run `--embed-only` again. The cache is a generated local file and
should not be committed to Git.

Rerun this command after the parsing and chunking pipeline produces new or
updated chunk files. Existing chunk IDs are updated and new chunk IDs are added,
so the database is not filled with duplicate copies.

The terminal displays:

- the number of validated chunks and input files;
- a Sentence Transformers embedding progress bar;
- the number of rows stored;
- a final database row/dimension verification result.

The default batch size is 16. For limited memory, reduce it:

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --chunks-root "C:\path\to\Knowledge Database\chunk_files" `
  --batch-size 4 --device cpu
```

The default table is `public.rag_chunks`. Use `--schema` and `--table` to choose
different names. The script creates an HNSW cosine-distance index after loading;
use `--skip-index` when testing exact search or when you plan to create the index
separately.

## 5. Query in plain English

No SQL is required for routine verification:

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --query "How does low temperature affect fast charging?" --top-k 5
```

Optionally limit results to one source:

```powershell
python .\data_pipeline\embedding\embed-and-store.py `
  --query "What charging protocol was evaluated?" `
  --record-id guo_2014 `
  --top-k 5
```

Each result displays cosine similarity, chunk ID, title, page numbers, and a text
preview.

## Direct SQL checks (optional)

If `psql` is installed:

```powershell
psql $env:DATABASE_URL
```

At the `psql` prompt:

```sql
SELECT COUNT(*) FROM public.rag_chunks;

SELECT
    record_id,
    COUNT(*) AS chunks,
    MIN(vector_dims(embedding)) AS dimensions,
    MAX(vector_dims(embedding)) AS dimensions_check
FROM public.rag_chunks
GROUP BY record_id
ORDER BY record_id;

SELECT chunk_id, metadata->>'title' AS title, page_numbers
FROM public.rag_chunks
LIMIT 5;
```

Exit with `\q`.

## What is stored

The table includes:

- stable chunk and document identifiers;
- embedding text plus the original/contextualized text fields;
- token count and content hash;
- complete Docling/document metadata as `JSONB`;
- page numbers as an integer array;
- embedding model and dimension information;
- the normalized pgvector embedding;
- an update timestamp.

The script does not delete database rows for chunks removed from the filesystem.
Deletion should be an explicit, reviewed operation.

## Troubleshooting

- **`DATABASE_URL is not set`**: set it in the same terminal session before
  running the script.
- **Cannot enable extension**: ask the database administrator to run
  `CREATE EXTENSION vector` in the target database.
- **Connection refused**: confirm PostgreSQL is running and that `HOST` and
  `PORT` in `DATABASE_URL` are correct.
- **SSL connection closed unexpectedly**: the completed embeddings remain in
  `embedding_cache.npz`; restore the connection and run `--store-only`.
- **Out of memory**: use a smaller `--batch-size` and `--device cpu`.
- **Dimension mismatch**: keep one embedding model per vector column/index. A
  different model may require a new table or migration.
- **Model download failure**: verify access to Hugging Face and rerun; downloaded
  files are cached locally.
