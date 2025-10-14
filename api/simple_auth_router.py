#!/usr/bin/env python3
"""
TEMPORARY SIMPLE LOGIN ENDPOINT
==============================
Create a working login endpoint for testing
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token

# Simple request model
class SimpleLogin(BaseModel):
    email: Optional[str] = None
    login: Optional[str] = None
    password: str

# Simple response model
class SimpleTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

# Create router
router = APIRouter(prefix="/simple", tags=["Simple Auth"])

@router.post("/login", response_model=SimpleTokenResponse)
async def simple_login(credentials: SimpleLogin, prisma: Prisma = Depends(get_prisma)):
    """Simple login endpoint for testing"""
    
    # Get identifier
    identifier = credentials.email or credentials.login
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or login required")
    
    # Find user
    user = await prisma.utilisateur.find_unique(where={"email": identifier})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Verify password
    if not verify_password(credentials.password, user.mdp_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Simple response
    return SimpleTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "prenom": user.prenom,
            "nom": user.nom,
            "role": user.role,
            "firstName": user.prenom,  # Admin panel compatibility
            "lastName": user.nom,
            "login": user.email
        }
    )