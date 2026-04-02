from pydantic import BaseModel, Field
from typing import Optional
import uuid

# --- Auth Schemas ---
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    currentrole: Optional[str] = None
    # Lifestyle
    physical_activity: Optional[str] = None    # e.g. "low", "moderate", "high"
    daily_screen_time: Optional[float] = None  # hours per day
    stress_sources: Optional[str] = None
    # Psychology traits (Big Five renamed)
    openness: Optional[float] = None       # Openness
    disciplined: Optional[float] = None   # Conscientiousness
    outgoing: Optional[float] = None      # Extraversion
    cooperative: Optional[float] = None   # Agreeableness
    anxious: Optional[float] = None       # Neuroticism

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PersonResponse(BaseModel):
    person_id: uuid.UUID
    name: Optional[str] = None
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    currentrole: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    profile_image_path: Optional[str] = None
    # Lifestyle
    physical_activity: Optional[str] = None
    daily_screen_time: Optional[float] = None
    stress_sources: Optional[str] = None
    # Psychology traits
    openness: Optional[float] = None
    disciplined: Optional[float] = None
    outgoing: Optional[float] = None
    cooperative: Optional[float] = None
    anxious: Optional[float] = None

    class Config:
        from_attributes = True

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    currentrole: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    # Lifestyle
    physical_activity: Optional[str] = None
    daily_screen_time: Optional[float] = None
    stress_sources: Optional[str] = None
    # Psychology traits
    openness: Optional[float] = None
    disciplined: Optional[float] = None
    outgoing: Optional[float] = None
    cooperative: Optional[float] = None
    anxious: Optional[float] = None
