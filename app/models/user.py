from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    password_hash = Column(String)
    social_media_id = Column(String, nullable=True)
    auth_provider = Column(String)
    is_phone_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    account_status = Column(String)
    preferred_language = Column(String, default='en_US')
    theme_preference = Column(String, default='light')

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    preferences = relationship("Preference", back_populates="user", uselist=False)
    sent_likes = relationship("Like", foreign_keys="Like.liker_user_id", back_populates="liker")
    received_likes = relationship("Like", foreign_keys="Like.liked_user_id", back_populates="liked")
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2")
    sent_messages = relationship("Message", foreign_keys="Message.sender_user_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_user_id", back_populates="receiver")
    notifications = relationship("Notification", back_populates="user")
    recommendations = relationship("Recommendation", foreign_keys="Recommendation.user_id", back_populates="user")
    reported_users = relationship("UserReport", foreign_keys="UserReport.reporter_user_id", back_populates="reporter")
    reports_against = relationship("UserReport", foreign_keys="UserReport.reported_user_id", back_populates="reported")
    blocked_users = relationship("BlockedUser", foreign_keys="BlockedUser.blocker_user_id", back_populates="blocker")
    blocked_by = relationship("BlockedUser", foreign_keys="BlockedUser.blocked_user_id", back_populates="blocked")
