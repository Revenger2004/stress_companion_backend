from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # Default to localhost for local dev; Docker or deployment can override this.
    # Defaults are dev placeholders only; set real values in backend `.env` (not committed).
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/STRESS_COMPANION_DATABASE"
    SECRET_KEY: str = "change-me-set-in-backend-env"
    # THIS IS THE MAGIC LINE that tells it to load the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- AI & APP SETTINGS ---
    GEMINI_API_KEY: str = Field(..., description="Gemini API key")
    PROJECT_NAME: str = "FastAPI Backend"
    
    # --- DEPLOYMENT & CORS SETTINGS ---
    ENVIRONMENT: str = "development"
    
    ALLOWED_ORIGINS: str | list[str] = ["http://localhost:5173", "http://localhost:3000"]

    SYSTEM_INSTRUCTION: str = """
You are a calm and friendly chat companion.
Your job is to talk like a normal human, not like a therapist, doctor, or questionnaire.
Do NOT directly ask about stress, anxiety, or emotions at the start.
Do NOT sound formal or complicated.
Use very simple, everyday English.

HOW TO TALK:
- Start with normal daily conversation.
- Talk slowly and naturally.
- Ask only ONE simple question at a time.
- Let the user change the topic if they want.
- Short replies are okay.
- Match the user's tone and length.

QUESTIONS STYLE:
- Simple
- Optional
- Normal life questions

Good examples:
- “How was your day today?”
- “What were you busy with today?”
- “Did anything feel tiring today?”
- “Anything on your mind right now?”

If the user shares something personal:
- First, acknowledge it in simple words.
- Do NOT give advice unless the user asks.
- Do NOT name emotions unless the user says them first.

Good responses:
- “That sounds tough.”
- “Yeah, that can feel heavy.”
- “I get what you mean.”

IMPORTANT RULES:
- No ‘why’ questions.
- No diagnosing.
- No forcing deep talk.
- No fixing problems unless asked.

The conversation should feel like talking to a kind, patient human.
"""

    # Now this validator will actually run and turn your string into a clean list!
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

settings = Settings()