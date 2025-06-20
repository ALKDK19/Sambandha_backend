from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.base import BaseSchema
from app.schemas.user import UserInDB
from app.schemas.profile import ProfileSummary

class LikeBase(BaseSchema):
    liker_user_id: int
    liked_user_id: int
    like_type: str = "like"

class LikeCreate(LikeBase):
    pass

class LikeInDB(LikeBase):
    like_id: int
    created_at: datetime

class LikeWithUser(LikeInDB):
    liker: UserInDB
    liked: UserInDB

class MatchBase(BaseSchema):
    user1_id: int
    user2_id: int
    compatibility_score: Optional[float] = None
    match_status: str = "active"

class MatchCreate(MatchBase):
    pass

class MatchInDB(MatchBase):
    match_id: int
    created_at: datetime
    updated_at: datetime

class MatchWithUsers(MatchInDB):
    user1: UserInDB
    user2: UserInDB

class ProfileVisitBase(BaseSchema):
    visitor_user_id: int
    visited_profile_user_id: int

class ProfileVisitCreate(ProfileVisitBase):
    pass

class ProfileVisitInDB(ProfileVisitBase):
    visit_id: int
    visit_timestamp: datetime

class ChatBase(BaseSchema):
    match_id: Optional[int] = None
    initiator_user_id: int
    receiver_user_id: int
    state: str = "request"  # 'request', 'active'

class ChatCreate(ChatBase):
    pass

class ChatInDB(ChatBase):
    chat_id: int
    created_at: datetime

class ChatWithUsers(ChatInDB):
    initiator: UserInDB
    receiver: UserInDB
    match: Optional[MatchInDB] = None

class MessageBase(BaseSchema):
    chat_id: int
    sender_user_id: int
    receiver_user_id: int
    message_content: str
    message_type: str = "text"

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    message_id: int
    sent_at: datetime
    read_at: Optional[datetime] = None

class MessageWithUsers(MessageInDB):
    sender: UserInDB
    receiver: UserInDB
    chat: ChatInDB
