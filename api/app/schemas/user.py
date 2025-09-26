from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.common import BaseResponseModel


# User schemas
class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    login: str


class UserCreate(UserBase):
    password: str
    role: str  # STUDENT, TEACHER, DEPARTMENT_HEAD, ADMIN


class UserResponse(UserBase, BaseResponseModel):
    role: str


class UserLogin(BaseModel):
    login: str
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None