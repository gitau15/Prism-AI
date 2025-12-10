from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, Document, DocumentProcessingRequest, TaskStatusResponse
from app.core.celery_tasks import process_document_task
from app.core.usage import check_usage_limits
import os
import uuid

router = APIRouter()

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = 1,  # In reality, this would come from authentication
    db: Session = Depends(get_db)
):
    """Upload a document for processing (non-blocking)"""
    # Check usage limits for page processing
    check_usage_limits(user_id, "page", db)
    
    # Create a unique filename to avoid conflicts
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"./data/uploads/{unique_filename}"
    
    # Ensure the upload directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file to storage
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create document record in database
    db_doc = Document(
        user_id=user_id,
        filename=file.filename,
        file_type=file.content_type,
        size=len(content),
        storage_provider="local",
        storage_path=file_path,
        processed=False
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Dispatch background task to process the document
    task = process_document_task.delay(db_doc.id, file_path, file.content_type)
    
    # Return task information immediately
    return {
        "message": "Document processing started",
        "task_id": task.id,
        "document_id": db_doc.id
    }

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
    
    # For backward compatibility, but in practice, this endpoint should not be used
    # since processing is now handled automatically after upload
    return {"message": f"Document {request.document_id} processing started"}

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Get the status of a background task"""
    from celery.result import AsyncResult
    from app.core.celery_app import celery_app
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }