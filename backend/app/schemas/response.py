"""
Standard API Response Schemas
"""
from typing import Optional, Any, List
from pydantic import BaseModel


class ResponseBase(BaseModel):
    """Base response model."""
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorDetail(BaseModel):
    """Error detail model."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    errors: Optional[List[ErrorDetail]] = None
    
    
class PaginatedResponse(BaseModel):
    """Paginated response model."""
    success: bool = True
    message: str = "Success"
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    
class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    database: str
    redis: str
    ml_models: str
