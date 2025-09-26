from pydantic import BaseModel
from typing import Optional, List
from app.schemas.common import BaseResponseModel


# Department schemas
class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase, BaseResponseModel):
    pass


# Specialty schemas
class SpecialtyBase(BaseModel):
    name: str


class SpecialtyCreate(SpecialtyBase):
    departmentId: str


class SpecialtyResponse(SpecialtyBase, BaseResponseModel):
    departmentId: str
    department: Optional[DepartmentResponse] = None


# Department Head schemas
class DepartmentHeadBase(BaseModel):
    userId: str
    departmentId: str


class DepartmentHeadCreate(DepartmentHeadBase):
    pass


class DepartmentHeadResponse(DepartmentHeadBase, BaseResponseModel):
    pass


# Admin schemas
class AdminBase(BaseModel):
    userId: str
    level: str = "ADMIN"  # SUPER_ADMIN, ADMIN, MODERATOR


class AdminCreate(AdminBase):
    pass


class AdminResponse(AdminBase, BaseResponseModel):
    pass