from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from utils.security import get_current_admin

def get_current_active_admin(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.admin_id == current_admin["admin_id"]).first()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive admin account"
        )
    return admin

def get_current_super_admin(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.admin_id == current_admin["admin_id"]).first()
    if not admin or not admin.is_active or admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return admin