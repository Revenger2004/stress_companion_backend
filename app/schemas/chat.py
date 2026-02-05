from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        description="Unique session ID for the user"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message"
    )

class ChatResponse(BaseModel):
    reply: str
