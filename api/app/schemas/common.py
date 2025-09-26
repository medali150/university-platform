from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IDModel(BaseModel):
    """Base model with ID field"""
    id: str


class TimestampModel(BaseModel):
    """Base model with timestamp fields"""
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class BaseResponseModel(IDModel, TimestampModel):
    """Base response model with ID and timestamps"""
    pass