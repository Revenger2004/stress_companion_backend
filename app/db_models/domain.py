import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Person(Base):
    __tablename__ = "persons"

    person_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    currentrole = Column(Text, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    medical_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="person", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(PG_UUID(as_uuid=True), ForeignKey("persons.person_id", ondelete="CASCADE"))
    status = Column(Text, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    person = relationship("Person", back_populates="sessions")
    frames = relationship("Frame", back_populates="session", cascade="all, delete-orphan")
    session_predictions = relationship("SessionPrediction", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Frame(Base):
    __tablename__ = "frames"

    frame_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"))
    camera_type = Column(Text, nullable=False)  # 'optical' or 'thermal'
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(Text, nullable=False)

    session = relationship("Session", back_populates="frames")
    predictions = relationship("Prediction", back_populates="frame", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    frame_id = Column(Integer, ForeignKey("frames.frame_id", ondelete="CASCADE"))
    model_type = Column(Text, nullable=False)
    stress_probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    frame = relationship("Frame", back_populates="predictions")

class SessionPrediction(Base):
    __tablename__ = "session_predictions"

    session_prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"))
    model_type = Column(Text, nullable=False)
    avg_stress_probability = Column(Float, nullable=False)
    max_stress_probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="session_predictions")

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"))
    role = Column(Text, nullable=False)  # 'user' or 'system' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
