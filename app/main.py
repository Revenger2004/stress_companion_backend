from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import chat
from app.routes import optical
from app.routes import thermal

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

# --- APP INITIALIZATION ---
# Disable Swagger UI docs in production so the public can't inspect your API
is_prod = getattr(settings, "ENVIRONMENT", "development").lower() == "production"

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
    openapi_url=None if is_prod else "/openapi.json"
)

# --- EXCEPTION HANDLERS ---
app.add_exception_handler(GeminiAuthenticationError, auth_error_handler)
app.add_exception_handler(GeminiQuotaExceededError, quota_error_handler)
app.add_exception_handler(GeminiServerError, upstream_error_handler)
app.add_exception_handler(GeminiServiceError, general_error_handler)

# --- MIDDLEWARE ---
# Use specific origins from your settings instead of "*"
# In your .env, this would look like: ALLOWED_ORIGINS=["http://localhost:5173", "https://your-react-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if hasattr(settings, "ALLOWED_ORIGINS") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(optical.router, prefix="/api/v1", tags=["Optical Sensor"])
app.include_router(thermal.router, prefix="/api/v1", tags=["Thermal Sensor"])


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
        "docs": "/docs" if not is_prod else "disabled",
        "health": "/health"
    }