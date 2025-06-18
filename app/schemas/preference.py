from typing import Optional, List
from pydantic import BaseModel

from app.schemas.base import BaseSchema

class PreferenceBase(BaseSchema):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    min_height_cm: Optional[int] = None
    max_height_cm: Optional[int] = None
    preferred_marital_status_text: Optional[str] = None
    preferred_religions_text: Optional[str] = None
    preferred_castes_text: Optional[str] = None
    preferred_education_levels_text: Optional[str] = None
    preferred_professions_text: Optional[str] = None
    preferred_locations_text: Optional[str] = None
    preferred_manglik_status: Optional[str] = None
    min_salary_expectation: Optional[int] = None
    max_salary_expectation: Optional[int] = None

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class PreferenceInDB(PreferenceBase):
    preference_id: int
    user_id: int

class PreferenceResponse(PreferenceInDB):
    preferred_marital_status: Optional[List[str]] = None
    preferred_religions: Optional[List[str]] = None
    preferred_castes: Optional[List[str]] = None
    preferred_education_levels: Optional[List[str]] = None
    preferred_professions: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None