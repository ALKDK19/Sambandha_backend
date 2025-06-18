from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from utils.recommender import Recommender
from app.models.interaction import ProfileVisit
from app.models.profile import Profile
from app.models.security import BlockedUser
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileInDB, ProfileSummary
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ProfileInDB)
def create_profile(
        profile: ProfileCreate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if profile already exists
    db_profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if db_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    # Create profile
    new_profile = Profile(**profile.dict(), user_id=current_user.user_id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/me", response_model=ProfileInDB)
def read_current_profile(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


@router.put("/me", response_model=ProfileInDB)
def update_profile(
        profile: ProfileUpdate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in profile.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/{user_id}", response_model=ProfileSummary)
def read_profile(
        user_id: int,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if user is blocked
    blocked = db.query(BlockedUser).filter(
        ((BlockedUser.blocker_user_id == current_user.user_id) & (BlockedUser.blocked_user_id == user_id)) |
        ((BlockedUser.blocker_user_id == user_id) & (BlockedUser.blocked_user_id == current_user.user_id))
    ).first()

    if blocked:
        raise HTTPException(status_code=403, detail="You are blocked from viewing this profile")

    db_profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Record profile visit
    visit = ProfileVisit(
        visitor_user_id=current_user.user_id,
        visited_profile_user_id=user_id
    )
    db.add(visit)
    db.commit()

    return db_profile


# NEW RECOMMENDATION ENDPOINT
@router.get("/recommendations", response_model=List[ProfileSummary])
def get_recommended_profiles(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10
):
    """
    Get recommended profiles for the current user based on AI matching
    """
    # Initialize recommender
    recommender = Recommender(db)

    # Get recommendations
    recommendations = recommender.hybrid_recommendation(
        user_id=current_user.user_id,
        limit=limit
    )

    # Extract recommended user IDs
    recommended_user_ids = [rec.recommended_user_id for rec in recommendations]

    # Fetch profiles for recommended users
    profiles = db.query(Profile).filter(
        Profile.user_id.in_(recommended_user_ids)
    ).all()

    return profiles
@router.get("/", response_model=List[ProfileSummary])
def search_profiles(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        age_min: int = None,
        age_max: int = None,
        religion: str = None,
        caste: str = None,
        location: str = None,
        limit: int = 10,
        offset: int = 0
):
    query = db.query(Profile).filter(
        Profile.user_id != current_user.user_id,
        Profile.profile_visibility == 'public'
    )

    # Apply filters
    if age_min or age_max:
        # Need to calculate age from date_of_birth
        pass  # Implementation would require SQL functions or post-filtering

    if religion:
        query = query.filter(Profile.religion_text == religion)

    if caste:
        query = query.filter(Profile.caste_text == caste)

    if location:
        query = query.filter(
            (Profile.city_text == location) |
            (Profile.district_text == location)
        )

    # Exclude blocked users
    blocked_users = db.query(BlockedUser.blocked_user_id).filter(
        BlockedUser.blocker_user_id == current_user.user_id
    ).all()
    blocked_user_ids = [bu[0] for bu in blocked_users]
    query = query.filter(Profile.user_id.notin_(blocked_user_ids))

    profiles = query.offset(offset).limit(limit).all()
    return profiles