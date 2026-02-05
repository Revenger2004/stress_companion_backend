from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import chat
from app.routes import optical

from app.core.exceptions import (
    GeminiAuthenticationError,
    GeminiQuotaExceededError,
    GeminiServerError,
    GeminiServiceError,
)
from app.core.handlers import (
    auth_error_handler,
    quota_error_handler,
    upstream_error_handler,
    general_error_handler,
)

app = FastAPI(title=settings.PROJECT_NAME)

# --- EXCEPTION HANDLERS ---
app.add_exception_handler(GeminiAuthenticationError, auth_error_handler)
app.add_exception_handler(GeminiQuotaExceededError, quota_error_handler)
app.add_exception_handler(GeminiServerError, upstream_error_handler)
app.add_exception_handler(GeminiServiceError, general_error_handler)

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

app.include_router(optical.router, prefix="/api/v1", tags=["Optical Sensor"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }
