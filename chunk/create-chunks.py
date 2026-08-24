"""Create RAG-ready JSONL chunks from serialized Docling documents.

Expected collection layout (the script defaults to the directory containing it):

    Docling_Files/<record_id>.json
    MD_Files/<record_id>.md
    chunk_files/<record_id>/chunks.jsonl
    chunk_files/<record_id>/manifest.json

HybridChunker does not provide overlapping chunks directly. This script reserves
part of the final token budget for the tail of the preceding chunk, so the
default 350-token output contains up to 35 overlap tokens (10%).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from transformers import AutoTokenizer


EMBEDDING_MODEL = "Alibaba-NLP/gte-modernbert-base"
MAX_TOKENS = 350
OVERLAP_PERCENT = 10.0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def markdown_front_matter(path: Path) -> dict[str, Any]:
    """Read the converter's JSON-valued YAML front matter without PyYAML."""
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8", errors="replace") as file:
        if file.readline().strip() != "---":
            return {}
        metadata: dict[str, Any] = {}
        for line in file:
            if line.strip() == "---":
                return metadata
            key, separator, raw_value = line.partition(":")
            if not separator:
                continue
            try:
                metadata[key.strip()] = json.loads(raw_value.strip())
            except json.JSONDecodeError:
                metadata[key.strip()] = raw_value.strip()
    return {}


def page_numbers(value: Any) -> list[int]:
    """Collect page numbers recursively from Docling's chunk metadata."""
    found: set[int] = set()

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if key in {"page_no", "page_number"} and isinstance(child, int):
                    found.add(child)
                else:
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return sorted(found)


def trim_token_tail(text: str, token_count: int, tokenizer: Any) -> str:
    if token_count <= 0 or not text:
        return ""
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    return tokenizer.decode(token_ids[-token_count:], skip_special_tokens=True).strip()


def combine_with_overlap(
    overlap_text: str,
    current_text: str,
    max_tokens: int,
    tokenizer: Any,
) -> tuple[str, str, int]:
    """Prepend as much overlap as fits while enforcing the final hard cap."""
    current_ids = tokenizer.encode(current_text, add_special_tokens=False)
    if len(current_ids) > max_tokens:
        current_ids = current_ids[:max_tokens]
        current_text = tokenizer.decode(current_ids, skip_special_tokens=True).strip()

    available = max_tokens - len(current_ids)
    used_overlap = trim_token_tail(overlap_text, available, tokenizer)
    combined = f"{used_overlap}\n\n{current_text}" if used_overlap else current_text
    combined_ids = tokenizer.encode(combined, add_special_tokens=False)

    # Tokenizer cleanup around the join can occasionally add a token.
    while used_overlap and len(combined_ids) > max_tokens:
        used_ids = tokenizer.encode(used_overlap, add_special_tokens=False)[:-1]
        used_overlap = tokenizer.decode(used_ids, skip_special_tokens=True).strip()
        combined = f"{used_overlap}\n\n{current_text}" if used_overlap else current_text
        combined_ids = tokenizer.encode(combined, add_special_tokens=False)

    return combined, used_overlap, len(combined_ids)


def json_safe(value: Any) -> Any:
    """Convert Pydantic metadata and other supported objects to JSON values."""
    if hasattr(value, "export_json_dict"):
        return value.export_json_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def chunk_document(
    docling_path: Path,
    markdown_dir: Path,
    output_dir: Path,
    chunker: HybridChunker,
    raw_tokenizer: Any,
    max_tokens: int,
    overlap_tokens: int,
    model_id: str,
) -> int:
    record_id = docling_path.stem
    markdown_path = markdown_dir / f"{record_id}.md"
    document_metadata = markdown_front_matter(markdown_path)
    document_metadata.setdefault("record_id", record_id)

    document = DoclingDocument.load_from_json(docling_path)
    chunks = list(chunker.chunk(document))
    records: list[dict[str, Any]] = []
    previous_text = ""

    for index, chunk in enumerate(chunks, start=1):
        content_text = chunk.text
        contextualized_text = chunker.contextualize(chunk=chunk)
        requested_overlap = trim_token_tail(previous_text, overlap_tokens, raw_tokenizer)
        embedding_text, used_overlap, token_count = combine_with_overlap(
            requested_overlap,
            contextualized_text,
            max_tokens,
            raw_tokenizer,
        )
        docling_metadata = json_safe(chunk.meta)
        chunk_id = f"{record_id}::chunk::{index:04d}"
        records.append(
            {
                "schema_version": 1,
                "chunk_id": chunk_id,
                "record_id": record_id,
                "chunk_index": index,
                "text": embedding_text,
                "content_text": content_text,
                "contextualized_text": contextualized_text,
                "overlap_text": used_overlap or None,
                "token_count": token_count,
                "content_sha256": sha256_bytes(embedding_text.encode("utf-8")),
                "metadata": {
                    **document_metadata,
                    "page_numbers": page_numbers(docling_metadata),
                    "docling": docling_metadata,
                },
            }
        )
        previous_text = content_text

    paper_dir = output_dir / record_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(paper_dir / "chunks.jsonl", records)
    write_json(
        paper_dir / "manifest.json",
        {
            "schema_version": 1,
            "record_id": record_id,
            "source_docling_json": str(docling_path),
            "source_docling_sha256": sha256_file(docling_path),
            "source_markdown": str(markdown_path) if markdown_path.exists() else None,
            "source_markdown_sha256": sha256_file(markdown_path) if markdown_path.exists() else None,
            "embedding_model": model_id,
            "max_tokens": max_tokens,
            "overlap_tokens": overlap_tokens,
            "chunk_count": len(records),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )
    return len(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="collection root containing Docling_Files and MD_Files (default: script folder)",
    )
    parser.add_argument("--model", default=EMBEDDING_MODEL, help="Hugging Face tokenizer/model ID")
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    parser.add_argument("--overlap-percent", type=float, default=OVERLAP_PERCENT)
    parser.add_argument("--fail-fast", action="store_true", help="stop after the first failed document")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    docling_dir = root / "Docling_Files"
    markdown_dir = root / "MD_Files"
    output_dir = root / "chunk_files"

    if args.max_tokens < 1:
        raise SystemExit("--max-tokens must be positive")
    if not 0 <= args.overlap_percent < 100:
        raise SystemExit("--overlap-percent must be at least 0 and less than 100")
    if not docling_dir.is_dir():
        raise SystemExit(f"Docling input directory not found: {docling_dir}")

    sources = sorted(docling_dir.glob("*.json"), key=lambda path: path.name.lower())
    if not sources:
        raise SystemExit(f"No Docling JSON files found in {docling_dir}")

    overlap_tokens = round(args.max_tokens * args.overlap_percent / 100)
    base_tokens = args.max_tokens - overlap_tokens
    raw_tokenizer = AutoTokenizer.from_pretrained(args.model)
    docling_tokenizer = HuggingFaceTokenizer(tokenizer=raw_tokenizer, max_tokens=base_tokens)
    chunker = HybridChunker(tokenizer=docling_tokenizer, merge_peers=True)

    failures = 0
    for number, source in enumerate(sources, start=1):
        try:
            count = chunk_document(
                source,
                markdown_dir,
                output_dir,
                chunker,
                raw_tokenizer,
                args.max_tokens,
                overlap_tokens,
                args.model,
            )
            print(f"[{number}/{len(sources)}] {source.name}: wrote {count} chunks")
        except Exception as error:
            failures += 1
            print(f"[{number}/{len(sources)}] {source.name}: FAILED: {error}", file=sys.stderr)
            if args.fail_fast:
                break

    if failures:
        print(f"Finished with {failures} failure(s).", file=sys.stderr)
        return 1
    print(f"Done. Chunk files are in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
