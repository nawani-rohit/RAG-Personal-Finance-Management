# app/schemas/query.py
from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query_text: str

class RelevantDocument(BaseModel):
    title: str
    relevance: float
    excerpt: str

class QueryResponse(BaseModel):
    answer: str
    relevant_documents: List[RelevantDocument]