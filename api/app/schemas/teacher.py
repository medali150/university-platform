from pydantic import BaseModel
from typing import Optional


class DepartmentUpdateRequest(BaseModel):
    """Schema for updating teacher department"""
    new_department_id: str


class TeacherProfileResponse(BaseModel):
    """Schema for teacher profile response"""
    teacher_info: dict
    department: dict
    department_head: Optional[dict] = None
    subjects_taught: list


class DepartmentResponse(BaseModel):
    """Schema for department response"""
    id: str
    nom: str
    specialties: list
    department_head: Optional[dict] = None


class SubjectResponse(BaseModel):
    """Schema for subject response"""
    id: str
    nom: str
    level: dict
    specialty: dict
    department: dict


class TeacherImageUpload(BaseModel):
    """Response model for teacher image upload"""
    success: bool
    message: str
    image_url: Optional[str] = None
    
    
class TeacherProfileUpdate(BaseModel):
    """Model for updating teacher profile information"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    image_url: Optional[str] = None