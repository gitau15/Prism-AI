from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
import enum

class SubscriptionTier(str, enum.Enum):
    EXPLORER = "EXPLORER"
    PRO = "PRO"

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    subscription_tier: SubscriptionTier = SubscriptionTier.EXPLORER

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    pages_processed_this_month: int = 0
    queries_this_month: int = 0
    last_usage_reset_date: date = date.today()
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None