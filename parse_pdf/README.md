# Docling PDF Converter

`docling-convert.py` converts journal-article PDFs into Markdown using [Docling](https://docling-project.github.io/docling/).

It is designed for a Knowledge Base folder containing PDF files.

## Setup

1. Copy `docling-convert.py` into the top level of your Knowledge Base folder.

2. Open an Anaconda Prompt or PowerShell with Conda enabled.

3. Install Docling if needed:
   ```
   python -m pip install docling
   ```

4. Change into the Knowledge Base folder:
   ```
   cd "C:\path\to\Knowledge Database"
   ```

##  Basic conversion

Convert every PDF in the Knowledge Base folder and its subfolders:
```
python docling-convert.py
```
## Output folders

The converter creates these folders as needed:
```
Knowledge Database/
├── docling-convert.py
├── article-1.pdf
├── article-2.pdf
├── MD_Files/
│   ├── trentadue_2018.md
│   └── smith_2024.md
└── Image_Files/              # Created only with --export-images
    └── trentadue_2018/
        ├── figure_001.png
        ├── table_001.png
        └── manifest.json
```

Each Markdown file begins with YAML metadata, including:
- paper_id — derived as primary-author-last-name_publication-year
- title and raw author string
- publication year/date, when detected
- DOI, when detected
- source PDF path, file size, and SHA-256 checksum
- page count
- Docling version and parsing timestamp
- whether formula enrichment was used

Example output filename:
```
MD_Files/trentadue_2018.md
```
If two papers have the same primary-author surname and publication year, the converter adds a short source-hash suffix to the filename to prevent overwriting a paper.

## Re-run conversion

By default, an existing output file is preserved.

To recreate and replace existing Docling Markdown files:
```
python docling-convert.py --force
```

## Export figures and tables

Export detected figure and table crops as PNG files, with a metadata manifest:
```
python docling-convert.py --export-images --force
```
Images are saved in:
```
Image_Files/<paper_id>/
```
The accompanying manifest.json records each image's ID, type, filename, checksum, page number, bounding box, and caption when available.

Increase or decrease image resolution with --image-scale:
```
python docling-convert.py --export-images --image-scale 1 --force
```
1 is approximately 72 DPI; the default value is 2 (approximately 144 DPI).

## Formula enrichment

For papers where mathematical equations are important, enable Docling's formula-enrichment model:
```
python docling-convert.py --enrich-formulas --force
```
This attempts to convert detected formulas into LaTeX. It downloads and runs an additional model, so it can be substantially slower and use more memory. Use it selectively for formula-heavy papers.

Formula enrichment can be combined with figure/table export:
```
python docling-convert.py --enrich-formulas --export-images --force
```
Notes
- The original PDFs are never modified.
- Markdown is intended for inspection and downstream RAG chunking.
- Some PDFs may contain repeated headers, footers, hidden text, or OCR artifacts. Keep raw Docling output and apply any cleanup as a separate step.
- For RAG, retain the Markdown front matter and later add chunk-level metadata such as section path, page range, and element type.
