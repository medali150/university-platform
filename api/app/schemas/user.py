from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from app.schemas.common import BaseResponseModel


# Role enum to match Prisma schema
class Role(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    ADMIN = "ADMIN"


# User schemas
class UserBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=50, description="Last name")
    prenom: str = Field(..., min_length=1, max_length=50, description="First name")
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    role: Role = Field(..., description="User role")


class UserResponse(UserBase, BaseResponseModel):
    role: Role


class UserLogin(BaseModel):
    email: Optional[EmailStr] = Field(None, description="User email address")  
    login: Optional[str] = Field(None, description="User login (admin panel compatibility)")
    password: str = Field(..., description="User password")


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict  # Flexible user data for compatibility


class TokenPayload(BaseModel):
    sub: Optional[str] = None