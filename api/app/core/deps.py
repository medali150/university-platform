from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.jwt import decode_token


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    prisma: Prisma = Depends(get_prisma)
):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = await prisma.utilisateur.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(allowed_roles: List[str]):
    """Dependency factory to require specific roles"""
    async def check_role(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    
    return check_role


async def get_current_admin_user(current_user = Depends(get_current_user)):
    """Get current user and ensure they are an admin"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Role-specific dependencies
require_admin = require_role(["ADMIN"])
require_department_head = require_role(["DEPARTMENT_HEAD", "ADMIN"])
require_teacher = require_role(["TEACHER", "DEPARTMENT_HEAD", "ADMIN"])
require_student = require_role(["STUDENT", "TEACHER", "DEPARTMENT_HEAD", "ADMIN"])