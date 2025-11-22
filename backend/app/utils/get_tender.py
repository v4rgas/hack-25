import requests
from pydantic import BaseModel
from datetime import datetime

class TenderDate(BaseModel):
    publish: datetime
    close: datetime


class TenderEvaluationCriteria(BaseModel):
    item_name: str
    observation: str
    ponderation: int
    row_index: int
    createdAt: datetime
    updatedAt: datetime


class TenderGuarantee(BaseModel):
    title: str
    description: str
    beneficiary: str
    due_date: datetime
    amount: float
    currency: str
    restitution_way: str
    gloss: str
    createdAt: datetime
    updatedAt: datetime


class Institution(BaseModel):
    code: str
    name: str
    category: str
    createdAt: datetime
    updatedAt: datetime


class Organization(BaseModel):
    tax_number: str
    name: str
    createdAt: datetime
    updatedAt: datetime
    institution_code: str
    institution: Institution


class OrgUnit(BaseModel):
    code: str
    name: str
    address: str
    city: str
    region: str
    createdAt: datetime
    updatedAt: datetime
    organization_tax_number: str


class TenderPurchaseData(BaseModel):
    id: int
    createdAt: datetime
    updatedAt: datetime
    organization_tax_number: str
    unit_code: str
    tender_id: str
    buying_user_id: str
    organization: Organization
    orgUnit: OrgUnit


class TenderResponse(BaseModel):
    tenderId: str
    name: str
    description: str
    status: str
    statusCode: int
    TenderDate: TenderDate
    TenderEvaluationCriteria: list[TenderEvaluationCriteria]
    TenderGuarantees: list[TenderGuarantee]
    tenderPurchaseData: TenderPurchaseData


def get_tender(tender_id: str) -> TenderResponse:
    url = f"https://api.licitalab.cl/free/tender/{tender_id}"
    
    response = requests.get(url, timeout=30.0)
    response.raise_for_status()
    return TenderResponse.model_validate(response.json())

