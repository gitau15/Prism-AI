from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Enum
from sqlalchemy.sql import func
from app.database.base import Base
import enum
from datetime import date

class SubscriptionTier(str, enum.Enum):
    EXPLORER = "EXPLORER"
    PRO = "PRO"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Usage tracking fields
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.EXPLORER)
    pages_processed_this_month = Column(Integer, default=0)
    queries_this_month = Column(Integer, default=0)
    last_usage_reset_date = Column(Date, default=date.today)