from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, Document, DocumentProcessingRequest

router = APIRouter()

@router.post("/", response_model=Document)
def upload_document(
    file: UploadFile = File(...),
    user_id: int = 1,  # In reality, this would come from authentication
    db: Session = Depends(get_db)
):
    """Upload a document for processing"""
    # Save file to storage (placeholder)
    # In reality, this would save to cloud storage or local storage
    
    db_doc = Document(
        user_id=user_id,
        filename=file.filename,
        file_type=file.content_type,
        size=0,  # Would get actual file size
        storage_provider="local",
        storage_path=f"/uploads/{file.filename}",
        processed=False
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/{document_id}", response_model=Document)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.get("/", response_model=List[Document])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all documents"""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@router.post("/{document_id}/process")
def process_document(request: DocumentProcessingRequest, db: Session = Depends(get_db)):
    """Process a document through the ingestion pipeline"""
    db_doc = db.query(Document).filter(Document.id == request.document_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # This would trigger the document processing pipeline:
    # 1. Parse the document based on file type
    # 2. Chunk the document intelligently
    # 3. Generate embeddings
    # 4. Store in vector database
    
    # For now, just marking as processed
    db_doc.processed = True
    db.commit()
    db.refresh(db_doc)
    
    return {"message": f"Document {request.document_id} processing started"}