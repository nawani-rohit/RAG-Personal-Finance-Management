from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    title: str
    document_type: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentList(DocumentResponse):
    file_path: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True