from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.user import User, SubscriptionTier
from app.schemas.user import UserCreate, User
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/{user_id}/upgrade", response_model=User)
def upgrade_user_to_pro(
    user_id: int,
    current_user_is_admin: bool = True,  # In reality, this would come from authentication
    db: Session = Depends(get_db)
):
    """Upgrade a user to the PRO subscription tier"""
    # In a real implementation, you would verify that current_user_is_admin is actually an admin
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Upgrade the user to PRO tier
    db_user.subscription_tier = SubscriptionTier.PRO
    db.commit()
    db.refresh(db_user)
    
    return db_user