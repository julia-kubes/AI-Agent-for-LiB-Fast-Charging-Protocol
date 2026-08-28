# Retrieve and rerank battery-literature chunks

`retrieval.py` runs a two-stage retrieval pipeline over the PostgreSQL/pgvector
database created by `embedding/embed-and-store.py`:

1. Embed a plain-language query with `Alibaba-NLP/gte-modernbert-base`.
2. Retrieve the 30 nearest chunks using pgvector cosine distance.
3. Score each query-chunk pair with
   `Alibaba-NLP/gte-reranker-modernbert-base`.
4. Return the eight highest-scoring chunks.

The script is read-only. It does not update database rows or stored embeddings.

## Requirements

- Python 3.10 or newer
- A PostgreSQL/Neon database containing `public.rag_chunks`
- The pgvector extension and 768-dimensional GTE embeddings
- `public.paper_metadata`, keyed by `record_id`
- Internet access on the first run to download the embedding and reranking
  models

The dependencies are shared with the embedding pipeline. From the repository
root, create or activate the environment described in `embedding/README.md`,
then install:

```powershell
python -m pip install -r .\embedding\requirements.txt
```

The first run downloads both GTE models from Hugging Face. Subsequent runs use
the local model cache. CUDA is optional; inference falls back to CPU.

## Database connection

Copy the connection string from the Neon **Connect** dialog and set it only in
the terminal session that will run retrieval:

```powershell
$env:DATABASE_URL = "postgresql://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require"
```

Do not put the connection string or password in source files or commit them to
Git.

## Basic usage

From the `retrieval` directory:

```powershell
python .\retrieval.py "Fast-charge protocol for LFP cells in 25 C ambient temperature"
```

The default funnel is vector top-30, followed by reranker top-8. Each result
shows:

- reranker rank and score;
- original vector rank and cosine similarity;
- chunk and paper identifiers;
- page numbers and Docling section headings;
- chemistry, manufacturer, and form factor from `paper_metadata`;
- a text preview.

Reranker scores are useful for ordering candidates but are not calibrated
probabilities. A score of `0.8` should not be interpreted as 80% confidence.

## Source diversity

By default, relevance alone determines the final ranking, so several chunks
from the same highly relevant paper may appear. Optionally cap the number of
results contributed by one paper:

```powershell
python .\retrieval.py `
  "Fast-charge protocol for LFP cells in 25 C ambient temperature" `
  --max-per-paper 2
```

The cap is applied after all 30 candidates are reranked. It can broaden the
evidence base, but it may remove legitimately relevant passages. Compare
constrained and unconstrained runs during evaluation.

## JSON output for evaluation

Use `--json` for machine-readable output:

```powershell
python .\retrieval.py "your evaluation query" --json
```

To retain the complete reranked candidate pool for calculating retrieval
metrics, return all 30 candidates:

```powershell
python .\retrieval.py "your evaluation query" --top-k 30 --json
```

Each JSON result contains `vector_rank`, `vector_similarity`,
`reranker_rank`, and `reranker_score`. This allows the same candidate pool to
be evaluated in both vector and reranked order.

Useful evaluation metrics include:

- Recall@30 for initial vector candidate coverage;
- nDCG@8 for graded ranking quality;
- Precision@8 and Hit Rate@8;
- Mean Reciprocal Rank@8;
- distinct papers represented in the top eight;
- redundant evidence in the top eight.

## Options

Display all command-line options:

```powershell
python .\retrieval.py --help
```

Common options:

| Option | Default | Purpose |
|---|---:|---|
| `--candidates` | 30 | Number of chunks retrieved by pgvector |
| `--top-k` | 8 | Number of reranked chunks returned |
| `--max-per-paper` | none | Optional per-paper diversity cap |
| `--batch-size` | 16 | Reranker inference batch size |
| `--max-length` | 1024 | Query-plus-chunk reranker token limit |
| `--device` | automatic | Force `cpu`, `cuda`, or another supported device |
| `--json` | off | Return structured JSON |

For a lower-memory CPU run:

```powershell
python .\retrieval.py "your query" --device cpu --batch-size 4
```

`--top-k` cannot exceed `--candidates`.

## Vector-only baseline

`embedding/embed-and-store.py --query` provides an independent vector-only
baseline:

```powershell
python .\embedding\embed-and-store.py `
  --query "Fast-charge protocol for LFP cells in 25 C ambient temperature" `
  --top-k 8
```

For the fairest reranking comparison, use `retrieval.py --top-k 30 --json` and
reconstruct vector order using `vector_rank`. Both rankings will then use the
same 30 candidates.

## Section headings

The script reads section information already stored in each chunk at:

```text
metadata.docling.headings
```

Missing headings are displayed as `n/s`. Showing headings does not require
rechunking or re-embedding.

## Troubleshooting

- **`DATABASE_URL is not set`**: set it in the same terminal session before
  running the script.
- **`Vector retrieval failed: relation "paper_metadata" does not exist`**:
  import the reviewed paper metadata into `public.paper_metadata`.
- **No candidate chunks found**: confirm that the `embedding_model` stored in
  `rag_chunks` is `Alibaba-NLP/gte-modernbert-base`.
- **Out of memory**: reduce `--batch-size`, use `--device cpu`, or reduce
  `--max-length`.
- **Model download failure**: verify Hugging Face access and rerun; partial
  downloads are normally recoverable through the model cache.
- **Only one or two papers dominate**: inspect relevance first, then compare
  against `--max-per-paper 2`.
