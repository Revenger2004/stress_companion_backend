from fastapi import Request
from fastapi.responses import JSONResponse
# We still import the specific errors to use in logic if needed, 
# but for the type hint signature, we use the base Exception.
from app.core.exceptions import (
    GeminiAuthenticationError, 
    GeminiQuotaExceededError, 
    GeminiServerError,
    GeminiServiceError
)

# NOTICE: We changed the type hint 'exc: GeminiQuotaExceededError' to 'exc: Exception'
async def quota_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=429,
        content={"detail": "We are receiving too many requests. Please try again later."}
    )

async def upstream_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={"detail": "The AI service is currently down. Please check back in a moment."}
    )

async def auth_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Server misconfiguration: API Key Invalid."}
    )

async def general_error_handler(request: Request, exc: Exception):
    # It is safe to assume 'exc' has a string representation
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal AI Service Error: {str(exc)}"}
    )