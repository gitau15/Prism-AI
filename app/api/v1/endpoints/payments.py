from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.daraja import DarajaService
from app.schemas.payment import InitiatePaymentRequest, InitiatePaymentResponse, DarajaCallback
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, SubscriptionTier
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/initiate", response_model=InitiatePaymentResponse)
def initiate_payment(
    payment_request: InitiatePaymentRequest,
    user_id: int = 1,  # In reality, this would come from authentication
    db: Session = Depends(get_db)
):
    """
    Initiate M-Pesa STK Push for user to upgrade to Pro tier
    
    Args:
        payment_request: Contains user's phone number and amount
        user_id: ID of the authenticated user
        db: Database session
        
    Returns:
        InitiatePaymentResponse: Contains checkout request ID
    """
    try:
        # Initialize Daraja service
        daraja_service = DarajaService()
        
        # Initiate STK Push
        response = daraja_service.initiate_stk_push(
            phone_number=payment_request.phone_number,
            amount=payment_request.amount,
            account_reference=f"PRISM_AI_PRO_{user_id}",
            transaction_desc="Prism AI Pro Subscription"
        )
        
        # Create payment record
        db_payment = Payment(
            user_id=user_id,
            checkout_request_id=response["CheckoutRequestID"],
            merchant_request_id=response["MerchantRequestID"],
            amount=payment_request.amount,
            phone_number=payment_request.phone_number,
            status=PaymentStatus.PENDING
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        return InitiatePaymentResponse(
            checkout_request_id=response["CheckoutRequestID"],
            message="STK Push sent successfully. Please check your phone to complete payment."
        )
        
    except Exception as e:
        logger.error(f"Error initiating payment for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate payment: {str(e)}")

@router.post("/daraja/callback")
async def daraja_callback(
    callback_data: DarajaCallback,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle callback from Daraja API after STK Push
    
    Args:
        callback_data: Data from Daraja callback
        request: HTTP request object (for logging IP address)
        db: Database session
        
    Returns:
        dict: Acknowledgment response for Daraja
    """
    try:
        # Log the callback for security/auditing purposes
        client_ip = request.client.host if request.client else "Unknown"
        logger.info(f"Daraja callback received from IP: {client_ip}")
        logger.info(f"Callback data: {callback_data}")
        
        # Extract relevant data from callback
        if "Body" not in callback_data.Body or "stkCallback" not in callback_data.Body["Body"]:
            logger.error("Invalid callback format")
            return {"ResultCode": 1, "ResultDesc": "Invalid callback format"}
        
        stk_callback = callback_data.Body["Body"]["stkCallback"]
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        # Find the payment record
        db_payment = db.query(Payment).filter(
            Payment.checkout_request_id == checkout_request_id
        ).first()
        
        if not db_payment:
            logger.error(f"Payment record not found for CheckoutRequestID: {checkout_request_id}")
            return {"ResultCode": 1, "ResultDesc": "Payment record not found"}
        
        # Update payment record
        db_payment.result_code = result_code
        db_payment.result_desc = result_desc
        
        if result_code == 0:
            # Payment successful
            db_payment.status = PaymentStatus.COMPLETED
            
            # Upgrade user to PRO tier
            db_user = db.query(User).filter(User.id == db_payment.user_id).first()
            if db_user:
                db_user.subscription_tier = SubscriptionTier.PRO
                logger.info(f"User {db_user.id} upgraded to PRO tier")
            else:
                logger.error(f"User {db_payment.user_id} not found for payment {db_payment.id}")
        else:
            # Payment failed
            db_payment.status = PaymentStatus.FAILED
            logger.info(f"Payment {db_payment.id} failed with result code {result_code}")
        
        # Commit changes
        db.commit()
        
        # Return acknowledgment to Daraja
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
    except Exception as e:
        logger.error(f"Error processing Daraja callback: {str(e)}")
        # Even in case of error, we must return a valid response to Daraja
        return {"ResultCode": 0, "ResultDesc": "Accepted"}