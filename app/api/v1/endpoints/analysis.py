# app/api/v1/endpoints/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import time
import json
from app.db.session import get_db
from app.services.openai_service import openai_service
from app.services.document_service import document_service
from app.schemas.query import QueryRequest, QueryResponse
from app.db.models.document import Document, QueryHistory

router = APIRouter()

@router.post("/query/", response_model=QueryResponse)
async def analyze_documents(
    query: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process natural language query against financial documents with enhanced tracking"""
    start_time = time.time()
    
    try:
        # Find relevant document chunks
        similar_chunks = await document_service.search_similar_chunks(
            db,
            query.query_text,
            top_k=5
        )
        
        if not similar_chunks:
            processing_time = time.time() - start_time
            
            # Log query even if no results found
            query_history = QueryHistory(
                query_text=query.query_text,
                answer="No relevant information found in the documents.",
                relevant_documents=json.dumps([]),
                processing_time=processing_time
            )
            db.add(query_history)
            db.commit()
            
            return QueryResponse(
                answer="No relevant information found in the documents.",
                relevant_documents=[],
                processing_time=processing_time
            )
        
        # Get context from similar chunks
        context = [chunk["chunk_text"] for chunk in similar_chunks]
        
        # Get completion from OpenAI with enhanced prompting
        instruction = """You are a professional financial analyst assistant. Analyze the provided financial documents 
        and answer the question accurately. If calculations are needed, show your work step by step.
        Always provide specific numbers and dates when available."""
        
        response = openai_service.get_completion(
            query=query.query_text,
            context=context,
            instruction=instruction,
            temperature=0.3
        )
        
        processing_time = time.time() - start_time
        
        # Prepare relevant documents for response
        relevant_docs = [{
            "title": chunk["title"],
            "document_type": chunk.get("document_type", "unknown"),
            "relevance": chunk["similarity"],
            "excerpt": chunk["chunk_text"][:200] + "..." if len(chunk["chunk_text"]) > 200 else chunk["chunk_text"]
        } for chunk in similar_chunks]
        
        # Log query history
        query_history = QueryHistory(
            query_text=query.query_text,
            answer=response,
            relevant_documents=json.dumps(relevant_docs),
            processing_time=processing_time
        )
        db.add(query_history)
        db.commit()
        
        return QueryResponse(
            answer=response,
            relevant_documents=relevant_docs,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error processing query: {str(e)}"
        
        # Log error in query history
        query_history = QueryHistory(
            query_text=query.query_text,
            answer=error_msg,
            relevant_documents=json.dumps([]),
            processing_time=processing_time
        )
        db.add(query_history)
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-trends/")
async def analyze_financial_trends(
    document_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Analyze financial trends across documents or specific document"""
    try:
        if document_id:
            # Analyze specific document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            analysis = openai_service.analyze_financial_trends(document.content)
            return {
                "document_id": document_id,
                "document_title": document.title,
                "analysis": analysis
            }
        else:
            # Analyze all documents
            documents = db.query(Document).all()
            if not documents:
                raise HTTPException(status_code=404, detail="No documents found")
            
            combined_content = "\n\n".join([doc.content for doc in documents])
            analysis = openai_service.analyze_financial_trends(combined_content)
            
            return {
                "analysis_type": "all_documents",
                "document_count": len(documents),
                "analysis": analysis
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-entities/")
async def extract_financial_entities(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Extract financial entities from a specific document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        entities = openai_service.extract_financial_entities(document.content)
        
        return {
            "document_id": document_id,
            "document_title": document.title,
            "entities": entities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query-history/")
async def get_query_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent query history"""
    try:
        history = db.query(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(limit).all()
        
        return [{
            "id": item.id,
            "query_text": item.query_text,
            "answer": item.answer,
            "processing_time": item.processing_time,
            "created_at": item.created_at,
            "relevant_documents": json.loads(item.relevant_documents) if item.relevant_documents else []
        } for item in history]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/")
async def get_analytics(
    db: Session = Depends(get_db)
):
    """Get system analytics and statistics"""
    try:
        # Document statistics
        total_documents = db.query(Document).count()
        documents_by_type = db.query(Document.document_type, func.count(Document.id)).group_by(Document.document_type).all() or []
        documents_by_type_dict = {k or 'Unknown': v for k, v in documents_by_type}
        
        # Query statistics
        total_queries = db.query(QueryHistory).count()
        avg_processing_time = db.query(func.avg(QueryHistory.processing_time)).scalar() or 0
        
        # Recent activity
        recent_queries = db.query(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(5).all() or []
        recent_documents = db.query(Document).order_by(Document.created_at.desc()).limit(5).all() or []
        
        return {
            "documents": {
                "total": total_documents,
                "by_type": documents_by_type_dict,
                "recent": [{"id": doc.id, "title": doc.title, "type": doc.document_type, "created_at": doc.created_at} for doc in recent_documents]
            },
            "queries": {
                "total": total_queries,
                "average_processing_time": round(avg_processing_time, 3),
                "recent": [{"query": q.query_text, "processing_time": q.processing_time, "created_at": q.created_at} for q in recent_queries]
            }
        }
        
    except Exception as e:
        import logging
        logging.error(f"Analytics endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))