from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.interaction import Like
from app.schemas.interaction import LikeCreate, LikeInDB
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user
from utils.matchmaker import MatchMaker

router = APIRouter()


@router.post("/", response_model=LikeInDB)
def create_like(
        like: LikeCreate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if user is liking themselves
    if like.liked_user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot like yourself")

    # Check if like already exists
    existing_like = db.query(Like).filter(
        Like.liker_user_id == current_user.user_id,
        Like.liked_user_id == like.liked_user_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="Like already exists")

    # Create like
    new_like = Like(
        liker_user_id=current_user.user_id,
        liked_user_id=like.liked_user_id,
        like_type=like.like_type
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    # Check for mutual likes and create match if compatible
    match_maker = MatchMaker(db)
    match_maker.create_match_if_compatible(current_user.user_id, like.liked_user_id)

    return new_like


@router.get("/received", response_model=list[LikeInDB])
def get_received_likes(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10,
        offset: int = 0
):
    likes = db.query(Like).filter(
        Like.liked_user_id == current_user.user_id
    ).offset(offset).limit(limit).all()
    return likes


@router.get("/sent", response_model=list[LikeInDB])
def get_sent_likes(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10,
        offset: int = 0
):
    likes = db.query(Like).filter(
        Like.liker_user_id == current_user.user_id
    ).offset(offset).limit(limit).all()
    return likes