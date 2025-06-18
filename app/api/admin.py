from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
from app.models.admin import Admin
from app.models.security import UserReport
from app.models.user import User
from app.schemas.admin import AdminCreate, AdminInDB, AdminLogin, AdminToken, AdminUpdate
from app.schemas.user import UserInDB
from app.schemas.security import UserReportWithUsers
from app.database import get_db
from utils.security import (
    get_admin_password_hash, verify_admin_password,
    create_admin_access_token, get_current_admin,
    get_current_active_admin, get_current_super_admin
)
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=AdminInDB)
def register_admin(
        admin: AdminCreate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_super_admin)
):
    # Check if admin already exists
    db_admin = db.query(Admin).filter(
        (Admin.username == admin.username) |
        (Admin.email == admin.email)
    ).first()

    if db_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    # Hash password
    hashed_password = get_admin_password_hash(admin.password)

    # Create admin
    new_admin = Admin(
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        password_hash=hashed_password,
        role=admin.role
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin


@router.post("/login", response_model=AdminToken)
def login_admin(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()

    if not admin or not verify_admin_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_admin_access_token(
        data={"admin_id": admin.admin_id}, expires_delta=access_token_expires
    )

    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminInDB)
def read_current_admin(
        current_admin: Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    return current_admin


@router.put("/me", response_model=AdminInDB)
def update_admin(
        admin_update: AdminUpdate,
        current_admin: Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    if admin_update.password:
        current_admin.password_hash = get_admin_password_hash(admin_update.password)

    if admin_update.email:
        existing_admin = db.query(Admin).filter(
            Admin.email == admin_update.email,
            Admin.admin_id != current_admin.admin_id
        ).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_admin.email = admin_update.email

    if admin_update.username:
        existing_admin = db.query(Admin).filter(
            Admin.username == admin_update.username,
            Admin.admin_id != current_admin.admin_id
        ).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Username already in use")
        current_admin.username = admin_update.username

    if admin_update.full_name:
        current_admin.full_name = admin_update.full_name

    if admin_update.role and current_admin.role == "super_admin":
        current_admin.role = admin_update.role

    db.commit()
    db.refresh(current_admin)
    return current_admin


@router.get("/users", response_model=List[UserInDB])
def get_all_users(
        db: Session = Depends(get_db),
        current_admin: Admin = Depends(get_current_active_admin),
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = Query(None)
):
    query = db.query(User)

    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.phone_number.ilike(f"%{search}%"))
        )

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/reports", response_model=List[UserReportWithUsers])
def get_all_reports(
        db: Session = Depends(get_db),
        current_admin: Admin = Depends(get_current_active_admin),
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
):
    query = db.query(UserReport)

    if status:
        query = query.filter(UserReport.status == status)

    reports = query.offset(skip).limit(limit).all()
    return reports


@router.patch("/reports/{report_id}")
def update_report_status(
        report_id: int,
        status: str,
        admin_notes: Optional[str] = None,
        db: Session = Depends(get_db),
        current_admin: Admin = Depends(get_current_active_admin)
):
    report = db.query(UserReport).filter(UserReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = status
    report.admin_id_assigned = current_admin.admin_id
    if admin_notes:
        report.admin_notes = admin_notes

    db.commit()
    return {"message": "Report status updated successfully"}


@router.patch("/users/{user_id}/status")
def update_user_status(
        user_id: int,
        status: str,
        db: Session = Depends(get_db),
        current_admin: Admin = Depends(get_current_active_admin)
):
    valid_statuses = ["active", "inactive", "suspended", "deleted"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.account_status = status
    db.commit()
    return {"message": f"User status updated to {status}"}