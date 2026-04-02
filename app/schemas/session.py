from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

# --- Session Schemas ---
class SessionCreateResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SessionUpdateRequest(BaseModel):
    status: str  # e.g. 'completed'

# --- Frame Schemas ---
# (Frames are now processed exclusively via WebSockets; no REST payload needed)

# --- Message Schemas ---
class MessageCreateRequest(BaseModel):
    session_id: uuid.UUID
    role: str  # 'user' or 'assistant'
    content: str

class MessageResponse(BaseModel):
    message_id: int
    session_id: uuid.UUID
    role: str
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
