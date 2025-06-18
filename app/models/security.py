from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserReport(Base):
    __tablename__ = "user_reports"

    report_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_user_id = Column(Integer, ForeignKey("users.user_id"))
    reported_user_id = Column(Integer, ForeignKey("users.user_id"))
    report_reason_text = Column(String, nullable=True)
    report_details = Column(Text, nullable=True)
    report_category = Column(String)
    status = Column(String, default='pending_review')
    admin_id_assigned = Column(Integer, ForeignKey("admin.admin_id"), nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_user_id], back_populates="reported_users")
    reported = relationship("User", foreign_keys=[reported_user_id], back_populates="reports_against")


class BlockedUser(Base):
    __tablename__ = "blocked_users"

    block_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    blocker_user_id = Column(Integer, ForeignKey("users.user_id"))
    blocked_user_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_user_id], back_populates="blocked_users")
    blocked = relationship("User", foreign_keys=[blocked_user_id], back_populates="blocked_by")
