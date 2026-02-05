class GeminiServiceError(Exception):
    """Base exception for Gemini service errors"""
    pass

class GeminiAuthenticationError(GeminiServiceError):
    """Raised when API key is invalid"""
    pass

class GeminiQuotaExceededError(GeminiServiceError):
    """Raised when we hit the rate limit"""
    pass

class GeminiServerError(GeminiServiceError):
    """Raised when Google's servers are down"""
    pass