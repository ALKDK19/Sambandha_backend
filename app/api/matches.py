from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.interaction import Match
from app.schemas.interaction import MatchInDB, MatchWithUsers
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MatchWithUsers])
def get_matches(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10,
        offset: int = 0
):
    matches = db.query(Match).filter(
        (Match.user1_id == current_user.user_id) |
        (Match.user2_id == current_user.user_id),
        Match.match_status == 'active'
    ).offset(offset).limit(limit).all()
    return matches


@router.delete("/{match_id}")
def unmatch(
        match_id: int,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    match = db.query(Match).filter(
        Match.match_id == match_id,
        (Match.user1_id == current_user.user_id) |
        (Match.user2_id == current_user.user_id)
    ).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.match_status = 'unmatched'
    db.commit()

    return {"message": "Successfully unmatched"}


def get_matched_profiles(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10,
        offset: int = 0
):
    """
    Get profiles of users matched with the current user.
    """
    matches = db.query(Match).filter(
        ((Match.user1_id == current_user.user_id) | (Match.user2_id == current_user.user_id)),
        Match.match_status == 'active'
    ).offset(offset).limit(limit).all()

    matched_user_ids = []
    for match in matches:
        if match.user1_id == current_user.user_id:
            matched_user_ids.append(match.user2_id)
        else:
            matched_user_ids.append(match.user1_id)

    profiles = db.query(Profile).filter(Profile.user_id.in_(matched_user_ids)).all()
    return profiles
