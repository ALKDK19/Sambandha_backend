from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime

from app.schemas.base import BaseSchema


class ProfileBase(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    height_cm: Optional[int] = None
    marital_status: Optional[str] = None
    physical_status: Optional[str] = None

    # Location
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    city_text: Optional[str] = None
    district_text: Optional[str] = None
    country: Optional[str] = "Nepal"

    # Education & Profession
    education_level_text: Optional[str] = None
    college_name: Optional[str] = None
    profession_text: Optional[str] = None
    company_name: Optional[str] = None
    annual_salary_npr: Optional[int] = None

    # Lifestyle & Preferences
    religion_text: Optional[str] = None
    caste_text: Optional[str] = None
    mother_tongue: Optional[str] = None
    dietary_preferences: Optional[str] = None
    smoking_habits: Optional[str] = None
    drinking_habits: Optional[str] = None
    hobbies_interests: Optional[str] = None

    # Horoscope Details
    rashi: Optional[str] = None
    nakshatra: Optional[str] = None
    gotra: Optional[str] = None
    manglik_status: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    kundali_image_url: Optional[str] = None

    # Profile Media
    primary_profile_image_url: Optional[str] = None
    additional_multiple_images: Optional[str] = None  # Comma-separated URLs
    video_intro_url: Optional[str] = None

    # Profile Status
    profile_visibility: Optional[str] = "public"


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileInDB(ProfileBase):
    profile_id: int
    user_id: int
    profile_completion_percentage: int = 0
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ProfileSummary(BaseSchema):
    user_id: int
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    city_text: Optional[str] = None
    profession_text: Optional[str] = None
    primary_profile_image_url: Optional[str] = None
    profile_completion_percentage: int = 0
