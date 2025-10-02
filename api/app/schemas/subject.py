from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseResponseModel


class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    levelId: str = Field(..., description="Level ID that this subject belongs to")
    teacherId: str = Field(..., description="Teacher ID who teaches this subject")


class SubjectCreate(SubjectBase):
    """Schema for creating a new subject"""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Subject name")
    levelId: Optional[str] = Field(None, description="Level ID that this subject belongs to")
    teacherId: Optional[str] = Field(None, description="Teacher ID who teaches this subject")


class SubjectResponse(SubjectBase, BaseResponseModel):
    """Schema for subject response"""
    # Relations (optional - can be included via joins)
    level: Optional[dict] = None
    teacher: Optional[dict] = None


class SubjectListResponse(BaseModel):
    """Schema for subject list response"""
    subjects: list[SubjectResponse]
    total: int
    page: int = 1
    pageSize: int = 10
    totalPages: int


class SubjectDetailResponse(SubjectResponse):
    """Schema for detailed subject response with relations"""
    level: dict
    teacher: dict
    schedules: Optional[list[dict]] = None