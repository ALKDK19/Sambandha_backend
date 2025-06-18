from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Preference(Base):
    __tablename__ = "preferences"

    preference_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)

    # Age preferences
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    # Physical preferences
    min_height_cm = Column(Integer, nullable=True)
    max_height_cm = Column(Integer, nullable=True)

    # Marital status preferences
    preferred_marital_status_text = Column(Text, nullable=True)

    # Religious preferences
    preferred_religions_text = Column(Text, nullable=True)
    preferred_castes_text = Column(Text, nullable=True)
    preferred_manglik_status = Column(String, nullable=True)

    # Education & Profession preferences
    preferred_education_levels_text = Column(Text, nullable=True)
    preferred_professions_text = Column(Text, nullable=True)

    # Location preferences
    preferred_locations_text = Column(Text, nullable=True)

    # Financial preferences
    min_salary_expectation = Column(Integer, nullable=True)
    max_salary_expectation = Column(Integer, nullable=True)

    # Relationship
    user = relationship("User", back_populates="preferences")