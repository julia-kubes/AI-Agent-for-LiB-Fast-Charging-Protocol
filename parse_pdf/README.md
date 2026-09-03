# Docling PDF Converter

`docling-convert.py` converts journal-article PDFs into Markdown using [Docling](https://docling-project.github.io/docling/). It is designed for a Knowledge Base folder containing PDFs and a `battery_paper_metadata.csv` table.

## Metadata-first workflow

Prepare each paper's metadata *before* parsing:

1. Add a row to `battery_paper_metadata.csv` with the verified paper title and canonical DOI. Leave fields that you will fill from parsed text blank for now.
2. Make a Windows-safe filename ID from the DOI by removing or replacing `/` consistently, then name the PDF with that ID. Example:

   ```
   DOI in CSV:   10.1016/j.apenergy.2024.124538
   PDF filename: 10.1016j.apenergy.2024.124538.pdf
   ```

3. Set the CSV's `record_id` to exactly the PDF filename without `.pdf`: `10.1016j.apenergy.2024.124538` in this example.

The converter deliberately does **not** extract or infer a DOI from PDF text. The filename stem becomes the `paper_id`, `record_id`, parsed Markdown filename, Docling JSON filename, image-folder name, and chunk-ID prefix. This keeps the parsing/chunking pipeline aligned with the curated metadata CSV and your database IDs.

## Setup

1. Copy `docling-convert.py` into the top level of the Knowledge Base folder.
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
record_id: 10.1016j.apenergy.2024.124538
doi: null
```

The authoritative DOI is the value in `battery_paper_metadata.csv`. Chunks use the same ID, for example `10.1016j.apenergy.2024.124538::chunk::0001`.

## Re-run conversion

Existing outputs are identified by source-PDF path and SHA-256 fingerprint and are skipped by default. To deliberately recreate an existing paper's Markdown and JSON:

```
python docling-convert.py --force
```

## Export figures and tables

```
python docling-convert.py --export-images --force
```

Images are saved in `Image_Files/<record_id>/`; the accompanying `manifest.json` includes each image's ID, type, checksum, page number, bounding box, and caption when available. Set rendering resolution with `--image-scale` (`1` is about 72 DPI; default is `2`).

## Formula enrichment

```
python docling-convert.py --enrich-formulas --force
```

Formula enrichment tries to convert recognized formulas into LaTeX and can be much slower, so use it selectively.

## Notes

- Original PDFs are never modified.
- Markdown is intended for inspection and downstream RAG chunking.
- Some PDFs contain repeated headers, footers, hidden text, or OCR artifacts. Keep raw Docling output and apply cleanup separately.