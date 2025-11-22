#!/usr/bin/env python3
"""Load companies CSV data into the database."""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

CSV_PATH = Path(__file__).parent.parent / "datasets" / "companies_with_registration_date.csv"
BATCH_SIZE = 10000


def load_companies():
    """Load companies from CSV into database."""
    with engine.connect() as conn:
        # Clear existing data
        conn.execute(text("TRUNCATE TABLE companies"))

        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []
            total = 0

            for row in reader:
                batch.append({
                    "rut": str(row["rut"]),
                    "company_name": row["company_name"],
                    "first_registration_date": row["first_registration_date"] or None
                })

                if len(batch) >= BATCH_SIZE:
                    conn.execute(
                        text("""
                            INSERT INTO companies (rut, company_name, first_registration_date)
                            VALUES (:rut, :company_name, :first_registration_date)
                            ON CONFLICT (rut) DO UPDATE SET
                                company_name = EXCLUDED.company_name,
                                first_registration_date = EXCLUDED.first_registration_date
                        """),
                        batch
                    )
                    total += len(batch)
                    print(f"Inserted {total} rows...")
                    batch = []

            # Insert remaining
            if batch:
                conn.execute(
                    text("""
                        INSERT INTO companies (rut, company_name, first_registration_date)
                        VALUES (:rut, :company_name, :first_registration_date)
                        ON CONFLICT (rut) DO UPDATE SET
                            company_name = EXCLUDED.company_name,
                            first_registration_date = EXCLUDED.first_registration_date
                    """),
                    batch
                )
                total += len(batch)

            conn.commit()
            print(f"Done! Loaded {total} companies.")


if __name__ == "__main__":
    load_companies()
