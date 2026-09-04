# Docling PDF Converter

`docling-convert.py` converts journal-article PDFs into Markdown using [Docling](https://docling-project.github.io/docling/). It is designed for a Knowledge Base folder containing PDFs and a `battery_paper_metadata.csv` table.

## Metadata-first workflow

Keep the PDFs, metadata CSV, and generated folders together in one collection
directory. Prepare each paper's metadata *before* parsing:

1. Add a row to `battery_paper_metadata.csv` with the verified paper title and canonical DOI. Leave fields that you will fill from parsed text blank for now.
2. Make a Windows-safe filename ID from the DOI by removing or replacing `/` consistently, then name the PDF with that ID. Example:

   ```
   DOI in CSV:   10.1016/j.apenergy.2024.124538
   PDF filename: 10.1016j.apenergy.2024.124538.pdf
   ```

3. Set both `doi` and `record_id` in the CSV to the canonical DOI, including its
   slash: `10.1016/j.apenergy.2024.124538` in this example.

The converter deliberately does **not** extract or infer a DOI from PDF text. It
normalizes punctuation only while matching the PDF filename to the CSV DOI. The
filename stem becomes the filesystem-safe `paper_id`; the matched CSV DOI becomes
the canonical `record_id` and `doi`. If a PDF cannot be matched uniquely, the
converter reports an error instead of creating a record with a guessed ID.

## Setup

1. Put `docling-convert.py` and `battery_paper_metadata.csv` in the collection
   folder with the PDFs, or use `--root` when running the repository copy.
2. Open an Anaconda Prompt or PowerShell with Conda enabled.
3. Install Docling if needed:

   ```
   python -m pip install docling
   ```

4. Change to the Knowledge Base folder:

   ```
   cd "C:\path\to\Knowledge DB 3"
   ```

## Basic conversion

```
python docling-convert.py
```

For the filename above, the converter creates:

```
MD_Files/10.1016j.apenergy.2024.124538.md
Docling_Files/10.1016j.apenergy.2024.124538.json
```

The generated Markdown front matter includes:

```yaml
paper_id: 10.1016j.apenergy.2024.124538
record_id: 10.1016/j.apenergy.2024.124538
doi: 10.1016/j.apenergy.2024.124538
```

The authoritative DOI is the value in `battery_paper_metadata.csv`. Chunks use
the DOI, for example `10.1016/j.apenergy.2024.124538::chunk::0001`.

The default collection root is the current working directory, so the basic
command contains no machine-specific path. To run the repository copy without
copying it into the collection folder, use:

```powershell
python path\to\docling-convert.py --root .
```

To use a differently named CSV inside the collection root:

```powershell
python docling-convert.py --metadata-csv my_metadata.csv
```

## Re-run conversion

Existing outputs are identified by source-PDF path and SHA-256 fingerprint and are skipped by default. To deliberately recreate an existing paper's Markdown and JSON:

```
python docling-convert.py --force
```

## Export figures and tables

```
python docling-convert.py --export-images --force
```

Images are saved in `Image_Files/<paper_id>/`; the accompanying `manifest.json`
includes both the filesystem-safe `paper_id` and DOI-based `record_id`, plus each
image's ID, type, checksum, page number, bounding box, and caption when available.
Set rendering resolution with `--image-scale` (`1` is about 72 DPI; default is `2`).

## End-to-end workflow

For new papers, follow this order:

1. Add and verify the paper's DOI and title in `battery_paper_metadata.csv`; set
   `record_id` equal to the DOI.
2. Name the PDF with a filesystem-safe form of that DOI.
3. Run `python docling-convert.py` to create DOI-linked Markdown and Docling JSON.
4. Run `python create-chunks.py` to create chunks whose `record_id` and
   `chunk_id` use the DOI.
5. Run the embedding/storage script.
6. Run `python import-paper-metadata.py` after the chunks exist in PostgreSQL.

With this workflow, `migrate-record-ids-to-dois.py` is not needed for newly
processed papers. It is only a repair tool for records produced by an older
version of the pipeline.

## Formula enrichment

```
python docling-convert.py --enrich-formulas --force
```

Formula enrichment tries to convert recognized formulas into LaTeX and can be much slower, so use it selectively.

## Notes

- Original PDFs are never modified.
- Markdown is intended for inspection and downstream RAG chunking.
- Some PDFs contain repeated headers, footers, hidden text, or OCR artifacts. Keep raw Docling output and apply cleanup separately.
