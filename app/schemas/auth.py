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
