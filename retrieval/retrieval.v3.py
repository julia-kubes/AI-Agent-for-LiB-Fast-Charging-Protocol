"""Run the retrieval.v3 settings through the app's integrated retrieval path.

This remains a direct, no-LLM comparison CLI. Its experimental retrieval logic
now lives in ``app.retrieval_adapter`` so CLI experiments and the app cannot
drift apart.
"""

from __future__ import annotations

import importlib.util
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
from app.retrieval_adapter import (  # noqa: E402
    NeonRetrievalAdapter,
    filter_excluded_sections,
    select_with_review_cap,
)
from app.schemas import SearchFilters  # noqa: E402


def _load_baseline_cli() -> Any:
    path = Path(__file__).with_name("retrieval.v2.py")
    spec = importlib.util.spec_from_file_location("retrieval_v2_cli", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load baseline CLI from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_cli = _load_baseline_cli()

DEFAULT_FINAL_CHUNK_COUNT = 18


class ExperimentalNeonRetrievalAdapter(NeonRetrievalAdapter):
    """Compatibility name for the retrieval.v3 comparison CLI."""


def main() -> int:
    baseline_cli.__doc__ = __doc__
    args = baseline_cli.parse_args(
        default_top_k=DEFAULT_FINAL_CHUNK_COUNT,
        max_top_k=DEFAULT_FINAL_CHUNK_COUNT,
    )
    settings = Settings.from_env()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is not configured in .env or the environment.")

    filters = baseline_cli.filters_from_args(args)
    retrieval = ExperimentalNeonRetrievalAdapter(
        settings.database_url,
        settings.embedding_model,
    )
    chunks = retrieval.search_chunks(args.query, filters, args.top_k)
    payload = baseline_cli.result_payload(
        args.query, args.top_k, filters, chunks
    )
    payload["implementation"] = (
        "retrieval.v3.ExperimentalNeonRetrievalAdapter"
    )
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        baseline_cli.print_results(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
