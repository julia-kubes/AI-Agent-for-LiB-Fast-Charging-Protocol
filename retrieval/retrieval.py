"""Retrieve and rerank RAG chunks from PostgreSQL/pgvector.

The retrieval funnel is:

    query -> GTE query embedding -> top 30 pgvector candidates
          -> GTE cross-encoder reranker -> top 8 results

DATABASE_URL supplies the PostgreSQL/Neon connection string. This script is
read-only: it does not update chunks, metadata, or stored embeddings.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any, Sequence


DEFAULT_EMBEDDING_MODEL = "Alibaba-NLP/gte-modernbert-base"
DEFAULT_RERANKER_MODEL = "Alibaba-NLP/gte-reranker-modernbert-base"
DEFAULT_CANDIDATE_COUNT = 30
DEFAULT_RESULT_COUNT = 8
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return number


def database_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "database identifiers may contain only letters, numbers, and "
            "underscores and cannot begin with a number"
        )
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="plain-language retrieval query")
    parser.add_argument("--schema", type=database_identifier, default="public")
    parser.add_argument("--table", type=database_identifier, default="rag_chunks")
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"query embedding model (default: {DEFAULT_EMBEDDING_MODEL})",
    )
    parser.add_argument(
        "--reranker-model",
        default=DEFAULT_RERANKER_MODEL,
        help=f"cross-encoder reranker (default: {DEFAULT_RERANKER_MODEL})",
    )
    parser.add_argument(
        "--candidates",
        type=positive_int,
        default=DEFAULT_CANDIDATE_COUNT,
        help=f"vector candidates to retrieve (default: {DEFAULT_CANDIDATE_COUNT})",
    )
    parser.add_argument(
        "--top-k",
        type=positive_int,
        default=DEFAULT_RESULT_COUNT,
        help=f"reranked results to return (default: {DEFAULT_RESULT_COUNT})",
    )
    parser.add_argument(
        "--max-per-paper",
        type=positive_int,
        help=(
            "optional diversity cap on results from one paper; for example, "
            "--max-per-paper 2"
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=positive_int,
        default=16,
        help="reranker inference batch size (default: 16)",
    )
    parser.add_argument(
        "--max-length",
        type=positive_int,
        default=1024,
        help="maximum query-plus-chunk token length for reranking (default: 1024)",
    )
    parser.add_argument(
        "--device",
        help="Sentence Transformers device, such as cpu or cuda (default: auto)",
    )
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL; preferably set DATABASE_URL instead",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of formatted text",
    )
    args = parser.parse_args()
    if args.top_k > args.candidates:
        parser.error("--top-k cannot be greater than --candidates")
    return args


def load_dependencies() -> tuple[Any, Any, Any, Any]:
    try:
        import psycopg
        from pgvector.psycopg import register_vector
        from sentence_transformers import CrossEncoder, SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "Missing dependency. Install the packages from "
            "../embedding/requirements.txt. Original error: " + str(error)
        ) from error
    return psycopg, register_vector, SentenceTransformer, CrossEncoder


@dataclass
class Candidate:
    chunk_id: str
    record_id: str
    chunk_index: int
    text: str
    page_numbers: list[int]
    title: str | None
    doi: str | None
    battery_chemistry_cathode: str | None
    manufacturer: str | None
    form_factor: str | None
    section_headings: list[str]
    vector_rank: int
    vector_similarity: float
    reranker_score: float | None = None


def encode_query(model: Any, query: str) -> Any:
    embeddings = model.encode(
        [query],
        batch_size=1,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings[0]


def retrieve_candidates(
    connection: Any,
    psycopg: Any,
    schema_name: str,
    table_name: str,
    query_embedding: Any,
    embedding_model: str,
    candidate_count: int,
) -> list[Candidate]:
    table = psycopg.sql.Identifier(schema_name, table_name)
    statement = psycopg.sql.SQL(
        """
        SELECT
            c.chunk_id,
            c.record_id,
            c.chunk_index,
            c.text,
            c.page_numbers,
            c.metadata->>'title' AS title,
            p.doi,
            p.battery_chemistry_cathode,
            p.manufacturer,
            p.form_factor,
            jsonb_extract_path(c.metadata, 'docling', 'headings') AS section_headings,
            1 - (c.embedding <=> %s) AS vector_similarity
        FROM {} AS c
        LEFT JOIN public.paper_metadata AS p
            ON p.record_id = c.record_id
        WHERE c.embedding_model = %s
        ORDER BY c.embedding <=> %s
        LIMIT %s
        """
    ).format(table)

    with connection.cursor() as cursor:
        cursor.execute(
            statement,
            (query_embedding, embedding_model, query_embedding, candidate_count),
        )
        rows = cursor.fetchall()

    return [
        Candidate(
            chunk_id=row[0],
            record_id=row[1],
            chunk_index=row[2],
            text=row[3],
            page_numbers=row[4] or [],
            title=row[5],
            doi=row[6],
            battery_chemistry_cathode=row[7],
            manufacturer=row[8],
            form_factor=row[9],
            section_headings=(
                [str(value) for value in row[10]]
                if isinstance(row[10], list)
                else []
            ),
            vector_rank=rank,
            vector_similarity=float(row[11]),
        )
        for rank, row in enumerate(rows, start=1)
    ]


def rerank(
    model: Any,
    query: str,
    candidates: Sequence[Candidate],
    batch_size: int,
    top_k: int,
    max_per_paper: int | None,
) -> list[Candidate]:
    pairs = [(query, candidate.text) for candidate in candidates]
    scores = model.predict(
        pairs,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    for candidate, score in zip(candidates, scores, strict=True):
        candidate.reranker_score = float(score)
    ranked = sorted(
        candidates,
        key=lambda candidate: candidate.reranker_score
        if candidate.reranker_score is not None
        else float("-inf"),
        reverse=True,
    )
    if max_per_paper is None:
        return ranked[:top_k]

    selected: list[Candidate] = []
    paper_counts: dict[str, int] = {}
    for candidate in ranked:
        count = paper_counts.get(candidate.record_id, 0)
        if count >= max_per_paper:
            continue
        selected.append(candidate)
        paper_counts[candidate.record_id] = count + 1
        if len(selected) == top_k:
            break
    return selected


def result_payload(query: str, candidates: Sequence[Candidate]) -> dict[str, Any]:
    return {
        "query": query,
        "result_count": len(candidates),
        "distinct_paper_count": len({candidate.record_id for candidate in candidates}),
        "results": [
            {"reranker_rank": rank, **asdict(candidate)}
            for rank, candidate in enumerate(candidates, start=1)
        ],
    }


def print_results(query: str, candidates: Sequence[Candidate]) -> None:
    print(f"\nTop {len(candidates)} reranked results for: {query}\n")
    print(f"Distinct papers represented: {len({c.record_id for c in candidates})}\n")
    for rank, candidate in enumerate(candidates, start=1):
        preview = " ".join(candidate.text.split())
        if len(preview) > 700:
            preview = preview[:697] + "..."
        print(
            f"[{rank}] reranker={candidate.reranker_score:.4f}  "
            f"vector={candidate.vector_similarity:.4f}  "
            f"original_vector_rank={candidate.vector_rank}"
        )
        print(
            f"    chunk={candidate.chunk_id}  source={candidate.title or candidate.record_id}"
        )
        print(
            f"    pages={candidate.page_numbers}  "
            f"section={' > '.join(candidate.section_headings) or 'n/s'}  "
        )
        print(
            "    "
            f"chemistry={candidate.battery_chemistry_cathode or 'n/s'}  "
            f"manufacturer={candidate.manufacturer or 'n/s'}  "
            f"form_factor={candidate.form_factor or 'n/s'}"
        )
        print(f"    {preview}\n")


def main() -> int:
    args = parse_args()
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set.")

    psycopg, register_vector, SentenceTransformer, CrossEncoder = load_dependencies()
    model_options = {"device": args.device} if args.device else {}

    if not args.json:
        print(f"Loading embedding model: {args.embedding_model}")
    embedding_model = SentenceTransformer(args.embedding_model, **model_options)
    query_embedding = encode_query(embedding_model, args.query)

    try:
        connection = psycopg.connect(database_url)
        register_vector(connection)
    except Exception as error:
        raise SystemExit(f"Could not connect to PostgreSQL: {error}") from error

    try:
        candidates = retrieve_candidates(
            connection=connection,
            psycopg=psycopg,
            schema_name=args.schema,
            table_name=args.table,
            query_embedding=query_embedding,
            embedding_model=args.embedding_model,
            candidate_count=args.candidates,
        )
    except Exception as error:
        raise SystemExit(f"Vector retrieval failed: {error}") from error
    finally:
        connection.close()

    if not candidates:
        raise SystemExit(
            "No candidate chunks were found for the requested embedding model."
        )

    if not args.json:
        print(f"Retrieved {len(candidates)} vector candidates.")
        print(f"Loading reranker: {args.reranker_model}")
    reranker_options = {"device": args.device} if args.device else {}
    reranker_model = CrossEncoder(
        args.reranker_model,
        max_length=args.max_length,
        **reranker_options,
    )
    results = rerank(
        model=reranker_model,
        query=args.query,
        candidates=candidates,
        batch_size=args.batch_size,
        top_k=args.top_k,
        max_per_paper=args.max_per_paper,
    )

    if args.json:
        print(json.dumps(result_payload(args.query, results), indent=2))
    else:
        print_results(args.query, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
