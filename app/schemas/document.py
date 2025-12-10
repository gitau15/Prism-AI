from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    size: int
    storage_provider: str

class DocumentCreate(DocumentBase):
    user_id: int
    storage_path: str

class DocumentUpdate(DocumentBase):
    processed: bool = False

class DocumentInDBBase(DocumentBase):
    id: int
    user_id: int
    storage_path: str
    processed: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    pass

class DocumentProcessingRequest(BaseModel):
    document_id: int

class QueryRequest(BaseModel):
    query: str
    user_id: int

class QueryResponse(BaseModel):
    response: str
    sources: List[str]