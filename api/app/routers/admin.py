from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.university import DepartmentHeadCreate, DepartmentHeadResponse, AdminCreate, AdminResponse
from app.core.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Administration"])


# Department Head endpoints
@router.get("/department-heads", response_model=List[DepartmentHeadResponse])
async def get_department_heads(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all department heads (Admin only)"""
    dept_heads = await prisma.departmenthead.find_many(
        include={
            "user": {
                "select": {
                    "firstName": True,
                    "lastName": True,
                    "email": True
                }
            },
            "department": True
        }
    )
    return dept_heads


@router.post("/department-heads", response_model=DepartmentHeadResponse)
async def create_department_head(
    dept_head_data: DepartmentHeadCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department head (Admin only)"""
    # Verify user exists and has DEPARTMENT_HEAD role
    user = await prisma.user.find_unique(where={"id": dept_head_data.userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.role != "DEPARTMENT_HEAD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have DEPARTMENT_HEAD role"
        )
    
    # Verify department exists
    department = await prisma.department.find_unique(where={"id": dept_head_data.departmentId})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department already has a head
    existing_head = await prisma.departmenthead.find_unique(where={"departmentId": dept_head_data.departmentId})
    if existing_head:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department already has a head"
        )
    
    # Check if user is already a department head
    existing_user_head = await prisma.departmenthead.find_unique(where={"userId": dept_head_data.userId})
    if existing_user_head:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a department head"
        )
    
    new_dept_head = await prisma.departmenthead.create(
        data={
            "userId": dept_head_data.userId,
            "departmentId": dept_head_data.departmentId
        },
        include={
            "user": {
                "select": {
                    "firstName": True,
                    "lastName": True,
                    "email": True
                }
            },
            "department": True
        }
    )
    
    return new_dept_head


# Admin endpoints
@router.get("/admins", response_model=List[AdminResponse])
async def get_admins(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all admins (Admin only)"""
    admins = await prisma.admin.find_many(
        include={
            "user": {
                "select": {
                    "firstName": True,
                    "lastName": True,
                    "email": True,
                    "role": True
                }
            }
        }
    )
    return admins


@router.post("/admins", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new admin (Admin only)"""
    # Verify user exists and has ADMIN role
    user = await prisma.user.find_unique(where={"id": admin_data.userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have ADMIN role"
        )
    
    # Check if user is already an admin
    existing_admin = await prisma.admin.find_unique(where={"userId": admin_data.userId})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    new_admin = await prisma.admin.create(
        data={
            "userId": admin_data.userId,
            "level": admin_data.level
        },
        include={
            "user": {
                "select": {
                    "firstName": True,
                    "lastName": True,
                    "email": True,
                    "role": True
                }
            }
        }
    )
    
    return new_admin