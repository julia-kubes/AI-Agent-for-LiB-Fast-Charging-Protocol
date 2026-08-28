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
import re
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
FORBIDDEN_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MINUS_CONTEXT_CHARS = set("()[]{}")


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


def character_context(text: str, index: int, radius: int = 50) -> str:
    """Return a printable excerpt around a suspicious character."""
    start = max(0, index - radius)
    end = min(len(text), index + radius + 1)
    return text[start:end].replace("\x00", "<NUL>")


def nearest_nonspace(text: str, index: int, step: int) -> str | None:
    position = index + step
    while 0 <= position < len(text):
        if not text[position].isspace():
            return text[position]
        position += step
    return None


def normalize_extracted_text(
    text: str,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Repair high-confidence missing minus signs and report ambiguous controls.

    PDF font mappings sometimes surface a minus sign as U+0000. A NUL is only
    changed when it occurs in a mathematical/textual token context. Other C0
    controls are not guessed: the containing chunk is quarantined for review.
    """
    characters = list(text)
    repairs: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for index, character in enumerate(text):
        if not FORBIDDEN_CONTROL_RE.fullmatch(character):
            continue
        context = character_context(text, index)
        if character == "\x00":
            left = nearest_nonspace(text, index, -1)
            right = nearest_nonspace(text, index, 1)
            left_is_token = left is not None and (left.isalnum() or left in MINUS_CONTEXT_CHARS)
            right_is_token = right is not None and (right.isalnum() or right in MINUS_CONTEXT_CHARS)
            if left_is_token and right_is_token:
                characters[index] = "-"
                repairs.append(
                    {
                        "character": "U+0000",
                        "replacement": "-",
                        "reason": "NUL between mathematical/text tokens; interpreted as minus",
                        "context": context,
                    }
                )
                continue
        issues.append(
            {
                "character": f"U+{ord(character):04X}",
                "reason": "ambiguous control character",
                "context": context,
            }
        )

    return "".join(characters), repairs, issues


def load_corrections(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load optional, document-scoped corrections verified against source PDFs."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("records"), dict):
        raise ValueError(f"Invalid corrections file: {path}")
    return data["records"]


def apply_verified_corrections(
    text: str,
    entries: list[dict[str, Any]],
    application_counts: list[int],
) -> str:
    """Apply exact replacements; broad character guesses remain quarantined."""
    for index, entry in enumerate(entries):
        find = entry.get("find")
        replacement = entry.get("replace")
        if not isinstance(find, str) or not find or not isinstance(replacement, str):
            raise ValueError("Each correction requires non-empty 'find' and string 'replace' values")
        occurrences = text.count(find)
        if occurrences:
            text = text.replace(find, replacement)
            application_counts[index] += occurrences
    return text


def apply_verified_corrections_to_value(
    value: Any,
    entries: list[dict[str, Any]],
    application_counts: list[int],
) -> Any:
    """Apply verified replacements recursively to JSON-compatible metadata."""
    if isinstance(value, str):
        return apply_verified_corrections(value, entries, application_counts)
    if isinstance(value, dict):
        return {
            key: apply_verified_corrections_to_value(child, entries, application_counts)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            apply_verified_corrections_to_value(child, entries, application_counts)
            for child in value
        ]
    return value


def remaining_control_issues(value: Any, path: str = "$") -> list[dict[str, Any]]:
    """Find forbidden controls anywhere in a JSON-compatible chunk record."""
    issues: list[dict[str, Any]] = []
    if isinstance(value, str):
        for match in FORBIDDEN_CONTROL_RE.finditer(value):
            issues.append(
                {
                    "field": path,
                    "character": f"U+{ord(match.group()):04X}",
                    "reason": "forbidden control character remains after normalization",
                    "context": character_context(value, match.start()),
                }
            )
    elif isinstance(value, dict):
        for key, child in value.items():
            issues.extend(remaining_control_issues(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(remaining_control_issues(child, f"{path}[{index}]"))
    return issues


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
    corrections: dict[str, list[dict[str, Any]]],
) -> int:
    record_id = docling_path.stem
    markdown_path = markdown_dir / f"{record_id}.md"
    document_metadata = markdown_front_matter(markdown_path)
    document_metadata.setdefault("record_id", record_id)

    document = DoclingDocument.load_from_json(docling_path)
    chunks = list(chunker.chunk(document))
    records: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    repair_events: list[dict[str, Any]] = []
    correction_entries = corrections.get(record_id, [])
    correction_application_counts = [0] * len(correction_entries)
    document_metadata = apply_verified_corrections_to_value(
        document_metadata, correction_entries, correction_application_counts
    )
    previous_text = ""

    for index, chunk in enumerate(chunks, start=1):
        chunk_id = f"{record_id}::chunk::{index:04d}"
        raw_content_text = apply_verified_corrections(
            chunk.text, correction_entries, correction_application_counts
        )
        raw_contextualized_text = apply_verified_corrections(
            chunker.contextualize(chunk=chunk), correction_entries, correction_application_counts
        )
        content_text, content_repairs, content_issues = normalize_extracted_text(raw_content_text)
        contextualized_text, context_repairs, context_issues = normalize_extracted_text(raw_contextualized_text)
        for field, events in (
            ("content_text", content_repairs),
            ("contextualized_text", context_repairs),
        ):
            for event in events:
                repair_events.append({"chunk_id": chunk_id, "field": field, **event})
        text_issues = [
            *({"field": "content_text", **issue} for issue in content_issues),
            *({"field": "contextualized_text", **issue} for issue in context_issues),
        ]
        if text_issues:
            quarantined.append(
                {
                    "chunk_id": chunk_id,
                    "record_id": record_id,
                    "chunk_index": index,
                    "reason": "ambiguous extracted control characters",
                    "issues": text_issues,
                }
            )
            previous_text = ""
            continue

        requested_overlap = trim_token_tail(previous_text, overlap_tokens, raw_tokenizer)
        embedding_text, used_overlap, token_count = combine_with_overlap(
            requested_overlap,
            contextualized_text,
            max_tokens,
            raw_tokenizer,
        )
        docling_metadata = json_safe(chunk.meta)
        record = {
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
        record_issues = remaining_control_issues(record)
        if record_issues:
            quarantined.append(
                {
                    "chunk_id": chunk_id,
                    "record_id": record_id,
                    "chunk_index": index,
                    "reason": "control characters remain in chunk record",
                    "issues": record_issues,
                }
            )
            previous_text = ""
            continue
        records.append(record)
        previous_text = content_text

    paper_dir = output_dir / record_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(paper_dir / "chunks.jsonl", records)
    write_jsonl(paper_dir / "quarantine.jsonl", quarantined)
    write_json(
        paper_dir / "quality_report.json",
        {
            "schema_version": 1,
            "record_id": record_id,
            "source_chunk_count": len(chunks),
            "written_chunk_count": len(records),
            "quarantined_chunk_count": len(quarantined),
            "automatic_repair_count": len(repair_events),
            "automatic_repairs": repair_events,
            "verified_corrections": [
                {
                    "find": entry["find"],
                    "replace": entry["replace"],
                    "source_page": entry.get("source_page"),
                    "note": entry.get("note"),
                    "application_count": correction_application_counts[index],
                }
                for index, entry in enumerate(correction_entries)
            ],
            "unmatched_verified_correction_count": sum(
                count == 0 for count in correction_application_counts
            ),
            "quarantine_file": "quarantine.jsonl",
        },
    )
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
            "source_chunk_count": len(chunks),
            "quarantined_chunk_count": len(quarantined),
            "automatic_repair_count": len(repair_events),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )
    verified_application_count = sum(correction_application_counts)
    unmatched_correction_count = sum(count == 0 for count in correction_application_counts)
    if quarantined:
        print(
            f"    REVIEW REQUIRED: {len(quarantined)} quarantined chunk(s); "
            f"see {paper_dir / 'quality_report.json'} and {paper_dir / 'quarantine.jsonl'}"
        )
    elif unmatched_correction_count:
        print(
            f"    REVIEW REQUIRED: {unmatched_correction_count} verified correction(s) did not match; "
            f"see {paper_dir / 'quality_report.json'}"
        )
    elif repair_events:
        print(
            f"    REVIEW RECOMMENDED: {len(repair_events)} automatic repair event(s); "
            f"see {paper_dir / 'quality_report.json'}"
        )
    elif verified_application_count:
        print(
            f"    Quality check passed: applied {verified_application_count} verified correction(s); "
            "no quarantines."
        )
    else:
        print("    Quality check passed: no control-character repairs or quarantines.")
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
    parser.add_argument(
        "--corrections",
        type=Path,
        help="verified corrections JSON (default: <root>/corrections.json)",
    )
    parser.add_argument(
        "--record",
        action="append",
        dest="records",
        help="process only this record ID; repeat to select multiple records",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    docling_dir = root / "Docling_Files"
    markdown_dir = root / "MD_Files"
    output_dir = root / "chunk_files"
    corrections_path = (args.corrections or (root / "corrections.json")).resolve()
    corrections = load_corrections(corrections_path)

    if args.max_tokens < 1:
        raise SystemExit("--max-tokens must be positive")
    if not 0 <= args.overlap_percent < 100:
        raise SystemExit("--overlap-percent must be at least 0 and less than 100")
    if not docling_dir.is_dir():
        raise SystemExit(f"Docling input directory not found: {docling_dir}")

    sources = sorted(docling_dir.glob("*.json"), key=lambda path: path.name.lower())
    if args.records:
        selected = set(args.records)
        sources = [source for source in sources if source.stem in selected]
        missing = selected - {source.stem for source in sources}
        if missing:
            raise SystemExit(f"Requested record(s) not found: {', '.join(sorted(missing))}")
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
                corrections,
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
