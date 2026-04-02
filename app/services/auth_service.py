from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db_models.domain import Person
from app.schemas.auth import RegisterRequest, LoginRequest, ProfileUpdateRequest
from app.core.security import hash_password, verify_password, create_access_token

def register_new_user(db: Session, request: RegisterRequest) -> str:
    # Check if email already exists
    existing = db.query(Person).filter(Person.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    person = Person(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        age=request.age,
        gender=request.gender,
        country=request.country,
        education=request.education,
        currentrole=request.currentrole
    )
    db.add(person)
    db.commit()
    
    return create_access_token(data={"sub": person.email})

def authenticate_user(db: Session, request: LoginRequest) -> str:
    person = db.query(Person).filter(Person.email == request.email).first()
    if not person or not verify_password(request.password, person.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return create_access_token(data={"sub": person.email})

def update_user_profile(db: Session, current_user: Person, request: ProfileUpdateRequest) -> Person:
    update_data = request.model_dump(exclude_unset=True)
    
    # Prevent duplicate email crashes
    if "email" in update_data and update_data["email"] != current_user.email:
        existing = db.query(Person).filter(Person.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email is already in use.")

    # Securely handle password updates
    if "password" in update_data:
        raw_password = update_data.pop("password")
        update_data["password_hash"] = hash_password(raw_password)

    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.commit()
    db.refresh(current_user)
    return current_user