import os, shutil, uuid as uuid_lib
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.db_models.domain import Person
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    PersonResponse, ProfileUpdateRequest
)
from app.core.security import get_current_user
from app.services import auth_service  # Import your new service

router = APIRouter(prefix="/auth", tags=["Auth"])

UPLOAD_DIR = "uploads/profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DBSession = Depends(get_db)):
    token = auth_service.register_new_user(db, request)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DBSession = Depends(get_db)):
    token = auth_service.authenticate_user(db, request)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=PersonResponse)
def get_profile(current_user: Person = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=PersonResponse)
def update_profile(
    request: ProfileUpdateRequest,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    updated_user = auth_service.update_user_profile(db, current_user, request)
    return updated_user

@router.post("/me/profile-image", response_model=PersonResponse)
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Upload a profile picture. Saves the file and stores the path in the DB."""
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid_lib.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_image_path = file_path
    db.commit()
    db.refresh(current_user)
    return current_user