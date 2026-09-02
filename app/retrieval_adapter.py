"""Application adapter for the shared vector retrieval and reranking pipeline."""

from __future__ import annotations

import re
from typing import Any

from retrieval.retrieval import (
    DEFAULT_RERANKER_MODEL,
    Candidate,
    encode_query,
    load_dependencies,
    rerank,
    retrieve_candidates,
)

from .schemas import EvidenceChunk, SearchFilters


INITIAL_CANDIDATE_COUNT = 72
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
    candidates: list[Candidate], filters: SearchFilters
) -> list[Candidate]:
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
    ranked: list[Candidate],
    paper_types: dict[str, str | None],
    top_k: int,
) -> list[Candidate]:
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


class NeonRetrievalAdapter:
    def __init__(self, database_url: str, embedding_model: str):
        self.database_url = database_url
        self.embedding_model = embedding_model
        self.reranker_model_name = DEFAULT_RERANKER_MODEL
        self._psycopg: Any | None = None
        self._register_vector: Any | None = None
        self._embedding_backend: Any | None = None
        self._reranker_backend: Any | None = None

    def _load_models(self) -> None:
        if self._embedding_backend is not None:
            return
        psycopg, register_vector, SentenceTransformer, CrossEncoder = load_dependencies()
        self._psycopg = psycopg
        self._register_vector = register_vector
        self._embedding_backend = SentenceTransformer(self.embedding_model)
        self._reranker_backend = CrossEncoder(
            self.reranker_model_name, max_length=1024
        )

    def _connect(self) -> Any:
        self._load_models()
        connection = self._psycopg.connect(self.database_url)
        self._register_vector(connection)
        return connection

    @staticmethod
    def _to_evidence(candidate: Candidate) -> EvidenceChunk:
        return EvidenceChunk(
            chunk_id=candidate.chunk_id,
            record_id=candidate.record_id,
            text=candidate.text,
            title=candidate.title,
            section=" > ".join(candidate.section_headings) or None,
            page_numbers=tuple(candidate.page_numbers),
            similarity=candidate.reranker_score,
            metadata={
                "doi": candidate.doi,
                "battery_chemistry_cathode": candidate.battery_chemistry_cathode,
                "manufacturer": candidate.manufacturer,
                "form_factor": candidate.form_factor,
                "vector_rank": candidate.vector_rank,
                "vector_similarity": candidate.vector_similarity,
                "reranker_score": candidate.reranker_score,
            },
        )

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

    def fetch_neighbors(
        self, chunk_id: str, before: int = 1, after: int = 1
    ) -> list[EvidenceChunk]:
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    WITH target AS (
                        SELECT record_id, chunk_index
                        FROM public.rag_chunks
                        WHERE chunk_id = %s
                    )
                    SELECT c.chunk_id, c.record_id, c.text, c.page_numbers,
                           c.metadata->>'title',
                           jsonb_extract_path(c.metadata, 'docling', 'headings'),
                           c.chunk_index
                    FROM public.rag_chunks AS c
                    JOIN target AS t ON t.record_id = c.record_id
                    WHERE c.chunk_index BETWEEN t.chunk_index - %s AND t.chunk_index + %s
                    ORDER BY c.chunk_index
                    """,
                    (chunk_id, before, after),
                )
                rows = cursor.fetchall()
        finally:
            connection.close()
        return [
            EvidenceChunk(
                chunk_id=row[0], record_id=row[1], text=row[2],
                page_numbers=tuple(row[3] or ()), title=row[4],
                section=" > ".join(row[5] or ()) or None,
                metadata={"chunk_index": row[6], "neighbor_of": chunk_id},
            )
            for row in rows
        ]

    def get_paper_metadata(self, record_id: str) -> dict[str, Any]:
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT to_jsonb(p) FROM public.paper_metadata AS p WHERE record_id = %s",
                    (record_id,),
                )
                row = cursor.fetchone()
        finally:
            connection.close()
        return dict(row[0]) if row else {}
