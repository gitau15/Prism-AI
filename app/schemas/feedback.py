from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    rating: int
    comment: Optional[str] = None
    feature_request: Optional[str] = None
    bug_report: Optional[str] = None
    user_id: Optional[int] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True