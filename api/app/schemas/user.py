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
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse  # Include user data


class TokenPayload(BaseModel):
    sub: Optional[str] = None