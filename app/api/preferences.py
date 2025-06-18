from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.preference import Preference
from app.schemas.preference import PreferenceCreate, PreferenceUpdate, PreferenceInDB
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=PreferenceInDB)
def create_preference(
        preference: PreferenceCreate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if preference already exists
    db_pref = db.query(Preference).filter(Preference.user_id == current_user.user_id).first()
    if db_pref:
        raise HTTPException(status_code=400, detail="Preference already exists")

    # Create preference
    new_pref = Preference(**preference.dict(), user_id=current_user.user_id)
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)

    return new_pref


@router.get("/me", response_model=PreferenceInDB)
def read_current_preference(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_pref = db.query(Preference).filter(Preference.user_id == current_user.user_id).first()
    if not db_pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    return db_pref


@router.put("/me", response_model=PreferenceInDB)
def update_preference(
        preference: PreferenceUpdate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_pref = db.query(Preference).filter(Preference.user_id == current_user.user_id).first()
    if not db_pref:
        raise HTTPException(status_code=404, detail="Preference not found")

    for key, value in preference.dict(exclude_unset=True).items():
        setattr(db_pref, key, value)

    db.commit()
    db.refresh(db_pref)
    return db_pref