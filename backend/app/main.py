from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.tools.read_supplier_attachments import (
    download_buyer_attachment_by_tender_id_and_row_id,
    read_buyer_attachments_table,
)
from app.database import get_db
from app.models import Tender, Party
from app.chilecompra import import_data
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI(title="API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok"}


# Graph endpoints
@app.get("/api/import")
def run_import(db: Session = Depends(get_db)):
    """Import data from JSONL file into database."""
    return import_data(db)


@app.get("/api/tenders")
def get_tenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of tenders."""
    total = db.query(Tender).count()
    tenders = db.query(Tender).offset(skip).limit(limit).all()
    return {"total": total, "tenders": tenders}


@app.get("/api/tenders/{tender_id}")
def get_tender(tender_id: int, db: Session = Depends(get_db)):
    """Get a specific tender with its parties."""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        return {"error": "Tender not found"}
    parties = db.query(Party).filter(Party.tender_id == tender_id).all()
    return {"tender": tender, "parties": parties}


@app.get("/api/tenders/{tender_id}/buyer-attachments-table")
def get_buyer_attachments_table(tender_id: str):
    return read_buyer_attachments_table(tender_id)


@app.get("/api/tenders/{tender_id}/download-attachment/{row_id}")
def download_attachment(tender_id: str, row_id: int):
    content = download_buyer_attachment_by_tender_id_and_row_id(tender_id, row_id)
    return Response(content=content, media_type="application/octet-stream")


@app.get("/api/parties")
def get_parties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of parties."""
    parties = db.query(Party).offset(skip).limit(limit).all()
    return parties
