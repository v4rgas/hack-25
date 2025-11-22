from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    ocid = Column(String, nullable=False, index=True, unique=True)
    title = Column(Text, nullable=False)
    published_date = Column(DateTime, nullable=False)
    parties = Column(JSON, nullable=False)


class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, nullable=False, index=True)
    mp_id = Column(String, nullable=False, index=True)
    rut = Column(String, nullable=False, index=True)
    roles = Column(JSON, nullable=False)
    date = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, unique=True)
    file_hash = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)
