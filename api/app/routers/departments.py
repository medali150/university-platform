from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.university import (
    DepartmentCreate, DepartmentResponse,
    SpecialtyCreate, SpecialtyResponse
)
from app.core.deps import require_admin, require_department_head

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(prisma: Prisma = Depends(get_prisma)):
    """Get all departments"""
    departments = await prisma.department.find_many(
        include={
            "specialties": True,
            "_count": {
                "select": {
                    "teachers": True,
                    "specialties": True
                }
            }
        }
    )
    return departments


@router.post("/", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate, 
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department (Admin only)"""
    # Check if department already exists
    existing = await prisma.department.find_unique(where={"name": dept_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists"
        )
    
    new_dept = await prisma.department.create(data={"name": dept_data.name})
    return new_dept


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: str, prisma: Prisma = Depends(get_prisma)):
    """Get department by ID"""
    department = await prisma.department.find_unique(
        where={"id": department_id},
        include={
            "specialties": True,
            "_count": {
                "select": {
                    "teachers": True,
                    "specialties": True
                }
            }
        }
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department