from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.base import BaseSchema
from app.schemas.user import UserInDB

class UserReportBase(BaseSchema):
    reporter_user_id: int
    reported_user_id: int
    report_reason_text: Optional[str] = None
    report_details: Optional[str] = None
    report_category: str

class UserReportCreate(UserReportBase):
    pass

class UserReportInDB(UserReportBase):
    report_id: int
    status: str = "pending_review"
    admin_id_assigned: Optional[int] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserReportWithUsers(UserReportInDB):
    reporter: UserInDB
    reported: UserInDB

class BlockedUserBase(BaseSchema):
    blocker_user_id: int
    blocked_user_id: int

class BlockedUserCreate(BlockedUserBase):
    pass

class BlockedUserInDB(BlockedUserBase):
    block_id: int
    created_at: datetime

class BlockedUserWithUsers(BlockedUserInDB):
    blocker: UserInDB
    blocked: UserInDB
