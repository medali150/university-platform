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
    name: str  # Frontend sends 'name'
    coefficient: float = 1.0  # Frontend sends 'coefficient'
    levelId: str  # Frontend sends 'levelId'
    teacherId: Optional[str] = None  # Frontend sends 'teacherId'

class SubjectUpdate(BaseModel):
    name: Optional[str] = None  # Frontend sends 'name'
    coefficient: Optional[float] = None  # Frontend sends 'coefficient'
    levelId: Optional[str] = None  # Frontend sends 'levelId'
    teacherId: Optional[str] = None  # Frontend sends 'teacherId'


@router.get("/")
async def get_subjects(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, description="Number of items per page"),
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
    
    # Transform data for response to match frontend expectations
    response_subjects = []
    for subject in subjects:
        subject_data = {
            "id": subject.id,
            "name": subject.nom,  # Frontend expects 'name'
            "coefficient": subject.coefficient,  # Frontend expects 'coefficient'
            "levelId": subject.id_specialite,  # Frontend expects 'levelId'
            "teacherId": subject.id_enseignant,  # Frontend expects 'teacherId'
            "level": {
                "id": subject.specialite.id,
                "name": subject.specialite.nom,  # Frontend expects 'name'
                "specialty": {
                    "id": subject.specialite.id,
                    "name": subject.specialite.nom,
                    "department": {
                        "id": subject.specialite.departement.id,
                        "name": subject.specialite.departement.nom  # Frontend expects 'name'
                    } if subject.specialite.departement else None
                }
            } if subject.specialite else None,
            "teacher": {
                "id": subject.enseignant.id,
                "user": {
                    "id": subject.enseignant.utilisateur.id,
                    "nom": subject.enseignant.utilisateur.nom,
                    "prenom": subject.enseignant.utilisateur.prenom,
                    "email": subject.enseignant.utilisateur.email
                } if subject.enseignant.utilisateur else None,
                "department": {
                    "id": subject.enseignant.departement.id,
                    "name": subject.enseignant.departement.nom  # Frontend expects 'name'
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
        where={"id": subject_data.levelId},  # Convert frontend levelId to database field
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
    if subject_data.teacherId:  # Convert frontend teacherId to database field
        enseignant = await prisma.enseignant.find_unique(
            where={"id": subject_data.teacherId},  # Convert frontend teacherId to database field
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
            "nom": subject_data.name,  # Convert frontend name to database field
            "id_specialite": subject_data.levelId  # Convert frontend levelId to database field
        }
    )
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A subject with this name already exists for this specialite"
        )
    
    # Create the subject (convert frontend fields to database fields)
    create_data = {
        "nom": subject_data.name,  # Convert frontend name to database nom
        "coefficient": subject_data.coefficient,  # Add coefficient
        "id_specialite": subject_data.levelId,  # Convert frontend levelId to database id_specialite
    }
    
    # Add teacher if provided (now optional in schema)
    if subject_data.teacherId:
        create_data["id_enseignant"] = subject_data.teacherId
    
    subject = await prisma.matiere.create(
        data=create_data,
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
    
    # Transform response to match frontend expectations
    return {
        "id": subject.id,
        "name": subject.nom,  # Convert database nom to frontend name
        "levelId": subject.id_specialite,  # Convert database id_specialite to frontend levelId
        "teacherId": subject.id_enseignant,  # Convert database id_enseignant to frontend teacherId
        "level": {
            "id": subject.specialite.id,
            "name": subject.specialite.nom,  # Convert database nom to frontend name
            "specialty": {
                "id": subject.specialite.id,
                "name": subject.specialite.nom,
                "department": {
                    "id": subject.specialite.departement.id,
                    "name": subject.specialite.departement.nom
                }
            }
        },
        "teacher": {
            "id": subject.enseignant.id,
            "name": f"{subject.enseignant.utilisateur.prenom} {subject.enseignant.utilisateur.nom}" if subject.enseignant.utilisateur else "Unknown Teacher"
        } if subject.enseignant else None
    }


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
    
    # Validate and add fields to update (convert frontend field names to database field names)
    if subject_data.coefficient is not None:  # Add coefficient validation
        if subject_data.coefficient <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coefficient must be greater than 0"
            )
        update_data["coefficient"] = subject_data.coefficient
    
    if subject_data.name is not None:  # Convert frontend name to database nom
        # Check for duplicate name in the same specialite
        specialite_id = subject_data.levelId if subject_data.levelId is not None else existing_subject.id_specialite
        duplicate = await prisma.matiere.find_first(
            where={
                "nom": subject_data.name,  # Convert frontend name to database nom
                "id_specialite": specialite_id,
                "id": {"not": subject_id}
            }
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A subject with this name already exists for this specialite"
            )
        update_data["nom"] = subject_data.name  # Convert frontend name to database nom
    
    if subject_data.levelId is not None:  # Convert frontend levelId to database id_specialite
        # Verify that specialite exists and belongs to the department head's department
        specialite = await prisma.specialite.find_unique(
            where={"id": subject_data.levelId},  # Convert frontend levelId to database field
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
        update_data["id_specialite"] = subject_data.levelId  # Convert frontend levelId to database id_specialite
    
    if subject_data.teacherId is not None:  # Convert frontend teacherId to database id_enseignant
        # Verify that enseignant exists and belongs to the same department
        enseignant = await prisma.enseignant.find_unique(
            where={"id": subject_data.teacherId},  # Convert frontend teacherId to database field
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
        update_data["id_enseignant"] = subject_data.teacherId  # Convert frontend teacherId to database id_enseignant
    
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
    
    # Transform response to match frontend expectations
    return {
        "id": subject.id,
        "name": subject.nom,  # Convert database nom to frontend name
        "levelId": subject.id_specialite,  # Convert database id_specialite to frontend levelId
        "teacherId": subject.id_enseignant,  # Convert database id_enseignant to frontend teacherId
        "level": {
            "id": subject.specialite.id,
            "name": subject.specialite.nom,  # Convert database nom to frontend name
            "specialty": {
                "id": subject.specialite.id,
                "name": subject.specialite.nom,
                "department": {
                    "id": subject.specialite.departement.id,
                    "name": subject.specialite.departement.nom
                }
            }
        },
        "teacher": {
            "id": subject.enseignant.id,
            "name": f"{subject.enseignant.utilisateur.prenom} {subject.enseignant.utilisateur.nom}" if subject.enseignant.utilisateur else "Unknown Teacher"
        } if subject.enseignant else None
    }


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
@router.get("/helpers/levels")
async def get_levels_for_dept_head(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get levels/specialites from the department head's department"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    specialites = await prisma.specialite.find_many(
        where={"id_departement": department.id},
        include={"departement": True}
    )
    
    # Transform to match frontend expectations
    levels = []
    for specialite in specialites:
        levels.append({
            "id": specialite.id,
            "name": specialite.nom,  # Transform nom to name
            "specialty": {
                "id": specialite.id,
                "name": specialite.nom,
                "department": {
                    "id": specialite.departement.id,
                    "name": specialite.departement.nom
                }
            }
        })
    
    return {"levels": levels}


@router.get("/helpers/teachers")
async def get_teachers_for_dept_head(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get teachers from the department head's department"""
    
    # Get department head's department
    department = await get_dept_head_department(current_user, prisma)
    
    enseignants = await prisma.enseignant.find_many(
        where={"id_departement": department.id},
        include={"utilisateur": True, "departement": True}
    )
    
    # Transform to match frontend expectations
    teachers = []
    for enseignant in enseignants:
        # Skip teachers without user records
        if not enseignant.utilisateur:
            continue
            
        teachers.append({
            "id": enseignant.id,
            "user": {
                "id": enseignant.utilisateur.id,
                "prenom": enseignant.utilisateur.prenom,
                "nom": enseignant.utilisateur.nom,
                "email": enseignant.utilisateur.email
            },
            "department": {
                "id": enseignant.departement.id,
                "name": enseignant.departement.nom
            }
        })
    
    return {"teachers": teachers}