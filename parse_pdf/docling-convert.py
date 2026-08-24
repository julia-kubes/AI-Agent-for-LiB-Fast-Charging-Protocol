"""Convert every PDF in this collection to Markdown with Docling.

Usage (from this folder, in the Conda environment with Docling installed):
    python docling-convert.py

Outputs are written beside the GROBID previews without overwriting them:
    MD_Files/trentadue_2018.md
    MD_Files/smith_2024.md

Use --force to replace existing Docling Markdown files.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from docling_core.types.doc import PictureItem, TableItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter
from docling.document_converter import PdfFormatOption


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "MD_Files"
IMAGE_DIR = ROOT / "Image_Files"
EXCLUDED_DIR_NAMES = {"MD_Files", "XML_Files"}


def find_pdfs() -> list[Path]:
    """Find collection PDFs recursively, excluding generated-output folders."""
    return sorted(
        (
            path
            for path in ROOT.rglob("*.pdf")
            if not any(parent.name in EXCLUDED_DIR_NAMES for parent in path.parents)
        ),
        key=lambda path: str(path.relative_to(ROOT)).lower(),
    )


def sha256(path: Path) -> str:
    """Return a content fingerprint for traceability and de-duplication."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nonempty_lines(markdown: str) -> list[str]:
    return [line.strip() for line in markdown.splitlines() if line.strip() and line.strip() != "<!-- image -->"]


def extract_metadata(
    markdown: str, pdf_path: Path, page_count: int | None, formula_enrichment: bool
) -> dict[str, object]:
    """Extract common scholarly metadata from Docling's Markdown, best-effort."""
    lines = nonempty_lines(markdown)
    title_index = next((i for i, line in enumerate(lines) if re.match(r"^#{1,6}\s+\S", line)), None)
    title = re.sub(r"^#{1,6}\s+", "", lines[title_index]).strip() if title_index is not None else pdf_path.stem

    authors_raw = ""
    if title_index is not None:
        for line in lines[title_index + 1 :]:
            if not line.startswith("#"):
                authors_raw = line
                break

    primary_author = authors_raw.split(",", maxsplit=1)[0]
    primary_author = re.sub(r"[*†‡\d]+", "", primary_author).strip()
    name_tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+", primary_author)
    primary_last_name = name_tokens[-1] if name_tokens else "unknown"
    primary_last_name = unicodedata.normalize("NFKD", primary_last_name).encode("ascii", "ignore").decode().lower()
    primary_last_name = re.sub(r"[^a-z0-9]+", "", primary_last_name) or "unknown"

    publication_date_match = re.search(r"(?:published|publication date)\s*:\s*([^;\n]+)", markdown, re.IGNORECASE)
    publication_date = publication_date_match.group(1).strip() if publication_date_match else None
    publication_match = re.search(r"\b((?:19|20)\d{2})\b", publication_date or "")
    year_match = publication_match or re.search(r"\b((?:19|20)\d{2})\b", markdown)
    publication_year = year_match.group(1) if year_match else "unknown"
    doi_match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", markdown, re.IGNORECASE)

    return {
        "paper_id": f"{primary_last_name}_{publication_year}",
        "title": title,
        "authors_raw": authors_raw or None,
        "primary_author_last_name": primary_last_name if primary_last_name != "unknown" else None,
        "publication_year": int(publication_year) if publication_year != "unknown" else None,
        "publication_date": publication_date,
        "doi": doi_match.group(1).rstrip(".,;)") if doi_match else None,
        "source_pdf": str(pdf_path.relative_to(ROOT)).replace("\\", "/"),
        "source_size_bytes": pdf_path.stat().st_size,
        "source_sha256": sha256(pdf_path),
        "page_count": page_count,
        "parser": "docling",
        "parser_version": importlib.metadata.version("docling"),
        "formula_enrichment": formula_enrichment,
        "parsed_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def yaml_front_matter(metadata: dict[str, object]) -> str:
    """Create dependency-free YAML front matter; JSON values are valid YAML."""
    fields = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    return f"---\n{fields}\n---\n\n"


def output_path_for(metadata: dict[str, object]) -> Path:
    """Keep the requested human-readable ID, adding a hash only on collisions."""
    paper_id = str(metadata["paper_id"])
    candidate = OUTPUT_DIR / f"{paper_id}.md"
    if not candidate.exists():
        return candidate

    existing = candidate.read_text(encoding="utf-8", errors="replace")[:2000]
    if f'source_sha256: "{metadata["source_sha256"]}"' in existing:
        return candidate
    return OUTPUT_DIR / f"{paper_id}_{str(metadata['source_sha256'])[:8]}.md"


def build_converter(
    export_images: bool, image_scale: float, enrich_formulas: bool
) -> DocumentConverter:
    """Configure only the optional Docling enrichments requested for this run."""
    if not export_images and not enrich_formulas:
        return DocumentConverter()

    options = PdfPipelineOptions()
    options.do_formula_enrichment = enrich_formulas
    options.images_scale = image_scale
    if export_images:
        options.generate_page_images = True
        options.generate_picture_images = True
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def provenance_for(element: object) -> list[dict[str, object]]:
    """Serialize page and bounding-box provenance without Docling internals."""
    records: list[dict[str, object]] = []
    for provenance in getattr(element, "prov", []):
        bbox = getattr(provenance, "bbox", None)
        records.append(
            {
                "page_no": getattr(provenance, "page_no", None),
                "bbox": {
                    key: getattr(bbox, key, None)
                    for key in ("l", "t", "r", "b", "coord_origin")
                }
                if bbox
                else None,
            }
        )
    return records


def export_images(document: object, metadata: dict[str, object], image_scale: float) -> None:
    """Save figure/table crops and a manifest that grounds them in the PDF."""
    paper_image_dir = IMAGE_DIR / str(metadata["record_id"])
    paper_image_dir.mkdir(parents=True, exist_ok=True)
    exported: list[dict[str, object]] = []
    counters = {"figure": 0, "table": 0}

    for element, _level in document.iterate_items():
        if isinstance(element, PictureItem):
            element_type = "figure"
        elif isinstance(element, TableItem):
            element_type = "table"
        else:
            continue

        image = element.get_image(document)
        if image is None:
            continue
        counters[element_type] += 1
        filename = f"{element_type}_{counters[element_type]:03d}.png"
        image_path = paper_image_dir / filename
        image.save(image_path, "PNG")
        try:
            caption = element.caption_text(document).strip() or None
        except Exception:
            caption = None

        exported.append(
            {
                "image_id": f"{metadata['record_id']}_{element_type}_{counters[element_type]:03d}",
                "paper_id": metadata["paper_id"],
                "record_id": metadata["record_id"],
                "element_type": element_type,
                "index": counters[element_type],
                "file": filename,
                "sha256": sha256(image_path),
                "caption": caption,
                "provenance": provenance_for(element),
            }
        )

    manifest = {
        "schema_version": 1,
        "paper_id": metadata["paper_id"],
        "record_id": metadata["record_id"],
        "source_pdf": metadata["source_pdf"],
        "parser": metadata["parser"],
        "parser_version": metadata["parser_version"],
        "image_scale": image_scale,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "images": exported,
    }
    (paper_image_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  Exported {len(exported)} figure/table image(s) to {paper_image_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace existing Docling Markdown files")
    parser.add_argument(
        "--export-images",
        action="store_true",
        help="export figure and table PNGs plus an Image_Files manifest",
    )
    parser.add_argument(
        "--enrich-formulas",
        action="store_true",
        help="decode recognized formulas to LaTeX (downloads and runs an additional model)",
    )
    parser.add_argument(
        "--image-scale",
        type=float,
        default=2.0,
        help="render scale for exported images; 1 is about 72 DPI (default: 2)",
    )
    args = parser.parse_args()

    pdfs = find_pdfs()
    if not pdfs:
        print(f"No PDFs found in {ROOT}")
        return 0

    OUTPUT_DIR.mkdir(exist_ok=True)
    converter = build_converter(args.export_images, args.image_scale, args.enrich_formulas)
    failures = 0

    for number, pdf_path in enumerate(pdfs, start=1):
        print(f"[{number}/{len(pdfs)}] Converting {pdf_path.name}")
        try:
            document = converter.convert(str(pdf_path)).document
            markdown = document.export_to_markdown()
            metadata = extract_metadata(
                markdown,
                pdf_path,
                len(getattr(document, "pages", {})),
                args.enrich_formulas,
            )
            output_path = output_path_for(metadata)
            metadata["record_id"] = output_path.stem
            if output_path.exists() and not args.force:
                print(f"  Skipping: {output_path.name} already exists (use --force to redo it).")
                continue
            output_path.write_text(yaml_front_matter(metadata) + markdown, encoding="utf-8")
            if args.export_images:
                export_images(document, metadata, args.image_scale)
            print(f"  Wrote {output_path.name}")
        except Exception as error:  # Keep processing the rest of a PDF collection.
            failures += 1
            print(f"  FAILED: {error}", file=sys.stderr)

    if failures:
        print(f"Finished with {failures} failure(s).", file=sys.stderr)
        return 1
    print(f"Done. Docling Markdown files are in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
