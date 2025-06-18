from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP

from app.models.base import Base


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    email = Column(String, unique=True)
    full_name = Column(String)
    role = Column(String, default='admin')  # 'super_admin', 'moderator'
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
