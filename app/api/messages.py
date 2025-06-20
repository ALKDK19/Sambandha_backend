from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.interaction import Chat, Message
from app.models.security import BlockedUser
from app.schemas.interaction import MessageCreate, MessageInDB, MessageWithUsers
from app.database import get_db
from app.schemas.user import UserInDB
from utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=MessageInDB)
def create_message(
        message: MessageCreate,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if chat exists and user is part of it
    chat = db.query(Chat).filter(
        Chat.chat_id == message.chat_id,
        (Chat.initiator_user_id == current_user.user_id) |
        (Chat.receiver_user_id == current_user.user_id)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Check if receiver is blocked
    blocked = db.query(BlockedUser).filter(
        ((BlockedUser.blocker_user_id == current_user.user_id) &
         (BlockedUser.blocked_user_id == message.receiver_user_id)) |
        ((BlockedUser.blocker_user_id == message.receiver_user_id) &
         (BlockedUser.blocked_user_id == current_user.user_id))
    ).first()

    if blocked:
        raise HTTPException(status_code=403, detail="Cannot message blocked user")

    # Only allow 1-2 messages if chat.state == 'request' and recipient hasn't replied
    if chat.state == 'request':
        # Count messages sent by current user in this chat
        sent_count = db.query(Message).filter(
            Message.chat_id == chat.chat_id,
            Message.sender_user_id == current_user.user_id
        ).count()
        # Check if recipient has replied
        recipient_replied = db.query(Message).filter(
            Message.chat_id == chat.chat_id,
            Message.sender_user_id == message.receiver_user_id
        ).count() > 0
        if not recipient_replied and sent_count >= 2:
            raise HTTPException(status_code=403, detail="You can only send 2 messages until the recipient replies or you are matched.")
        # If recipient replied, unlock chat
        if recipient_replied:
            chat.state = 'active'
            db.commit()
    # If chat is linked to a match, unlock chat
    if chat.match_id is not None and chat.state != 'active':
        chat.state = 'active'
        db.commit()

    # Create message
    new_message = Message(
        chat_id=message.chat_id,
        sender_user_id=current_user.user_id,
        receiver_user_id=message.receiver_user_id,
        message_content=message.message_content,
        message_type=message.message_type
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


@router.get("/chat/{chat_id}", response_model=List[MessageWithUsers])
def get_chat_messages(
        chat_id: int,
        current_user: UserInDB = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 100,
        offset: int = 0
):
    # Check if chat exists and user is part of it
    chat = db.query(Chat).filter(
        Chat.chat_id == chat_id,
        (Chat.initiator_user_id == current_user.user_id) |
        (Chat.receiver_user_id == current_user.user_id)
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.sent_at.desc()).offset(offset).limit(limit).all()
    return messages