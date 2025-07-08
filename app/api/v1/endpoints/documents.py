# app/api/v1/endpoints/documents.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.document_service import document_service
from app.schemas.document import DocumentResponse, DocumentList
from app.db.models.document import Document
from app.db.models.document import DocumentEmbedding

router = APIRouter()

@router.post("/upload/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = None,
    db: Session = Depends(get_db)
):
    """Upload and process a new financial document"""
    try:
        document = await document_service.upload_document(db, file, document_type)
        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type,
            created_at=document.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list/", response_model=List[DocumentList])
async def list_documents(
    document_type: str = None,
    db: Session = Depends(get_db)
):
    """List all uploaded documents with optional filtering by type"""
    query = db.query(Document)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    documents = query.all()
    return documents

@router.delete("/delete/{document_id}/", status_code=204)
async def delete_document(
    document_id: int = Path(..., description="ID of the document to delete"),
    db: Session = Depends(get_db)
):
    """Delete a document and its embeddings from the database by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    # Delete all embeddings for this document
    db.query(DocumentEmbedding).filter(DocumentEmbedding.document_id == document_id).delete()
    # Delete the document itself
    db.delete(document)
    db.commit()
    return