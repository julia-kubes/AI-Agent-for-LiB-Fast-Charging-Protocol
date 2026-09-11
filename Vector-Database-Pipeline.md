# Vector Database Pipeline

The pipeline converts source PDFs into structured documents, creates reviewed
chunks, embeds those chunks, and stores them in PostgreSQL with pgvector. These
instructions assume Windows PowerShell and Python 3.11.

This pipeline can be completed from either branch: `literature-synthesis` or `protocol-generation`

For script-specific options, consult:

- `data_pipeline\parse_pdf\README.md`
- `data_pipeline\chunk\README.md`
- `data_pipeline\embedding\README.md`

The instructions below describe the overall workflow and common problems.

## 1. Create a separate source collection

Keep the research papers and generated data outside the Git repository. For
example:

```powershell
New-Item -ItemType Directory -Path "C:\Research\Knowledge Database"
```

The collection will eventually have this structure:

```text
Knowledge Database\
├── battery_paper_metadata.csv
├── paper PDFs
├── Docling_Files\
├── MD_Files\
└── chunk_files\
```

The scripts create the generated folders automatically. Original PDFs are not
modified.

## 2. Download the pipeline files and dependencies

Download or clone either supported application branch. The necessary scripts
are included under:

```text
data_pipeline\
├── parse_pdf\
├── chunk\
├── embedding\
└── metadata\
```

From the repository root, install the application dependencies and Docling:

```powershell
py -3.11 -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements-app.txt
python -m pip install docling
```

Copy the PDFs being processed into the separate collection folder, not into the
Git repository. Docling, tokenizer models, and embedding models may require
internet access during their first use.

## 3. Prepare and update paper metadata

This step must be completed *before* parsing begins to ensure the record_id is parsed and saved to the database correctly. 
Updating the metadata.csv with DOI and paper title is essential for the LLM to cite its sources.

Copy the current metadata file from:

```text
data_pipeline\metadata\battery_paper_metadata.csv
```

Place a working copy named `battery_paper_metadata.csv` in the source collection
alongside the PDFs. Before parsing each paper:

1. Verify its title and canonical DOI.
2. Add or update its row in the metadata CSV.
3. Set both `doi` and `record_id` to the canonical DOI, including the slash.
4. Rename the PDF using a Windows-safe version of the DOI.

For example:

```text
Canonical DOI: 10.1016/j.apenergy.2024.124538
PDF filename:  10.1016j.apenergy.2024.124538.pdf
```

The PDF filename must correspond uniquely to the DOI in the metadata file. Do
not invent a DOI or derive one solely from potentially inaccurate PDF text.

## 4. Parse the PDFs

From the Git repository root:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\parse_pdf\docling-convert.py" `
  --root "C:\Research\Knowledge Database"
```

This creates Markdown files in `MD_Files` and structured Docling JSON files in
`Docling_Files`.

If a PDF cannot be matched to the metadata, check the PDF filename, DOI,
`record_id`, duplicate rows, and missing or extra DOI characters. Rename the PDF
or correct the metadata and rerun the script. Successfully processed files are
normally skipped; consult the parsing README before using options such as
`--force`.

## 5. Create chunks

Run:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\chunk\create-chunks.py" `
  --root "C:\Research\Knowledge Database" `
  --corrections ".\data_pipeline\chunk\corrections.json"
```

The script creates one directory per paper under `chunk_files`. Typical outputs
include:

```text
chunks.jsonl
quarantine.jsonl
quality_report.json
manifest.json
```

The tokenizer downloads automatically during its first use and should match the
embedding model used later.

## 6. Review quarantined chunks

A chunk is quarantined when its source contains ambiguous control characters,
OCR artifacts, or corrupted text that cannot be corrected safely and
automatically. Quarantining prevents questionable text from entering the vector
database and affecting retrieval or generated answers.

For every paper flagged by the script:
(*NOTE*: note you may use agentic workflows to complete this task for you)
1. Open its `quality_report.json` and `quarantine.jsonl`.
2. Compare the questionable text against the original PDF 
3. If the correct text can be verified, add a document-specific correction to
   `data_pipeline\chunk\corrections.json`.
4. Rerun chunking for the affected paper.
5. If the correct text cannot be verified, leave that material quarantined and
   excluded.

Do not guess replacements. Quarantined chunks are excluded from `chunks.jsonl`
and therefore will not be embedded. See the chunking README for the corrections
format and the command for rerunning an individual record.

## 7. Validate, embed, and store the chunks

Set the database URL in the same PowerShell window:

```powershell
$env:DATABASE_URL = "(paste Database URL from Neon here)"
```

This variable lasts only for the current PowerShell session.

To obtain the URL from Neon:
1. Log into you Neon account and navigate to the "AI Charging RAG Project"
2. Click "Connect"
3. Copy the connection string

Validate the chunks before embedding:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\embedding\embed-and-store.py" `
  --chunks-root "C:\Research\Knowledge Database\chunk_files" `
  --dry-run
```

For a normal embedding and upload:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\embedding\embed-and-store.py" `
  --chunks-root "C:\Research\Knowledge Database\chunk_files"
```

For a large collection, separate the time-consuming embedding operation from
database storage:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\embedding\embed-and-store.py" `
  --chunks-root "C:\Research\Knowledge Database\chunk_files" `
  --embed-only
```

After embedding finishes:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\embedding\embed-and-store.py" `
  --chunks-root "C:\Research\Knowledge Database\chunk_files" `
  --store-only
```

This creates a local embedding cache before upload. If the database connection
fails during storage, restore the connection and rerun `--store-only`; the
documents do not need to be embedded again. If the chunks change, rerun
`--embed-only` before using `--store-only`.

## 8. Import the updated paper metadata

Make sure all fields in the metadata are filled (you can use an agentic workflow to fill in the remaining fields. It is VERY important to paste the DOI by hand however, the parsing script is not robust to obtaining the correct DOI). 

After reviewing the collection's metadata, copy the updated CSV into:

```text
data_pipeline\metadata\battery_paper_metadata.csv
```

With `DATABASE_URL` still active, run:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\data_pipeline\metadata\import-paper-metadata.py"
```

Preserve the reviewed CSV as the authoritative metadata record. Before
contributing it to GitHub, confirm that it contains no confidential information.

## General troubleshooting

- **`ModuleNotFoundError: docling` or `docling_core`:** Install Docling in the
  same virtual environment used to run the script.
- **Metadata matching failure:** Verify the DOI, `record_id`, PDF filename, and
  duplicate rows.
- **Model download failure:** Confirm internet and Hugging Face access, then
  rerun the command.
- **Out-of-memory error:** Reduce the embedding batch size and use CPU mode.
- **Database connection error:** Verify `DATABASE_URL`, database availability,
  SSL settings, and credentials.
- **`DATABASE_URL is not set`:** Set it again in the same PowerShell window.
- **Storage interruption:** Retain `embedding_cache.npz` and retry with
  `--store-only`.
- **Unexpected parsing or chunking behavior:** Stop and consult the relevant
  component README before forcing regeneration or modifying generated files.
