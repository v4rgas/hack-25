from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List


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


# LangGraph Workflow schemas
class RankingInput(BaseModel):
    """Input for the ranking agent - tender context"""
    tender_id: str = Field(description="Tender/procurement ID")
    tender_name: str = Field(description="Name of the tender")
    tender_date: str = Field(description="Date of the tender")
    bases: str = Field(description="General tender specifications")
    bases_tecnicas: str = Field(description="Technical specifications")
    additional_context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")


class RankedItem(BaseModel):
    """A single ranked item with risk assessment"""
    tender_id: str = Field(description="Tender/procurement ID")
    risk_score: float = Field(description="Risk score from 0 to 1")
    risk_indicators: List[str] = Field(description="List of identified risk indicators")
    full_context: Dict[str, Any] = Field(description="Complete tender context for investigation")
    ranking_reason: str = Field(description="Explanation of why this was ranked at this position")


class RankingOutput(BaseModel):
    """Output from the ranking agent"""
    ranked_items: List[RankedItem] = Field(description="Top 5 ranked items by risk")
    analysis_summary: str = Field(description="Overall analysis summary")


class FraudDetectionInput(BaseModel):
    """Input for fraud detection agent - single tender to investigate"""
    tender_id: str = Field(description="Tender ID to investigate")
    risk_indicators: List[str] = Field(description="Risk indicators from ranking")
    full_context: Dict[str, Any] = Field(description="Complete context from ranking agent")


class Anomaly(BaseModel):
    """A detected anomaly or fraud indicator"""
    anomaly_name: str = Field(description="Name/type of the anomaly")
    description: str = Field(description="Detailed description of the anomaly")
    evidence: List[str] = Field(description="Supporting evidence from investigation")
    confidence: float = Field(description="Confidence score from 0 to 1")
    affected_documents: List[str] = Field(default_factory=list, description="Documents where anomaly was found")


class FraudDetectionOutput(BaseModel):
    """Output from fraud detection agent"""
    tender_id: str = Field(description="Investigated tender ID")
    is_fraudulent: bool = Field(description="Whether fraud indicators were found")
    anomalies: List[Anomaly] = Field(description="List of detected anomalies")
    investigation_summary: str = Field(description="Summary of the investigation")


class WorkflowState(BaseModel):
    """State management for LangGraph workflow"""
    input_data: RankingInput | None = None
    ranked_items: List[RankedItem] = Field(default_factory=list)
    investigation_results: List[FraudDetectionOutput] = Field(default_factory=list)
    final_fraud_cases: List[FraudDetectionOutput] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
