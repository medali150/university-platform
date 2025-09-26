from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import List
from prisma import Prisma
from datetime import timedelta

from app.db.prisma_client import get_prisma
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, prisma: Prisma = Depends(get_prisma)):
    """Register a new user"""
    # Check if user already exists
    existing = await prisma.user.find_first(
        where={
            "OR": [
                {"email": user_data.email},
                {"login": user_data.login}
            ]
        }
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or login already exists"
        )
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    new_user = await prisma.user.create(
        data={
            "firstName": user_data.firstName,
            "lastName": user_data.lastName,
            "email": user_data.email,
            "login": user_data.login,
            "passwordHash": hashed_password,
            "role": user_data.role
        }
    )
    
    return new_user


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, prisma: Prisma = Depends(get_prisma)):
    """Login user and return JWT tokens"""
    user = await prisma.user.find_unique(where={"login": user_credentials.login})
    
    if not user or not verify_password(user_credentials.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(prisma: Prisma = Depends(get_prisma)):
    """Get all users"""
    users = await prisma.user.find_many(
        select={
            "id": True,
            "firstName": True,
            "lastName": True,
            "email": True,
            "login": True,
            "role": True,
            "createdAt": True,
            "updatedAt": True
        }
    )
    return users