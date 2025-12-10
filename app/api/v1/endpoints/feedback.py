from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, Feedback as FeedbackSchema
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=FeedbackSchema)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submit user feedback
    """
    try:
        # Convert Pydantic model to dict, excluding unset values
        feedback_dict = feedback.model_dump(exclude_unset=True)
        db_feedback = Feedback(**feedback_dict)
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Feedback submitted: ID {db_feedback.id}")
        return db_feedback
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/{feedback_id}", response_model=FeedbackSchema)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """
    Get specific feedback by ID
    """
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.get("/", response_model=List[FeedbackSchema])
def list_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all feedback
    """
    feedback = db.query(Feedback).offset(skip).limit(limit).all()
    return feedback