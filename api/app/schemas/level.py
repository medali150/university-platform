from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseResponseModel


class LevelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Level name (e.g., 'License 1', 'Master 2')")
    specialtyId: str = Field(..., description="Specialty ID that this level belongs to")


class LevelCreate(LevelBase):
    """Schema for creating a new level"""
    pass


class LevelUpdate(BaseModel):
    """Schema for updating a level"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Level name")
    specialtyId: Optional[str] = Field(None, description="Specialty ID that this level belongs to")


class LevelResponse(LevelBase, BaseResponseModel):
    """Schema for level response"""
    # Relations (optional - can be included via joins)
    specialty: Optional[dict] = None


class LevelListResponse(BaseModel):
    """Schema for level list response"""
    levels: list[LevelResponse]
    total: int
    page: int = 1
    pageSize: int = 10
    totalPages: int


class LevelDetailResponse(LevelResponse):
    """Schema for detailed level response with relations"""
    specialty: dict
    groups: Optional[list[dict]] = None
    subjects: Optional[list[dict]] = None