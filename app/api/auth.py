from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, Token
from utils.security import (
    get_password_hash, create_access_token,
    verify_password
)

router = APIRouter()


@router.post("/register", response_model=UserInDB)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email or phone already exists
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.phone_number:
        db_user_phone = db.query(User).filter(User.phone_number == user.phone_number).first()
        if db_user_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Hash password
    hashed_password = get_password_hash(user.password)

    # Create user
    db_user = User(
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password,
        auth_provider="email",
        account_status="active"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        (User.email == form_data.username) |
        (User.phone_number == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.user_id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
