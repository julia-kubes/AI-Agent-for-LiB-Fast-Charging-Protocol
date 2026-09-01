import csv
import os
from pathlib import Path

import psycopg


CSV_PATH = Path(__file__).with_name("battery_paper_metadata.csv")

COLUMNS = [
    "record_id",
    "doi",
    "battery_chemistry_cathode",
    "manufacturer",
    "form_factor",
    "ambient_temperature_experiments",
    "state_of_charge_mentioned",
    "paper_title",
    "paper_type",
    "review_notes",
]


def clean(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return None if not value or value.lower() == "n/s" else value


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL is not set.")

with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
    rows = list(csv.DictReader(stream))

with psycopg.connect(database_url) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_metadata (
                record_id TEXT PRIMARY KEY,
                doi TEXT,
                battery_chemistry_cathode TEXT,
                manufacturer TEXT,
                form_factor TEXT,
                ambient_temperature_experiments TEXT,
                state_of_charge_mentioned TEXT,
                paper_title TEXT,
                paper_type TEXT,
                review_notes TEXT,
                updated_at TIMESTAMPTZ NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            ALTER TABLE paper_metadata
            ADD COLUMN IF NOT EXISTS paper_type TEXT
            """
        )

        cursor.execute(
            """
            SELECT DISTINCT record_id
            FROM rag_chunks
            """
        )
        chunk_record_ids = {row[0] for row in cursor.fetchall()}
        csv_record_ids = {row["record_id"].strip() for row in rows}

        missing_from_chunks = csv_record_ids - chunk_record_ids
        if missing_from_chunks:
            raise RuntimeError(
                "CSV record IDs not found in rag_chunks: "
                + ", ".join(sorted(missing_from_chunks))
            )

        statement = """
            INSERT INTO paper_metadata (
                record_id,
                doi,
                battery_chemistry_cathode,
                manufacturer,
                form_factor,
                ambient_temperature_experiments,
                state_of_charge_mentioned,
                paper_title,
                paper_type,
                review_notes
            )
            VALUES (
                %(record_id)s,
                %(doi)s,
                %(battery_chemistry_cathode)s,
                %(manufacturer)s,
                %(form_factor)s,
                %(ambient_temperature_experiments)s,
                %(state_of_charge_mentioned)s,
                %(paper_title)s,
                %(paper_type)s,
                %(review_notes)s
            )
            ON CONFLICT (record_id) DO UPDATE SET
                doi = EXCLUDED.doi,
                battery_chemistry_cathode =
                    EXCLUDED.battery_chemistry_cathode,
                manufacturer = EXCLUDED.manufacturer,
                form_factor = EXCLUDED.form_factor,
                ambient_temperature_experiments =
                    EXCLUDED.ambient_temperature_experiments,
                state_of_charge_mentioned =
                    EXCLUDED.state_of_charge_mentioned,
                paper_title = EXCLUDED.paper_title,
                paper_type = EXCLUDED.paper_type,
                review_notes = EXCLUDED.review_notes,
                updated_at = CURRENT_TIMESTAMP
        """

        cleaned_rows = [
            {column: clean(row.get(column)) for column in COLUMNS}
            for row in rows
        ]
        cursor.executemany(statement, cleaned_rows)

    connection.commit()

print(f"Imported or updated {len(rows)} paper metadata records.")
