from pydantic import BaseModel
from typing import Optional, Dict, Any

class OpticalAnalysisResponse(BaseModel):
    """
    Standardized lightweight response for Optical (RGB) analysis.
    
    Optimized for bandwidth:
    - Returns only the raw probability (0.0 - 1.0).
    - Frontend calculates the Score (0-100).
    """
    status: str
    
    # The raw output from the regression model (0.0 to 1.0)
    stress_probability: float  
    
    # Flexible container for debugging info (e.g., model version, processing time)
    metadata: Optional[Dict[str, Any]] = None