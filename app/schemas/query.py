# app/schemas/query.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    query_text: str
    document_type: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    relevant_documents: List[dict]
    processing_time: Optional[float] = None

class AnalyticsResponse(BaseModel):
    documents: dict
    queries: dict

class QueryHistoryItem(BaseModel):
    id: int
    query_text: str
    answer: str
    processing_time: float
    created_at: datetime
    relevant_documents: List[dict]

class FinancialAnalysisResponse(BaseModel):
    document_id: Optional[int] = None
    document_title: Optional[str] = None
    analysis_type: Optional[str] = None
    document_count: Optional[int] = None
    analysis: dict

class EntityExtractionResponse(BaseModel):
    document_id: int
    document_title: str
    entities: dict