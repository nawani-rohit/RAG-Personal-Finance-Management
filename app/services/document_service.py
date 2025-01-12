# app/services/document_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from app.services.openai_service import openai_service
from fastapi import UploadFile, HTTPException
import logging
from app.db.models import Document, DocumentEmbedding  # Updated import


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentService:
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    @staticmethod
    async def upload_document(
        db: Session,
        file: UploadFile,
        document_type: "bank_statements"
    ) -> Document:
        """Upload and process a new document"""
        try:
            logger.info(f"Starting document upload: {file.filename}")
            
            # Read file content
            content = await file.read()
            text_content = content.decode()
            
            logger.info(f"File content read successfully. Size: {len(text_content)} characters")
                
            # Create document record
            document = Document(
                title=file.filename,
                content=text_content,
                file_path=file.filename,
                document_type=document_type
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Document record created with ID: {document.id}")
            
            # Process chunks immediately
            chunks = DocumentService._create_chunks(text_content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                try:
                    logger.info(f"Processing chunk {i+1} of {len(chunks)}")
                    embedding = openai_service.get_embedding(chunk)
                    
                    doc_embedding = DocumentEmbedding(
                        document_id=document.id,
                        embedding=embedding,
                        chunk_text=chunk,
                        chunk_index=i
                    )
                    
                    db.add(doc_embedding)
                    logger.info(f"Added embedding for chunk {i+1}")
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {i}: {str(e)}")
                    continue
            
            db.commit()
            logger.info("All chunks processed and saved")
            
            # Verify embeddings were saved
            embedding_count = db.query(DocumentEmbedding).filter(
                DocumentEmbedding.document_id == document.id
            ).count()
            logger.info(f"Verified {embedding_count} embeddings saved for document {document.id}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error in upload_document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def _create_chunks(text: str) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + DocumentService.CHUNK_SIZE
            if end > len(text):
                end = len(text)
            
            # Try to find a good breaking point
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start:
                end = break_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - DocumentService.CHUNK_OVERLAP
            if start < 0:
                start = 0
            
            # Limit the number of chunks for testing
            if len(chunks) >= 10:
                break
        
        return chunks
    
    @staticmethod
    async def search_similar_chunks(
        db: Session,
        query: str,
        top_k: int = 3
    ) -> List[dict]:
        """Search for similar chunks"""
        try:
            logger.info(f"Searching for query: {query}")
            
            # Debug: Check documents
            doc_count = db.query(Document).count()
            logger.info(f"Total documents in database: {doc_count}")
            
            # Debug: Check embeddings
            emb_count = db.query(DocumentEmbedding).count()
            logger.info(f"Total embeddings in database: {emb_count}")
            
            # Get query embedding
            query_embedding = openai_service.get_embedding(query)
            logger.info("Generated query embedding")
            
            # Get all embeddings first
            query = db.query(DocumentEmbedding).join(Document)
            
            
            embeddings = query.all()
            logger.info(f"Found {len(embeddings)} embeddings to compare")
            
            # Calculate similarities
            similarities = []
            for emb in embeddings:
                if emb.embedding:
                    similarity = openai_service.calculate_similarity(
                        query_embedding,
                        emb.embedding
                    )
                    
                    if similarity > 0.3:  # Only include reasonably similar chunks
                        doc = db.query(Document).filter(Document.id == emb.document_id).first()
                        similarities.append({
                            'chunk_text': emb.chunk_text,
                            'title': doc.title,
                            'similarity': similarity
                        })
            
            # Sort and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            results = similarities[:top_k]
            
            logger.info(f"Returning {len(results)} similar chunks")
            for idx, res in enumerate(results):
                logger.info(f"Similarity {idx+1}: {res['similarity']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search_similar_chunks: {str(e)}", exc_info=True)
            return []

document_service = DocumentService()