"""Experiment with app-equivalent Neon retrieval without calling an LLM.

``ExperimentalNeonRetrievalAdapter.search_chunks`` initially mirrors the app
adapter. Make retrieval experiments in that method, leaving retrieval.v2.py as
the current-app comparison CLI. Once an experiment is validated, the focused
method diff can be transferred to app/retrieval_adapter.py.
"""

from __future__ import annotations

import importlib.util
import json
import re
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
    encode_query,
    rerank,
    retrieve_candidates,
)
from app.schemas import EvidenceChunk, SearchFilters  # noqa: E402


def _load_baseline_cli() -> Any:
    path = Path(__file__).with_name("retrieval.v2.py")
    spec = importlib.util.spec_from_file_location("retrieval_v2_cli", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load baseline CLI from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_cli = _load_baseline_cli()

INITIAL_CANDIDATE_COUNT = 72
DEFAULT_FINAL_CHUNK_COUNT = 18
MAX_CHUNKS_PER_PAPER = 6
MAX_REVIEW_CHUNKS = 4

ALWAYS_EXCLUDED_SECTIONS = {
    "acknowledgement",
    "acknowledgements",
    "acknowledgment",
    "acknowledgments",
    "bibliography",
    "references",
    "workscited",
}


def normalize_section_heading(value: str) -> str:
    without_numbering = re.sub(
        r"^(?:[0-9]+(?:\.[0-9]+)*|[ivxlcdm]+)[\s.):-]+",
        "",
        value.casefold().strip(),
    )
    return re.sub(r"[^a-z0-9]+", "", without_numbering)


def filter_excluded_sections(
    candidates: list[Any], filters: SearchFilters
) -> list[Any]:
    excluded = set(ALWAYS_EXCLUDED_SECTIONS)
    if "introduction" in filters.excluded_sections:
        excluded.add("introduction")
    if "abstract" in filters.excluded_sections:
        excluded.add("abstract")
    return [
        candidate
        for candidate in candidates
        if not any(
            normalize_section_heading(heading) in excluded
            for heading in candidate.section_headings
        )
    ]


def select_with_review_cap(
    ranked: list[Any],
    paper_types: dict[str, str | None],
    top_k: int,
) -> list[Any]:
    """Select ranked candidates while limiting papers classified as Review."""
    selected = []
    review_count = 0
    for candidate in ranked:
        paper_type = (paper_types.get(candidate.record_id) or "").strip().casefold()
        if paper_type == "review":
            if review_count >= MAX_REVIEW_CHUNKS:
                continue
            review_count += 1
        selected.append(candidate)
        if len(selected) == top_k:
            break
    return selected


class ExperimentalNeonRetrievalAdapter(NeonRetrievalAdapter):
    """Editable retrieval path, initially identical to the app adapter."""

    def search_chunks(
        self, query: str, filters: SearchFilters, top_k: int
    ) -> list[EvidenceChunk]:
        self._load_models()
        query_embedding = encode_query(self._embedding_backend, query)
        connection = self._connect()
        try:
            candidates = retrieve_candidates(
                connection=connection,
                psycopg=self._psycopg,
                schema_name="public",
                table_name="rag_chunks",
                query_embedding=query_embedding,
                embedding_model=self.embedding_model,
                candidate_count=INITIAL_CANDIDATE_COUNT,
                include_intro="introduction" not in filters.excluded_sections,
                exclude_abstract="abstract" in filters.excluded_sections,
                record_id=filters.record_id,
            )
            candidates = filter_excluded_sections(candidates, filters)
            paper_types: dict[str, str | None] = {}
            paper_titles: dict[str, str | None] = {}
            record_ids = list({candidate.record_id for candidate in candidates})
            if record_ids:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT record_id, paper_type, paper_title
                        FROM public.paper_metadata
                        WHERE record_id = ANY(%s)
                        """,
                        (record_ids,),
                    )
                    for record_id, paper_type, paper_title in cursor.fetchall():
                        paper_types[record_id] = paper_type
                        paper_titles[record_id] = paper_title
        finally:
            connection.close()
        if not candidates:
            return []
        ranked = rerank(
            model=self._reranker_backend,
            query=query,
            candidates=candidates,
            batch_size=16,
            top_k=len(candidates),
            max_per_paper=MAX_CHUNKS_PER_PAPER,
        )
        selected = select_with_review_cap(ranked, paper_types, top_k)
        evidence = []
        for candidate in selected:
            candidate.title = paper_titles.get(candidate.record_id) or candidate.title
            chunk = self._to_evidence(candidate)
            chunk.metadata["paper_type"] = paper_types.get(candidate.record_id)
            evidence.append(chunk)
        return evidence


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
