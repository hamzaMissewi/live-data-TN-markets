"""Common schemas for pagination, errors, etc."""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    redis: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class APIInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str
    openapi_url: str
    contact_email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)