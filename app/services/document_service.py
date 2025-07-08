# app/services/document_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
import os
import hashlib
from datetime import datetime
from app.services.openai_service import openai_service
from fastapi import UploadFile, HTTPException
import logging
from app.db.models import Document, DocumentEmbedding
import PyPDF2
import io
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentService:
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx'}
    
    @staticmethod
    def _validate_file(file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in DocumentService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(DocumentService.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (will be validated when reading)
        if hasattr(file, 'size') and file.size > DocumentService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {DocumentService.MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    @staticmethod
    def _extract_text_from_pdf(content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid PDF file or unable to extract text")
    
    @staticmethod
    def _generate_file_hash(content: bytes) -> str:
        """Generate SHA-256 hash of file content for deduplication"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def detect_document_type(text: str) -> str:
        # Heuristic rules
        bank_keywords = ["account number", "statement period", "deposit", "withdrawal", "closing balance"]
        credit_keywords = ["credit card", "payment due", "minimum payment", "credit limit"]
        investment_keywords = ["dividend", "shares", "portfolio", "investment account"]
        tax_keywords = ["irs", "form 1040", "tax year", "w-2", "1099"]

        text_lower = text.lower()
        if any(k in text_lower for k in bank_keywords):
            return "bank_statement"
        if any(k in text_lower for k in credit_keywords):
            return "credit_card"
        if any(k in text_lower for k in investment_keywords):
            return "investment"
        if any(k in text_lower for k in tax_keywords):
            return "tax"

        # Fallback: Use LLM
        prompt = (
            "Classify the following document as one of: Bank Statement, Credit Card Statement, "
            "Investment Document, Tax Document. Only return the type.\n\nDocument:\n" + text[:2000]
        )
        result = openai_service.get_completion(
            query="",
            context=[text],
            instruction=prompt,
            temperature=0.0
        )
        # Normalize result
        result = result.lower()
        if "bank" in result:
            return "bank_statement"
        if "credit" in result:
            return "credit_card"
        if "investment" in result:
            return "investment"
        if "tax" in result:
            return "tax"
        return "unknown"

    @staticmethod
    async def upload_document(
        db: Session,
        file: UploadFile,
        document_type: str = None
    ) -> Document:
        """Upload and process a new document with enhanced validation and processing"""
        try:
            logger.info(f"Starting document upload: {file.filename}")
            
            # Validate file
            DocumentService._validate_file(file)
            
            # Read file content
            content = await file.read()
            
            # Check file size after reading
            if len(content) > DocumentService.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size: {DocumentService.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Generate file hash for deduplication
            file_hash = DocumentService._generate_file_hash(content)
            
            # Check for duplicate files
            existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
            if existing_doc:
                raise HTTPException(status_code=400, detail="This file has already been uploaded")
            
            # Extract text based on file type
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext == '.pdf':
                text_content = DocumentService._extract_text_from_pdf(content)
            else:
                text_content = content.decode('utf-8')
            
            if not text_content.strip():
                raise HTTPException(status_code=400, detail="No text content found in file")
            
            logger.info(f"File content extracted successfully. Size: {len(text_content)} characters")
            
            # Detect document type if not provided
            detected_type = document_type or DocumentService.detect_document_type(text_content)
            logger.info(f"Detected document type: {detected_type}")
            
            # Create document record with enhanced metadata
            document = Document(
                title=file.filename,
                content=text_content,
                file_path=file.filename,
                document_type=detected_type,
                file_hash=file_hash,
                file_size=len(content),
                word_count=len(text_content.split())
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Document record created with ID: {document.id}")
            
            # Process chunks with improved strategy
            chunks = DocumentService._create_smart_chunks(text_content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Process each chunk with better error handling
            successful_chunks = 0
            for i, chunk in enumerate(chunks):
                try:
                    logger.info(f"Processing chunk {i+1} of {len(chunks)}")
                    embedding = openai_service.get_embedding(chunk)
                    
                    if not embedding:
                        logger.warning(f"Failed to generate embedding for chunk {i+1}")
                        continue
                    
                    doc_embedding = DocumentEmbedding(
                        document_id=document.id,
                        embedding=embedding,
                        chunk_text=chunk,
                        chunk_index=i,
                        chunk_size=len(chunk)
                    )
                    
                    db.add(doc_embedding)
                    successful_chunks += 1
                    logger.info(f"Added embedding for chunk {i+1}")
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {i}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Successfully processed {successful_chunks} out of {len(chunks)} chunks")
            
            # Update document with processing metadata
            document.processed_chunks = successful_chunks
            document.processing_status = "completed"
            db.commit()
            
            return document
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in upload_document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    @staticmethod
    def _create_smart_chunks(text: str) -> List[str]:
        """Create chunks with improved text segmentation"""
        chunks = []
        sentences = text.split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip() + "."
            
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > DocumentService.CHUNK_SIZE and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - DocumentService.CHUNK_OVERLAP)
                current_chunk = current_chunk[overlap_start:] + sentence
            else:
                current_chunk += " " + sentence
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks[:20]  # Limit to 20 chunks for performance
    
    @staticmethod
    async def search_similar_chunks(
        db: Session,
        query: str,
        top_k: int = 5,
        document_type: Optional[str] = None
    ) -> List[dict]:
        """Search for similar chunks with enhanced filtering"""
        try:
            logger.info(f"Searching for query: {query}")
            
            # Get query embedding
            query_embedding = openai_service.get_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            logger.info("Generated query embedding")
            
            # Build query with optional document type filter
            db_query = db.query(DocumentEmbedding).join(Document)
            if document_type:
                db_query = db_query.filter(Document.document_type == document_type)
            
            embeddings = db_query.all()
            logger.info(f"Found {len(embeddings)} embeddings to compare")
            
            # Calculate similarities with improved threshold
            similarities = []
            for emb in embeddings:
                if emb.embedding:
                    similarity = openai_service.calculate_similarity(
                        query_embedding,
                        emb.embedding
                    )
                    
                    if similarity > settings.SIMILARITY_THRESHOLD:  # Use config value
                        doc = db.query(Document).filter(Document.id == emb.document_id).first()
                        similarities.append({
                            'chunk_text': emb.chunk_text,
                            'title': doc.title,
                            'document_type': doc.document_type,
                            'similarity': similarity,
                            'chunk_index': emb.chunk_index
                        })
            
            # Sort and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            results = similarities[:top_k]
            
            logger.info(f"Returning {len(results)} similar chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error in search_similar_chunks: {str(e)}", exc_info=True)
            return []

document_service = DocumentService()