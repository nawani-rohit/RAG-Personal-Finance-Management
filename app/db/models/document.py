# app/db/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from ..session import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    file_path = Column(String)
    document_type = Column(String, index=True)
    file_hash = Column(String, unique=True, index=True)  # For deduplication
    file_size = Column(Integer)  # File size in bytes
    word_count = Column(Integer)  # Number of words in document
    processed_chunks = Column(Integer, default=0)  # Number of successfully processed chunks
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    embedding = Column(ARRAY(FLOAT))
    chunk_text = Column(Text)
    chunk_index = Column(Integer)
    chunk_size = Column(Integer)  # Size of chunk in characters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="embeddings")

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    relevant_documents = Column(Text)  # JSON string of relevant documents
    processing_time = Column(FLOAT)  # Time taken to process query in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional user tracking (for future authentication)
    user_id = Column(String, nullable=True, index=True)
    session_id = Column(String, nullable=True, index=True)