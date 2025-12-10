from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.document import Document
from app.database.base import Base
from app.utils.document_parser import parse_document
from app.utils.document_chunker import chunk_document
from app.utils.embedder import Embedder
from app.utils.vector_store import VectorStore
import logging

# Set up logging
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_document_task(self, document_id: int, file_path: str, file_type: str):
    """
    Celery task to process a document in the background.
    This task creates its own database session and handles the full document processing pipeline.
    """
    logger.info(f"Starting document processing for document_id: {document_id}")
    
    try:
        # Create a new database session for this task
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get the document from the database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document with id {document_id} not found")
            return {"status": "error", "message": f"Document with id {document_id} not found"}
        
        # Update document status to processing
        document.processed = False  # Using processed as a status indicator
        db.commit()
        
        # Process the document
        logger.info(f"Parsing document {document_id}...")
        text_content = parse_document(file_path, file_type)
        
        # Chunk the document
        logger.info("Chunking document...")
        chunks = chunk_document(text_content, method="paragraph")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embedder = Embedder()
        embeddings = embedder.embed_batch(chunks)
        
        # Store in vector database
        logger.info("Storing in vector database...")
        vector_store = VectorStore()
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        
        vector_store.add_documents(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )
        
        # Update document status to processed
        document.processed = True
        db.commit()
        db.refresh(document)
        
        # Close the database session
        db.close()
        
        logger.info(f"Document processing completed for document_id: {document_id}")
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        # Log the error and update document status
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update document status to failed
        try:
            engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.processed = False
                db.commit()
            db.close()
        except Exception as db_error:
            logger.error(f"Error updating document status: {str(db_error)}")
        
        # Re-raise the exception so Celery knows the task failed
        raise self.retry(exc=e, countdown=60, max_retries=3)