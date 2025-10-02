from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.university import SpecialtyCreate, SpecialtyResponse
from app.core.deps import require_admin, require_department_head

router = APIRouter(prefix="/specialties", tags=["Specialties"])


@router.get("/", response_model=List[SpecialtyResponse])
async def get_specialties(prisma: Prisma = Depends(get_prisma)):
    """Get all specialties mapped from Specialite model."""
    specialties = await prisma.specialite.find_many(
        include={
            "departement": True
        }
    )
    # Map fields to API schema shape
    return [
        {
            "id": s.id,
            "name": s.nom,
            "departmentId": s.id_departement,
            "department": (
                {
                    "id": s.departement.id,
                    "name": s.departement.nom,
                    "createdAt": getattr(s.departement, "createdAt", None),
                    "updatedAt": getattr(s.departement, "updatedAt", None),
                }
                if getattr(s, "departement", None) else None
            ),
            "createdAt": getattr(s, "createdAt", None),
            "updatedAt": getattr(s, "updatedAt", None),
        }
        for s in specialties
    ]


@router.post("/", response_model=SpecialtyResponse)
async def create_specialty(
    spec_data: SpecialtyCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create a new specialty (Department Head or Admin only)"""
    # Verify department exists
    department = await prisma.departement.find_unique(where={"id": spec_data.departmentId})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    new_specialty = await prisma.specialite.create(
        data={
            "nom": spec_data.name,
            "id_departement": spec_data.departmentId
        },
        include={"departement": True}
    )
    
    return {
        "id": new_specialty.id,
        "name": new_specialty.nom,
        "departmentId": new_specialty.id_departement,
        "department": {"id": department.id, "name": department.nom},
        "createdAt": getattr(new_specialty, "createdAt", None),
        "updatedAt": getattr(new_specialty, "updatedAt", None),
    }


@router.get("/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(specialty_id: str, prisma: Prisma = Depends(get_prisma)):
    """Get specialty by ID"""
    specialty = await prisma.specialite.find_unique(
        where={"id": specialty_id},
        include={
            "departement": True
        }
    )
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialty not found"
        )
    return {
        "id": specialty.id,
        "name": specialty.nom,
        "departmentId": specialty.id_departement,
        "department": (
            {"id": specialty.departement.id, "name": specialty.departement.nom}
            if getattr(specialty, "departement", None) else None
        ),
        "createdAt": getattr(specialty, "createdAt", None),
        "updatedAt": getattr(specialty, "updatedAt", None),
    }