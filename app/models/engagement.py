from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, Float, Text, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    notification_type = Column(String)  # 'new_match', 'message_request', 'profile_like', etc.
    title = Column(String, nullable=True)
    message_body = Column(Text)
    related_entity_type = Column(String, nullable=True)  # 'user', 'match', 'chat'
    related_entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)

    # Relationship
    user = relationship("User", back_populates="notifications")


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    recommended_user_id = Column(Integer, ForeignKey("users.user_id"))
    recommendation_score = Column(Float)
    reason = Column(Text, nullable=True)
    status = Column(String, default='active')  # 'active', 'viewed', 'interacted'

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="recommendations")
    recommended_user = relationship("User", foreign_keys=[recommended_user_id])
