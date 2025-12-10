from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PaymentBase(BaseModel):
    amount: int
    phone_number: str

class PaymentCreate(PaymentBase):
    user_id: int

class PaymentUpdate(BaseModel):
    status: PaymentStatus
    result_code: Optional[int] = None
    result_desc: Optional[str] = None

class PaymentInDBBase(PaymentBase):
    id: int
    user_id: int
    checkout_request_id: str
    merchant_request_id: str
    status: PaymentStatus
    result_code: Optional[int] = None
    result_desc: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Payment(PaymentInDBBase):
    pass

class InitiatePaymentRequest(BaseModel):
    phone_number: str
    amount: int = 1000  # Default amount for Pro subscription

class InitiatePaymentResponse(BaseModel):
    checkout_request_id: str
    message: str

class DarajaCallback(BaseModel):
    Body: dict