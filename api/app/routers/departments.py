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
    """Get all departments (maps from Departement model)."""
    departments = await prisma.departement.find_many()
    return [
        {
            "id": d.id,
            "name": d.nom,
            "createdAt": getattr(d, "createdAt", None),
            "updatedAt": getattr(d, "updatedAt", None),
        }
        for d in departments
    ]


@router.post("/", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate, 
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department (Admin only)"""
    # Check if department already exists
    existing = await prisma.departement.find_first(where={"nom": dept_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists"
        )
    
    new_dept = await prisma.departement.create(data={"nom": dept_data.name})
    return {
        "id": new_dept.id,
        "name": new_dept.nom,
        "createdAt": getattr(new_dept, "createdAt", None),
        "updatedAt": getattr(new_dept, "updatedAt", None),
    }


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: str, prisma: Prisma = Depends(get_prisma)):
    """Get department by ID"""
    department = await prisma.departement.find_unique(
        where={"id": department_id}
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return {
        "id": department.id,
        "name": department.nom,
        "createdAt": getattr(department, "createdAt", None),
        "updatedAt": getattr(department, "updatedAt", None),
    }