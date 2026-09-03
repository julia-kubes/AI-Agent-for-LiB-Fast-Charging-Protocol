"""Embed Docling JSONL chunks and store them in PostgreSQL with pgvector.

The default input layout is:

    chunk_files/<record_id>/chunks.jsonl

Database credentials are read from DATABASE_URL. Use --dry-run to validate the
input files without loading the model or connecting to PostgreSQL.

Embeddings are cached locally before database upload. If an upload is
interrupted, rerun with --store-only to reuse the cache without re-embedding.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_MODEL = "Alibaba-NLP/gte-modernbert-base"
DEFAULT_DIMENSIONS = 768
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return number


def database_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "database identifiers may contain only letters, numbers, and underscores "
            "and cannot begin with a number"
        )
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chunks-root",
        type=Path,
        default=Path.cwd() / "chunk_files",
        help="directory containing **/chunks.jsonl (default: ./chunk_files)",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--schema", type=database_identifier, default="public")
    parser.add_argument("--table", type=database_identifier, default="rag_chunks")
    parser.add_argument("--batch-size", type=positive_int, default=16)
    parser.add_argument(
        "--device",
        default=None,
        help="Sentence Transformers device, such as cpu, cuda, or mps (default: auto)",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="PostgreSQL URL; preferably set DATABASE_URL instead of using this option",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and count chunks without loading the model or using the database",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--embed-only",
        action="store_true",
        help="create/replace the local embedding cache without using PostgreSQL",
    )
    modes.add_argument(
        "--store-only",
        action="store_true",
        help="upload a previously created cache without running the embedding model",
    )
    parser.add_argument(
        "--embedding-cache",
        type=Path,
        default=Path.cwd() / "embedding_cache.npz",
        help="local NumPy cache (default: ./embedding_cache.npz)",
    )
    parser.add_argument(
        "--query",
        metavar="TEXT",
        help="query existing embeddings instead of ingesting chunks",
    )
    parser.add_argument("--top-k", type=positive_int, default=5)
    parser.add_argument(
        "--record-id",
        help="optional record_id filter used with --query",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="do not create the HNSW cosine index after ingestion",
    )
    return parser.parse_args()


def discover_chunk_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise SystemExit(f"Chunk directory not found: {root}")
    files = sorted(root.rglob("chunks.jsonl"), key=lambda path: str(path).lower())
    if not files:
        raise SystemExit(f"No chunks.jsonl files found under: {root}")
    return files


def validate_chunk(value: Any, source: Path, line_number: int) -> dict[str, Any]:
    location = f"{source}:{line_number}"
    if not isinstance(value, dict):
        raise ValueError(f"{location}: each line must be a JSON object")

    required = {
        "chunk_id": str,
        "record_id": str,
        "chunk_index": int,
        "text": str,
        "content_sha256": str,
        "metadata": dict,
    }
    for field, expected_type in required.items():
        if field not in value:
            raise ValueError(f"{location}: missing required field {field!r}")
        if not isinstance(value[field], expected_type):
            raise ValueError(
                f"{location}: {field!r} must be {expected_type.__name__}"
            )
    if not value["chunk_id"] or not value["record_id"] or not value["text"].strip():
        raise ValueError(f"{location}: chunk_id, record_id, and text cannot be empty")
    return value


def is_embedding_eligible(value: Any) -> bool:
    """Return False for chunks explicitly quarantined or not approved."""
    if not isinstance(value, dict):
        return True

    metadata = value.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    quarantined = value.get("quarantined", metadata.get("quarantined", False))
    validation_status = value.get(
        "validation_status", metadata.get("validation_status", "approved")
    )
    return quarantined is not True and validation_status == "approved"


def load_chunks(files: Sequence[Path]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    skipped = 0
    for path in files:
        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
                if not is_embedding_eligible(raw):
                    skipped += 1
                    continue
                chunk = validate_chunk(raw, path, line_number)
                chunk_id = chunk["chunk_id"]
                if chunk_id in seen_ids:
                    raise ValueError(f"{path}:{line_number}: duplicate chunk_id {chunk_id!r}")
                seen_ids.add(chunk_id)
                chunks.append(chunk)
    if not chunks:
        raise ValueError("Chunk files contained no embedding-eligible records")
    if skipped:
        print(f"Skipped {skipped} quarantined or unapproved chunks.")
    return chunks


def page_numbers(chunk: dict[str, Any]) -> list[int]:
    values = chunk.get("metadata", {}).get("page_numbers", [])
    return [value for value in values if isinstance(value, int)]


def batched(values: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def load_dependencies() -> tuple[Any, Any, Any, Any]:
    try:
        import psycopg
        from pgvector.psycopg import register_vector
        from psycopg.types.json import Jsonb
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "Missing Python dependency. Install the packages in requirements.txt "
            f"before continuing. Original error: {error}"
        ) from error
    return psycopg, register_vector, Jsonb, SentenceTransformer


def connect(database_url: str, psycopg: Any, register_vector: Any) -> Any:
    try:
        connection = psycopg.connect(database_url)
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.commit()
        register_vector(connection)
        return connection
    except Exception as error:
        raise SystemExit(f"Could not connect to PostgreSQL/enable pgvector: {error}") from error


def ensure_table(
    connection: Any,
    schema_name: str,
    table_name: str,
    dimensions: int,
    psycopg: Any,
) -> None:
    sql = psycopg.sql
    table = sql.Identifier(schema_name, table_name)
    schema = sql.Identifier(schema_name)
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(schema))
        cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {} (
                    chunk_id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    content_text TEXT,
                    contextualized_text TEXT,
                    overlap_text TEXT,
                    token_count INTEGER,
                    content_sha256 TEXT NOT NULL,
                    metadata JSONB NOT NULL,
                    page_numbers INTEGER[] NOT NULL DEFAULT ARRAY[]::INTEGER[],
                    embedding_model TEXT NOT NULL,
                    embedding_dimensions INTEGER NOT NULL,
                    embedding vector({}) NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (record_id, chunk_index)
                )
                """
            ).format(table, sql.Literal(dimensions))
        )
    connection.commit()


def encode(model: Any, texts: Sequence[str], batch_size: int) -> Any:
    return model.encode(
        list(texts),
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def save_embedding_cache(
    path: Path,
    chunks: Sequence[dict[str, Any]],
    embeddings: Any,
    model_name: str,
    dimensions: int,
) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        embeddings=embeddings,
        chunk_ids=np.asarray([chunk["chunk_id"] for chunk in chunks]),
        content_sha256=np.asarray([chunk["content_sha256"] for chunk in chunks]),
        model=np.asarray(model_name),
        dimensions=np.asarray(dimensions),
    )
    print(f"Saved reusable embedding cache: {path}")


def load_embedding_cache(
    path: Path,
    chunks: Sequence[dict[str, Any]],
    expected_model: str,
) -> tuple[Any, int]:
    import numpy as np

    if not path.is_file():
        raise SystemExit(
            f"Embedding cache not found: {path}. Run without --store-only or use --embed-only first."
        )
    with np.load(path, allow_pickle=False) as cache:
        embeddings = cache["embeddings"]
        cached_ids = cache["chunk_ids"].tolist()
        cached_hashes = cache["content_sha256"].tolist()
        cached_model = str(cache["model"].item())
        dimensions = int(cache["dimensions"].item())

    current_ids = [chunk["chunk_id"] for chunk in chunks]
    current_hashes = [chunk["content_sha256"] for chunk in chunks]
    if cached_model != expected_model:
        raise SystemExit(
            f"Cache model mismatch: cache uses {cached_model}, requested {expected_model}."
        )
    if cached_ids != current_ids or cached_hashes != current_hashes:
        raise SystemExit(
            "Embedding cache does not match the current chunks. Re-embed to refresh the cache."
        )
    if embeddings.shape != (len(chunks), dimensions):
        raise SystemExit(f"Invalid embedding cache shape: {embeddings.shape}")
    print(f"Loaded {len(chunks)} embeddings from cache: {path}")
    return embeddings, dimensions


def ingest(args: argparse.Namespace, chunks: Sequence[dict[str, Any]]) -> None:
    psycopg, register_vector, Jsonb, SentenceTransformer = load_dependencies()
    cache_path = args.embedding_cache.resolve()
    if args.store_only:
        embeddings, dimensions = load_embedding_cache(cache_path, chunks, args.model)
    else:
        print(f"Loading embedding model: {args.model}")
        model_options = {"device": args.device} if args.device else {}
        model = SentenceTransformer(args.model, **model_options)
        dimension_getter = getattr(model, "get_embedding_dimension", None)
        dimensions = (
            dimension_getter()
            if dimension_getter is not None
            else model.get_sentence_embedding_dimension()
        )
        if dimensions != DEFAULT_DIMENSIONS and args.model == DEFAULT_MODEL:
            raise SystemExit(
                f"Expected {DEFAULT_DIMENSIONS} dimensions for {DEFAULT_MODEL}, got {dimensions}."
            )
        print(f"Encoding {len(chunks)} chunks in batches of {args.batch_size}...")
        embeddings = encode(model, [chunk["text"] for chunk in chunks], args.batch_size)
        if embeddings.shape != (len(chunks), dimensions):
            raise SystemExit(f"Unexpected embedding array shape: {embeddings.shape}")
        save_embedding_cache(cache_path, chunks, embeddings, args.model, dimensions)

    if args.embed_only:
        print("Embedding complete; database upload skipped (--embed-only).")
        return

    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL is not set. The embedding cache was saved; set the connection and "
            "rerun with --store-only."
        )

    print("Connecting to PostgreSQL with a fresh connection...")
    connection = connect(database_url, psycopg, register_vector)
    try:
        ensure_table(connection, args.schema, args.table, dimensions, psycopg)
        sql = psycopg.sql
        table = sql.Identifier(args.schema, args.table)
        statement = sql.SQL(
            """
            INSERT INTO {} (
                chunk_id, record_id, chunk_index, text, content_text,
                contextualized_text, overlap_text, token_count, content_sha256,
                metadata, page_numbers, embedding_model, embedding_dimensions,
                embedding
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (chunk_id) DO UPDATE SET
                record_id = EXCLUDED.record_id,
                chunk_index = EXCLUDED.chunk_index,
                text = EXCLUDED.text,
                content_text = EXCLUDED.content_text,
                contextualized_text = EXCLUDED.contextualized_text,
                overlap_text = EXCLUDED.overlap_text,
                token_count = EXCLUDED.token_count,
                content_sha256 = EXCLUDED.content_sha256,
                metadata = EXCLUDED.metadata,
                page_numbers = EXCLUDED.page_numbers,
                embedding_model = EXCLUDED.embedding_model,
                embedding_dimensions = EXCLUDED.embedding_dimensions,
                embedding = EXCLUDED.embedding,
                updated_at = CURRENT_TIMESTAMP
            """
        ).format(table)

        processed = 0
        with connection.cursor() as cursor:
            for chunk_batch in batched(list(zip(chunks, embeddings)), args.batch_size):
                rows = []
                for chunk, embedding in chunk_batch:
                    rows.append(
                        (
                            chunk["chunk_id"],
                            chunk["record_id"],
                            chunk["chunk_index"],
                            chunk["text"],
                            chunk.get("content_text"),
                            chunk.get("contextualized_text"),
                            chunk.get("overlap_text"),
                            chunk.get("token_count"),
                            chunk["content_sha256"],
                            Jsonb(chunk["metadata"]),
                            page_numbers(chunk),
                            args.model,
                            dimensions,
                            embedding,
                        )
                    )
                cursor.executemany(statement, rows)
                processed += len(rows)
                print(f"Stored {processed}/{len(chunks)} chunks", end="\r", flush=True)
        connection.commit()
        print(f"Stored {processed}/{len(chunks)} chunks")

        if not args.skip_index:
            index_name = database_identifier(f"{args.table}_embedding_hnsw_idx")
            with connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL(
                        "CREATE INDEX IF NOT EXISTS {} ON {} "
                        "USING hnsw (embedding vector_cosine_ops)"
                    ).format(sql.Identifier(index_name), table)
                )
            connection.commit()

        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(table))
            total_rows = cursor.fetchone()[0]
            cursor.execute(
                sql.SQL(
                    "SELECT COUNT(*) FROM {} WHERE embedding_model = %s "
                    "AND vector_dims(embedding) = %s"
                ).format(table),
                (args.model, dimensions),
            )
            valid_rows = cursor.fetchone()[0]
        print(
            f"Verification passed: table contains {total_rows} rows; "
            f"{valid_rows} use {args.model} with {dimensions} dimensions."
        )
    finally:
        connection.close()


def query_database(args: argparse.Namespace) -> None:
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set.")
    psycopg, register_vector, _Jsonb, SentenceTransformer = load_dependencies()
    model_options = {"device": args.device} if args.device else {}
    print(f"Loading embedding model: {args.model}")
    model = SentenceTransformer(args.model, **model_options)
    query_embedding = encode(model, [args.query], 1)[0]
    connection = connect(database_url, psycopg, register_vector)
    try:
        sql = psycopg.sql
        table = sql.Identifier(args.schema, args.table)
        record_filter = sql.SQL("")
        parameters: list[Any] = [query_embedding, args.model]
        if args.record_id:
            record_filter = sql.SQL(" AND record_id = %s")
            parameters.append(args.record_id)
        parameters.extend([query_embedding, args.top_k])
        statement = sql.SQL(
            """
            SELECT
                chunk_id,
                record_id,
                text,
                page_numbers,
                metadata->>'title' AS title,
                1 - (embedding <=> %s) AS similarity
            FROM {}
            WHERE embedding_model = %s{}
            ORDER BY embedding <=> %s
            LIMIT %s
            """
        ).format(table, record_filter)
        with connection.cursor() as cursor:
            cursor.execute(statement, parameters)
            rows = cursor.fetchall()
        if not rows:
            print("No matching chunks found.")
            return
        print(f"\nTop {len(rows)} result(s) for: {args.query}\n")
        for rank, row in enumerate(rows, start=1):
            chunk_id, record_id, text_value, pages, title, similarity = row
            preview = " ".join(text_value.split())
            if len(preview) > 500:
                preview = preview[:497] + "..."
            print(f"[{rank}] similarity={similarity:.4f}  chunk={chunk_id}")
            print(f"    source={title or record_id}  pages={pages or []}")
            print(f"    {preview}\n")
    finally:
        connection.close()


def main() -> int:
    args = parse_args()
    if args.query:
        query_database(args)
        return 0

    files = discover_chunk_files(args.chunks_root.resolve())
    try:
        chunks = load_chunks(files)
    except ValueError as error:
        raise SystemExit(f"Chunk validation failed: {error}") from error
    print(f"Validated {len(chunks)} unique chunks from {len(files)} files.")
    if args.dry_run:
        record_count = len({chunk["record_id"] for chunk in chunks})
        print(f"Dry run complete: {record_count} records; no model or database was used.")
        return 0
    ingest(args, chunks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
