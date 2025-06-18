from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)

    # Personal Information
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String)  # 'male', 'female', 'other'
    bio = Column(Text, nullable=True)
    height_cm = Column(Integer, nullable=True)
    marital_status = Column(String, nullable=True)
    physical_status = Column(String, nullable=True)

    # Location
    current_address = Column(Text, nullable=True)
    permanent_address = Column(Text, nullable=True)
    city_text = Column(String, nullable=True)
    district_text = Column(String, nullable=True)
    country = Column(String, default='Nepal')

    # Education & Profession
    education_level_text = Column(String, nullable=True)
    college_name = Column(String, nullable=True)
    profession_text = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    annual_salary_npr = Column(Integer, nullable=True)

    # Lifestyle & Preferences
    religion_text = Column(String, nullable=True)
    caste_text = Column(String, nullable=True)
    mother_tongue = Column(String, nullable=True)
    dietary_preferences = Column(String, nullable=True)
    smoking_habits = Column(String, nullable=True)
    drinking_habits = Column(String, nullable=True)
    hobbies_interests = Column(Text, nullable=True)

    # Horoscope Details
    rashi = Column(String, nullable=True)
    nakshatra = Column(String, nullable=True)
    gotra = Column(String, nullable=True)
    manglik_status = Column(String, nullable=True)
    birth_time = Column(String, nullable=True)
    birth_place = Column(String, nullable=True)
    kundali_image_url = Column(String, nullable=True)

    # Profile Media
    primary_profile_image_url = Column(String, nullable=True)
    additional_multiple_images = Column(String, nullable=True)
    video_intro_url = Column(String, nullable=True)

    # Profile Status
    profile_completion_percentage = Column(Integer, default=0)
    profile_visibility = Column(String, default='public')
    last_active = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")
