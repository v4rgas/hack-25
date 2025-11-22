import json
import hashlib
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Tender, Party, FileMetadata


def get_data_path() -> Path:
    return Path(__file__).parent.parent / "datasets" / "chilecompra_single_suppliers.jsonl"


def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def import_data(db: Session) -> dict:
    """Import JSONL data into database. Returns status."""
    data_path = get_data_path()

    if not data_path.exists():
        return {"status": "error", "message": f"File not found: {data_path}"}

    # Check if file has changed
    current_hash = get_file_hash(data_path)
    existing = db.query(FileMetadata).filter(FileMetadata.filename == str(data_path)).first()

    if existing and existing.file_hash == current_hash:
        return {"status": "skipped", "message": "File unchanged, no import needed"}

    # Clear existing data
    db.execute(text("TRUNCATE TABLE tenders, parties RESTART IDENTITY"))

    # Process file in chunks
    batch_size = 5000
    tender_batch = []
    party_batch = []
    total_lines = 0
    tender_id = 0

    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            data = json.loads(line)
            total_lines += 1
            tender_id += 1

            tender_batch.append({
                "id": tender_id,
                "ocid": data["ocid"],
                "title": data["title"],
                "published_date": datetime.fromisoformat(data["publishedDate"].replace("Z", "+00:00")),
                "parties": data["parties"]
            })

            for party in data["parties"]:
                party_date = None
                if party.get("date"):
                    party_date = datetime.fromisoformat(party["date"].replace("Z", "+00:00"))

                party_batch.append({
                    "tender_id": tender_id,
                    "mp_id": party["mp_id"],
                    "rut": party["rut"],
                    "roles": party["roles"],
                    "date": party_date,
                    "amount": party.get("amount"),
                    "currency": party.get("currency")
                })

            if len(tender_batch) >= batch_size:
                db.bulk_insert_mappings(Tender, tender_batch)
                db.bulk_insert_mappings(Party, party_batch)
                tender_batch = []
                party_batch = []

        if tender_batch:
            db.bulk_insert_mappings(Tender, tender_batch)
        if party_batch:
            db.bulk_insert_mappings(Party, party_batch)

    # Update file metadata
    if existing:
        existing.file_hash = current_hash
        existing.processed_at = datetime.utcnow()
    else:
        db.add(FileMetadata(
            filename=str(data_path),
            file_hash=current_hash,
            processed_at=datetime.utcnow()
        ))

    db.commit()

    return {
        "status": "success",
        "message": f"Imported {total_lines} tenders"
    }


