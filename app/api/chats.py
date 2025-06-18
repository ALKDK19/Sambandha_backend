from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.interaction import Chat
from app.schemas.interaction import ChatInDB, ChatWithUsers
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ChatWithUsers])
def get_chats(
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 10,
        offset: int = 0
):
    chats = db.query(Chat).filter(
        (Chat.initiator_user_id == current_user.user_id) |
        (Chat.receiver_user_id == current_user.user_id)
    ).offset(offset).limit(limit).all()
    return chats


@router.get("/{chat_id}", response_model=ChatWithUsers)
def get_chat(
        chat_id: int,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(
        Chat.chat_id == chat_id,
        (Chat.initiator_user_id == current_user.user_id) |
        (Chat.receiver_user_id == current_user.user_id)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat