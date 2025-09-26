from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.university import SpecialtyCreate, SpecialtyResponse
from app.core.deps import require_admin, require_department_head

router = APIRouter(prefix="/specialties", tags=["Specialties"])


@router.get("/", response_model=List[SpecialtyResponse])
async def get_specialties(prisma: Prisma = Depends(get_prisma)):
    """Get all specialties"""
    specialties = await prisma.specialty.find_many(
        include={
            "department": True,
            "_count": {
                "select": {
                    "levels": True,
                    "students": True
                }
            }
        }
    )
    return specialties


@router.post("/", response_model=SpecialtyResponse)
async def create_specialty(
    spec_data: SpecialtyCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create a new specialty (Department Head or Admin only)"""
    # Verify department exists
    department = await prisma.department.find_unique(where={"id": spec_data.departmentId})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    new_specialty = await prisma.specialty.create(
        data={
            "name": spec_data.name,
            "departmentId": spec_data.departmentId
        },
        include={"department": True}
    )
    
    return new_specialty


@router.get("/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(specialty_id: str, prisma: Prisma = Depends(get_prisma)):
    """Get specialty by ID"""
    specialty = await prisma.specialty.find_unique(
        where={"id": specialty_id},
        include={
            "department": True,
            "_count": {
                "select": {
                    "levels": True,
                    "students": True
                }
            }
        }
    )
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialty not found"
        )
    return specialty