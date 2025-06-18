from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.admin import Admin
from app.models.user import User
from app.schemas.user import TokenData
from app.schemas.admin import AdminToken

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/login")


# --------------------------
# Common Security Functions
# --------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --------------------------
# User Authentication
# --------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.account_status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# --------------------------
# Admin Authentication
# --------------------------

def create_admin_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ADMIN_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_admin(
        token: str = Depends(admin_oauth2_scheme),
        db: Session = Depends(get_db)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.ADMIN_SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: int = payload.get("admin_id")
        if admin_id is None:
            raise credentials_exception
        token_data = {"admin_id": admin_id}
    except JWTError:
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.admin_id == token_data["admin_id"]).first()
    if admin is None:
        raise credentials_exception

    return admin


async def get_current_active_admin(
        current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    if not current_admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin account")
    return current_admin


async def get_current_super_admin(
        current_admin: Admin = Depends(get_current_active_admin)
) -> Admin:
    if current_admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_admin


# --------------------------
# Password Verification
# --------------------------

def verify_admin_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_admin_password_hash(password: str) -> str:
    return pwd_context.hash(password)