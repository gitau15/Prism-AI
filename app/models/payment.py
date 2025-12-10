from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database.base import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkout_request_id = Column(String, unique=True, nullable=False)
    merchant_request_id = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    result_code = Column(Integer, nullable=True)
    result_desc = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())