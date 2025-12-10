from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User, SubscriptionTier
from app.core.config import settings
from datetime import date, timedelta
import calendar

def check_usage_limits(
    user_id: int,
    increment_type: str,  # "page" or "query"
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency to check user usage limits.
    
    Args:
        user_id: The ID of the user making the request
        increment_type: Type of usage to check/increment ("page" or "query")
        db: Database session
    
    Raises:
        HTTPException: If the user has exceeded their usage limits
    """
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if we need to reset the usage counters (monthly reset)
    today = date.today()
    if user.last_usage_reset_date:
        # Check if the last reset was in a previous month
        if (today.year > user.last_usage_reset_date.year or
            (today.year == user.last_usage_reset_date.year and 
             today.month > user.last_usage_reset_date.month)):
            # Reset counters
            user.pages_processed_this_month = 0
            user.queries_this_month = 0
            user.last_usage_reset_date = today
            db.commit()
    else:
        # Initialize the reset date if it doesn't exist
        user.last_usage_reset_date = today
        db.commit()
    
    # Get the limits for the user's subscription tier
    tier_name = user.subscription_tier.value
    limits = settings.USAGE_LIMITS.get(tier_name, settings.USAGE_LIMITS["EXPLORER"])
    
    # Check the appropriate limit based on increment_type
    if increment_type == "page":
        if user.pages_processed_this_month >= limits["max_pages_per_month"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You have reached your monthly page processing limit ({limits['max_pages_per_month']} pages). Please upgrade to the Pro plan."
            )
        # Increment the page counter
        user.pages_processed_this_month += 1
    elif increment_type == "query":
        if user.queries_this_month >= limits["max_queries_per_month"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You have reached your monthly query limit ({limits['max_queries_per_month']} queries). Please upgrade to the Pro plan."
            )
        # Increment the query counter
        user.queries_this_month += 1
    else:
        raise HTTPException(status_code=500, detail="Invalid increment_type specified")
    
    # Commit the changes to the database
    db.commit()
    
    # Return the user object for further use if needed
    return user