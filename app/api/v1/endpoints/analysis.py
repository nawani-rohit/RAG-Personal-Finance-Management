# app/api/v1/endpoints/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.openai_service import openai_service
from app.services.document_service import document_service
from app.schemas.query import QueryRequest, QueryResponse
from app.db.models.document import Document

router = APIRouter()

@router.post("/query/", response_model=QueryResponse)
async def analyze_documents(
    query: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process natural language query against financial documents"""
    try:
        # Find relevant document chunks
        similar_chunks = await document_service.search_similar_chunks(
            db,
            query.query_text,
            top_k=3
        )
        
        if not similar_chunks:
            return QueryResponse(
                answer="No relevant information found in the documents.",
                relevant_documents=[]
            )
        
        # Get context from similar chunks
        context = [chunk["chunk_text"] for chunk in similar_chunks]
        
        # Get completion from OpenAI
        instruction = """You are a financial analysis assistant. Analyze the provided financial documents 
        and answer the question accurately. If calculations are needed, show your work step by step."""
        
        response = openai_service.get_completion(
            query=query.query_text,
            context=context,
            instruction=instruction
        )
        
        return QueryResponse(
            answer=response,
            relevant_documents=[{
                "title": chunk["title"],
                "relevance": chunk["similarity"],
                "excerpt": chunk["chunk_text"][:200] + "..."
            } for chunk in similar_chunks]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))