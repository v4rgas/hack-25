from pydantic import BaseModel
from datetime import datetime


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True


# ChileCompra schemas
class Party(BaseModel):
    mp_id: str
    rut: str
    roles: list[str]
    date: datetime | None = None
    amount: float | None = None
    currency: str | None = None


class Tender(BaseModel):
    ocid: str
    title: str
    publishedDate: datetime
    parties: list[Party]
