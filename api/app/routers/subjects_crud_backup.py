from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin, require_department_head
from pydantic import BaseModel

router = APIRouter(prefix="/department-head/subjects", tags=["Department Head - Subjects"])

# Helper function to get department head's department
async def get_dept_head_department(current_user, prisma: Prisma):
    """Get the department managed by the current department head"""
    dept_head = await prisma.chefdepartement.find_unique(
        where={"id_utilisateur": current_user.id},
        include={"departement": True}
    )
    
    if not dept_head:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a department head"
        )
    
    return dept_head.departement

# Pydantic models for API
class SubjectCreate(BaseModel):
    nom: str
    id_specialite: str
    id_enseignant: Optional[str] = None

class SubjectUpdate(BaseModel):
    nom: Optional[str] = None
    id_specialite: Optional[str] = None
    id_enseignant: Optional[str] = None


@router.get("/")
async def get_subjects(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in subject name"),
    levelId: Optional[str] = Query(None, description="Filter by speciality ID"),
    teacherId: Optional[str] = Query(None, description="Filter by teacher ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all subjects with pagination and filtering (Department Head only)"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    # Build where clause for filtering - only subjects from the department head's department
    where_clause = {
        "specialite": {
            "id_departement": department.id
        }
    }
    if search:
        where_clause["nom"] = {"contains": search}
    if levelId:
        where_clause["id_specialite"] = levelId
    if teacherId:
        where_clause["id_enseignant"] = teacherId
    
    # Get total count
    total = await prisma.matiere.count(where=where_clause)
    
    # Calculate pagination
    skip = (page - 1) * pageSize
    total_pages = (total + pageSize - 1) // pageSize
    
    # Get subjects with relations
    subjects = await prisma.matiere.find_many(
        where=where_clause,
        include={
            "specialite": {
                "include": {
                    "departement": True
                }
            },
            "enseignant": {
                "include": {
                    "utilisateur": True,
                    "departement": True
                }
            }
        },
        skip=skip,
        take=pageSize,
        order={"nom": "asc"}
    )
    
    # Transform data for response
    response_subjects = []
    for subject in subjects:
        subject_data = {
            "id": subject.id,
            "nom": subject.nom,
            "id_specialite": subject.id_specialite,
            "id_enseignant": subject.id_enseignant,
            "specialite": {
                "id": subject.specialite.id,
                "nom": subject.specialite.nom,
                "departement": {
                    "id": subject.specialite.departement.id,
                    "nom": subject.specialite.departement.nom
                } if subject.specialite else None
            } if subject.specialite else None,
            "enseignant": {
                "id": subject.enseignant.id,
                "nom": subject.enseignant.nom,
                "prenom": subject.enseignant.prenom,
                "email": subject.enseignant.email,
                "utilisateur": {
                    "id": subject.enseignant.utilisateur.id,
                    "nom": subject.enseignant.utilisateur.nom,
                    "prenom": subject.enseignant.utilisateur.prenom
                } if subject.enseignant.utilisateur else None,
                "departement": {
                    "id": subject.enseignant.departement.id,
                    "nom": subject.enseignant.departement.nom
                } if subject.enseignant.departement else None
            } if subject.enseignant else None
        }
        response_subjects.append(subject_data)
    
    return {
        "subjects": response_subjects,
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "totalPages": total_pages
    }


@router.post("/")
async def create_subject(
    subject_data: SubjectCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create a new subject (Department Head only)"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify that specialite exists and belongs to the department head's department
    specialite = await prisma.specialite.find_unique(
        where={"id": subject_data.id_specialite},
        include={"departement": True}
    )
    if not specialite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialite not found"
        )
    
    if specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create subjects for specialites in your department"
        )
    
    # Verify that enseignant exists and belongs to the same department (if provided)
    if subject_data.id_enseignant:
        enseignant = await prisma.enseignant.find_unique(
            where={"id": subject_data.id_enseignant},
            include={"departement": True}
        )
        if not enseignant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enseignant not found"
            )
        
        if enseignant.id_departement != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign teachers from your department"
            )
    
    # Check if subject with same name already exists for this level
    existing_subject = await prisma.matiere.find_first(
        where={
            "nom": subject_data.nom,
            "id_specialite": subject_data.id_specialite
        }
    )
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A subject with this name already exists for this specialite"
        )
    
    # Create the subject
    subject = await prisma.matiere.create(
        data={
            "nom": subject_data.nom,
            "id_specialite": subject_data.id_specialite,
            "id_enseignant": subject_data.id_enseignant
        },
        include={
            "specialite": {
                "include": {
                    "departement": True
                }
            },
            "enseignant": {
                "include": {"utilisateur": True, "departement": True}
            }
        }
    )
    
    return subject


@router.put("/{subject_id}")
async def update_subject(
    subject_id: str,
    subject_data: SubjectUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Update a subject (Department Head only)"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    # Check if subject exists and belongs to the department head's department
    existing_subject = await prisma.matiere.find_unique(
        where={"id": subject_id},
        include={"specialite": {"include": {"departement": True}}}
    )
    if not existing_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    if existing_subject.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update subjects from your department"
        )
    
    # Prepare update data
    update_data = {}
    
    # Validate and add fields to update
    if subject_data.nom is not None:
        # Check for duplicate name in the same specialite
        specialite_id = subject_data.id_specialite if subject_data.id_specialite is not None else existing_subject.id_specialite
        duplicate = await prisma.matiere.find_first(
            where={
                "nom": subject_data.nom,
                "id_specialite": specialite_id,
                "id": {"not": subject_id}
            }
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A subject with this name already exists for this specialite"
            )
        update_data["nom"] = subject_data.nom
    
    if subject_data.id_specialite is not None:
        # Verify that specialite exists and belongs to the department head's department
        specialite = await prisma.specialite.find_unique(
            where={"id": subject_data.id_specialite},
            include={"departement": True}
        )
        if not specialite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialite not found"
            )
        
        if specialite.id_departement != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign specialites from your department"
            )
        update_data["id_specialite"] = subject_data.id_specialite
    
    if subject_data.id_enseignant is not None:
        # Verify that enseignant exists and belongs to the same department
        enseignant = await prisma.enseignant.find_unique(
            where={"id": subject_data.id_enseignant},
            include={"departement": True}
        )
        if not enseignant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enseignant not found"
            )
        
        if enseignant.id_departement != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign teachers from your department"
            )
        update_data["id_enseignant"] = subject_data.id_enseignant
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    # Update the subject
    subject = await prisma.matiere.update(
        where={"id": subject_id},
        data=update_data,
        include={
            "specialite": {
                "include": {
                    "departement": True
                }
            },
            "enseignant": {
                "include": {"utilisateur": True, "departement": True}
            }
        }
    )
    
    return subject


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Delete a subject (Department Head only)"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    # Check if subject exists and belongs to the department head's department
    subject = await prisma.matiere.find_unique(
        where={"id": subject_id},
        include={"specialite": {"include": {"departement": True}}}
    )
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    if subject.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete subjects from your department"
        )
    
    # Check if subject has associated schedules
    schedule_count = await prisma.emploitemps.count(where={"id_matiere": subject_id})
    if schedule_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete subject. It has {schedule_count} associated schedules. Please remove or reassign these schedules first."
        )
    
    # Delete the subject
    await prisma.matiere.delete(where={"id": subject_id})
    
    return None


@router.get("/{subject_id}/schedules")
async def get_subject_schedules(
    subject_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all schedules for a specific subject (Department Head only)"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    # Check if subject exists and belongs to the department head's department
    subject = await prisma.matiere.find_unique(
        where={"id": subject_id},
        include={"specialite": {"include": {"departement": True}}}
    )
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    if subject.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view schedules for subjects from your department"
        )
    
    # Get total count
    total = await prisma.emploitemps.count(where={"id_matiere": subject_id})
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    # Get schedules
    schedules = await prisma.emploitemps.find_many(
        where={"id_matiere": subject_id},
        include={
            "salle": True,
            "groupe": True,
            "enseignant": {"include": {"utilisateur": True}},
            "absences": {"include": {"etudiant": {"include": {"utilisateur": True}}}}
        },
        skip=skip,
        take=page_size,
        order={"date": "desc"}
    )
    
    return {
        "schedules": schedules,
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages,
        "subject": subject
    }


# Helper endpoints for frontend
@router.get("/specialites")
async def get_specialites_for_dept_head(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get specialites from the department head's department"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    specialites = await prisma.specialite.find_many(
        where={"id_departement": department.id},
        include={"niveaux": True}
    )
    return specialites


@router.get("/enseignants")
async def get_enseignants_for_dept_head(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get teachers from the department head's department"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    enseignants = await prisma.enseignant.find_many(
        where={"id_departement": department.id},
        include={"utilisateur": True}
    )
    return enseignants