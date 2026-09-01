"""Run the application's current Neon retrieval adapter without an LLM.

This is the baseline retrieval-quality CLI. It deliberately imports
``app.retrieval_adapter.NeonRetrievalAdapter`` instead of copying its logic, so
the results represent the application implementation in the current checkout.
No LLM client is created and no LLM API calls are made.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIRECTORY.parent
sys.path[:] = [
    entry
    for entry in sys.path
    if Path(entry or ".").resolve() != SCRIPT_DIRECTORY
]
if str(REPOSITORY_ROOT) in sys.path:
    sys.path.remove(str(REPOSITORY_ROOT))
sys.path.insert(0, str(REPOSITORY_ROOT))

from app.config import Settings  # noqa: E402
from app.retrieval_adapter import NeonRetrievalAdapter  # noqa: E402
from app.schemas import EvidenceChunk, SearchFilters  # noqa: E402


DEFAULT_TOP_K = 12


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return number


def parse_args(
    *,
    default_top_k: int = DEFAULT_TOP_K,
    max_top_k: int = DEFAULT_TOP_K,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="plain-language retrieval query")
    parser.add_argument(
        "--top-k",
        type=positive_int,
        default=default_top_k,
        help=f"reranked chunks to return (default: {default_top_k})",
    )
    parser.add_argument("--record-id", help="optionally search one paper only")
    parser.add_argument(
        "--include-intro",
        action="store_true",
        help="include Introduction sections (excluded by default)",
    )
    parser.add_argument(
        "--include-abstract",
        action="store_true",
        help="include Abstract sections (excluded by default)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    args = parser.parse_args()
    if args.top_k > max_top_k:
        parser.error(
            f"--top-k cannot exceed the configured limit of {max_top_k}"
        )
    return args


def filters_from_args(args: argparse.Namespace) -> SearchFilters:
    excluded = []
    if not args.include_intro:
        excluded.append("introduction")
    if not args.include_abstract:
        excluded.append("abstract")
    return SearchFilters(
        record_id=args.record_id,
        excluded_sections=tuple(excluded),
    )


def result_payload(
    query: str,
    requested_top_k: int,
    filters: SearchFilters,
    chunks: list[EvidenceChunk],
) -> dict[str, Any]:
    return {
        "implementation": "app.retrieval_adapter.NeonRetrievalAdapter",
        "query": query,
        "requested_top_k": requested_top_k,
        "result_count": len(chunks),
        "distinct_paper_count": len({chunk.record_id for chunk in chunks}),
        "filters": {
            "record_id": filters.record_id,
            "excluded_sections": list(filters.excluded_sections),
        },
        "results": [
            {"reranker_rank": rank, **chunk.to_dict()}
            for rank, chunk in enumerate(chunks, start=1)
        ],
    }


def print_results(payload: dict[str, Any]) -> None:
    print(f"\nTop {payload['result_count']} app retrieval results")
    print(f"Query: {payload['query']}")
    print(f"Distinct papers: {payload['distinct_paper_count']}")
    print(f"Filters: {payload['filters']}\n")
    for result in payload["results"]:
        metadata = result["metadata"]
        preview = " ".join(result["text"].split())
        if len(preview) > 700:
            preview = preview[:697] + "..."
        print(
            f"[{result['reranker_rank']}] "
            f"reranker={metadata.get('reranker_score', 'n/s')} "
            f"vector={metadata.get('vector_similarity', 'n/s')}"
        )
        print(
            f"    chunk={result['chunk_id']} "
            f"source={result.get('title') or result['record_id']}"
        )
        print(
            f"    pages={result['page_numbers']} "
            f"section={result.get('section') or 'n/s'}"
        )
        print(
            "    "
            f"chemistry={metadata.get('battery_chemistry_cathode') or 'n/s'} "
            f"manufacturer={metadata.get('manufacturer') or 'n/s'} "
            f"form_factor={metadata.get('form_factor') or 'n/s'}"
        )
        print(f"    {preview}\n")


def main() -> int:
    args = parse_args()
    settings = Settings.from_env()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is not configured in .env or the environment.")

    filters = filters_from_args(args)
    retrieval = NeonRetrievalAdapter(
        settings.database_url,
        settings.embedding_model,
    )
    chunks = retrieval.search_chunks(args.query, filters, args.top_k)
    payload = result_payload(args.query, args.top_k, filters, chunks)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_results(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
