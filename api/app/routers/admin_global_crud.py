"""
Admin Global CRUD Module
========================
Complete CRUD operations for all university entities.
Admin can manage: Departments, Specialties, Teachers, Students, Classrooms, Subjects
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

from app.db.prisma_client import get_prisma
from app.core.deps import require_admin
from app.core.security import hash_password

router = APIRouter(prefix="/admin/global", tags=["Admin - Global CRUD"])


# ============================================================================
# SCHEMAS
# ============================================================================

class DepartmentCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)

class DepartmentUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)

class SpecialtyCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    id_departement: str

class SpecialtyUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    id_departement: Optional[str] = None

class LevelCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=50)
    id_specialite: str = Field(..., description="Specialty ID (required)")

class LevelUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=50)
    id_specialite: Optional[str] = Field(None, description="Specialty ID to update")

class GroupCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=50)
    id_niveau: str

class GroupUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=50)
    id_niveau: Optional[str] = None

class RoomCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    type: str = Field(..., min_length=1, max_length=20)
    capacite: int = Field(..., ge=1, le=500)
    
    @validator('type')
    def validate_type(cls, v):
        # Map French/frontend values to database enum values
        type_mapping = {
            'AMPHITHEATRE': 'LECTURE',
            'TD': 'LECTURE',
            'TP': 'LAB',
            'AUTRE': 'OTHER',
            'LECTURE': 'LECTURE',
            'LAB': 'LAB',
            'EXAM': 'EXAM',
            'OTHER': 'OTHER'
        }
        v_upper = v.upper()
        if v_upper not in type_mapping:
            raise ValueError(f'Type must be one of: AMPHITHEATRE, TD, TP, AUTRE, LECTURE, LAB, EXAM, OTHER')
        return type_mapping[v_upper]

class RoomUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    type: Optional[str] = Field(None, min_length=1, max_length=20)
    capacite: Optional[int] = Field(None, ge=1, le=500)
    
    @validator('type')
    def validate_type(cls, v):
        if v is None:
            return v
        # Map French/frontend values to database enum values
        type_mapping = {
            'AMPHITHEATRE': 'LECTURE',
            'TD': 'LECTURE',
            'TP': 'LAB',
            'AUTRE': 'OTHER',
            'LECTURE': 'LECTURE',
            'LAB': 'LAB',
            'EXAM': 'EXAM',
            'OTHER': 'OTHER'
        }
        v_upper = v.upper()
        if v_upper not in type_mapping:
            raise ValueError(f'Type must be one of: AMPHITHEATRE, TD, TP, AUTRE, LECTURE, LAB, EXAM, OTHER')
        return type_mapping[v_upper]

class TeacherCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    id_departement: str
    password: str = Field(..., min_length=6)
    image_url: Optional[str] = None

class TeacherUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    id_departement: Optional[str] = None
    image_url: Optional[str] = None

class StudentCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    id_groupe: str
    id_specialite: str
    id_niveau: Optional[str] = None
    password: str = Field(..., min_length=6)

class StudentUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    id_groupe: Optional[str] = None
    id_specialite: Optional[str] = None
    id_niveau: Optional[str] = None

class SubjectCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    coefficient: float = Field(default=1.0, ge=0.1, le=10.0)
    semester: Optional[str] = Field(None, pattern=r'^S[1-6]$')  # S1, S2, S3, S4, S5, S6
    id_departement: str  # Required
    id_niveau: str  # Required (1=Tronc Commun, 2/3=Specialized)
    id_specialite: str  # Required: Every level has a specialty (Level 1 = Tronc Commun)
    id_enseignant: Optional[str] = None  # Optional: Assigned in schedule

class SubjectUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    coefficient: Optional[float] = Field(None, ge=0.1, le=10.0)
    semester: Optional[str] = Field(None, pattern=r'^S[1-6]$')  # S1, S2, S3, S4, S5, S6
    id_departement: Optional[str] = None
    id_niveau: Optional[str] = None
    id_specialite: Optional[str] = None
    id_enseignant: Optional[str] = None


# ============================================================================
# GLOBAL SEARCH & LOOKUP ENDPOINTS
# ============================================================================

@router.get("/lookup")
async def global_lookup(
    q: str = Query(..., min_length=1, description="Search query"),
    entity: Optional[str] = Query(None, regex="^(teachers|students|all)$"),
    limit: int = Query(10, ge=1, le=50),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Global quick lookup for teachers and students"""
    results = {}
    
    # Search teachers
    if not entity or entity in ["teachers", "all"]:
        teachers = await prisma.enseignant.find_many(
            where={
                "OR": [
                    {"nom": {"contains": q, "mode": "insensitive"}},
                    {"prenom": {"contains": q, "mode": "insensitive"}},
                    {"email": {"contains": q, "mode": "insensitive"}}
                ]
            },
            take=limit,
            include={
                "departement": True,
                "utilisateur": True
            },
            order={"nom": "asc"}
        )
        results["teachers"] = teachers
    
    # Search students
    if not entity or entity in ["students", "all"]:
        students = await prisma.etudiant.find_many(
            where={
                "OR": [
                    {"nom": {"contains": q, "mode": "insensitive"}},
                    {"prenom": {"contains": q, "mode": "insensitive"}},
                    {"email": {"contains": q, "mode": "insensitive"}},
                    {"cne": {"contains": q, "mode": "insensitive"}}
                ]
            },
            take=limit,
            include={
                "groupe": True,
                "specialite": True,
                "niveau": True,
                "utilisateur": True
            },
            order={"nom": "asc"}
        )
        results["students"] = students
    
    return results


# ============================================================================
# DEPARTMENTS CRUD
# ============================================================================

@router.get("/departments")
async def get_all_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all departments with pagination and search"""
    where_clause = {}
    if search:
        where_clause = {"nom": {"contains": search, "mode": "insensitive"}}
    
    departments = await prisma.departement.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "specialites": True,
            "enseignants": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.departement.count(where=where_clause)
    
    return {
        "data": departments,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/departments/{department_id}")
async def get_department(
    department_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a single department by ID"""
    department = await prisma.departement.find_unique(
        where={"id": department_id},
        include={
            "specialites": {
                "include": {
                    "niveaux": {
                        "include": {"groupes": True}
                    }
                }
            },
            "enseignants": {
                "include": {"utilisateur": True}
            },
            "chefDepartement": {
                "include": {"utilisateur": True}
            }
        }
    )
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return department

@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department"""
    # Check if department name already exists
    existing = await prisma.departement.find_first(where={"nom": data.nom})
    if existing:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    department = await prisma.departement.create(
        data={"nom": data.nom}
    )
    
    return {
        "message": "Department created successfully",
        "data": department
    }

@router.put("/departments/{department_id}")
async def update_department(
    department_id: str,
    data: DepartmentUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a department"""
    # Check if department exists
    existing = await prisma.departement.find_unique(where={"id": department_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check name uniqueness if changing name
    if data.nom and data.nom != existing.nom:
        name_exists = await prisma.departement.find_first(where={"nom": data.nom})
        if name_exists:
            raise HTTPException(status_code=400, detail="Department name already exists")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    department = await prisma.departement.update(
        where={"id": department_id},
        data=update_data
    )
    
    return {
        "message": "Department updated successfully",
        "data": department
    }

@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    force: bool = Query(False, description="Force delete even with related data"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a department"""
    # Check if department exists
    department = await prisma.departement.find_unique(
        where={"id": department_id}
    )
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check for related data
    if not force:
        specialties_count = await prisma.specialite.count(where={"id_departement": department_id})
        teachers_count = await prisma.enseignant.count(where={"id_departement": department_id})
        if specialties_count > 0 or teachers_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete department with {specialties_count} specialties and {teachers_count} teachers. Use force=true to override."
            )
    
    await prisma.departement.delete(where={"id": department_id})
    
    return {"message": "Department deleted successfully"}


# ============================================================================
# SPECIALTIES CRUD
# ============================================================================

@router.get("/specialties")
async def get_all_specialties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department_id: Optional[str] = None,
    level_id: Optional[str] = None,
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Get all specialties with optional filtering.
    
    Filters:
    - department_id: Get specialties belonging to a specific department
    - level_id: Get specialties that have a specific level (filters by department too)
    - search: Search by specialty name
    """
    where_clause = {}
    
    # If level_id is provided, get specialties associated with that level
    if level_id:
        level = await prisma.niveau.find_unique(
            where={"id": level_id},
            include={
                "specialite": {
                    "include": {"departement": True}
                }
            }
        )
        if not level:
            raise HTTPException(status_code=404, detail="Level not found")
        
        # Get the specialty ID for this level
        specialty_ids = [level.id_specialite] if level.id_specialite else []
        
        if not specialty_ids:
            return {
                "data": [],
                "total": 0,
                "page": 1,
                "pages": 0,
                "message": "Level has no specialties assigned"
            }
        
        # Filter by specialties of this level
        where_clause["id"] = {"in": specialty_ids}
        
        # If department_id is also specified, further filter
        if department_id:
            where_clause["id_departement"] = department_id
    elif department_id:
        # Just filter by department
        where_clause["id_departement"] = department_id
    
    if search:
        where_clause["nom"] = {"contains": search, "mode": "insensitive"}
    
    specialties = await prisma.specialite.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "departement": True,
            "niveaux": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.specialite.count(where=where_clause)
    
    return {
        "data": specialties,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/specialties", status_code=status.HTTP_201_CREATED)
async def create_specialty(
    data: SpecialtyCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new specialty"""
    # Verify department exists
    department = await prisma.departement.find_unique(where={"id": data.id_departement})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    specialty = await prisma.specialite.create(
        data=data.dict(),
        include={"departement": True}
    )
    
    return {
        "message": "Specialty created successfully",
        "data": specialty
    }

@router.put("/specialties/{specialty_id}")
async def update_specialty(
    specialty_id: str,
    data: SpecialtyUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a specialty"""
    existing = await prisma.specialite.find_unique(where={"id": specialty_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Specialty not found")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    specialty = await prisma.specialite.update(
        where={"id": specialty_id},
        data=update_data,
        include={"departement": True}
    )
    
    return {
        "message": "Specialty updated successfully",
        "data": specialty
    }

@router.delete("/specialties/{specialty_id}")
async def delete_specialty(
    specialty_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a specialty"""
    specialty = await prisma.specialite.find_unique(
        where={"id": specialty_id}
    )
    
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    
    # Check for related data
    if not force:
        students_count = await prisma.etudiant.count(where={"id_specialite": specialty_id})
        subjects_count = await prisma.matiere.count(where={"id_specialite": specialty_id})
        
        if students_count > 0 or subjects_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete specialty with {students_count} students and {subjects_count} subjects"
            )
    
    await prisma.specialite.delete(where={"id": specialty_id})
    return {"message": "Specialty deleted successfully"}


# ============================================================================
# ROOMS CRUD
# ============================================================================

@router.get("/rooms")
async def get_all_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    type: Optional[str] = None,
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all classrooms/rooms"""
    where_clause = {}
    if type:
        where_clause["type"] = type
    if search:
        where_clause["code"] = {"contains": search, "mode": "insensitive"}
    
    rooms = await prisma.salle.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        order={"code": "asc"}
    )
    
    total = await prisma.salle.count(where=where_clause)
    
    return {
        "data": rooms,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/rooms", status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new classroom"""
    # Check if room code already exists
    existing = await prisma.salle.find_unique(where={"code": data.code})
    if existing:
        raise HTTPException(status_code=400, detail="Room code already exists")
    
    # Type is already converted to uppercase by validator
    room = await prisma.salle.create(data=data.dict())
    
    return {
        "message": "Room created successfully",
        "data": room
    }

@router.put("/rooms/{room_id}")
async def update_room(
    room_id: str,
    data: RoomUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a classroom"""
    existing = await prisma.salle.find_unique(where={"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check code uniqueness if changing
    if data.code and data.code != existing.code:
        code_exists = await prisma.salle.find_unique(where={"code": data.code})
        if code_exists:
            raise HTTPException(status_code=400, detail="Room code already exists")
    
    # Type is already converted to uppercase by validator
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    room = await prisma.salle.update(
        where={"id": room_id},
        data=update_data
    )
    
    return {
        "message": "Room updated successfully",
        "data": room
    }

@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a classroom"""
    room = await prisma.salle.find_unique(
        where={"id": room_id}
    )
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check for related data
    if not force:
        sessions_count = await prisma.emploitemps.count(where={"id_salle": room_id})
        
        if sessions_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete room with {sessions_count} scheduled sessions"
            )
    
    await prisma.salle.delete(where={"id": room_id})
    return {"message": "Room deleted successfully"}


# ============================================================================
# TEACHERS CRUD
# ============================================================================

@router.get("/teachers")
async def get_all_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department_id: Optional[str] = None,
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all teachers"""
    where_clause = {}
    if department_id:
        where_clause["id_departement"] = department_id
    if search:
        where_clause["OR"] = [
            {"nom": {"contains": search, "mode": "insensitive"}},
            {"prenom": {"contains": search, "mode": "insensitive"}},
            {"email": {"contains": search, "mode": "insensitive"}}
        ]
    
    teachers = await prisma.enseignant.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "departement": True,
            "utilisateur": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.enseignant.count(where=where_clause)
    
    return {
        "data": teachers,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/teachers/search")
async def search_teachers(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Quick search for teachers by name, email, or department"""
    teachers = await prisma.enseignant.find_many(
        where={
            "OR": [
                {"nom": {"contains": q, "mode": "insensitive"}},
                {"prenom": {"contains": q, "mode": "insensitive"}},
                {"email": {"contains": q, "mode": "insensitive"}},
                {
                    "departement": {
                        "nom": {"contains": q, "mode": "insensitive"}
                    }
                }
            ]
        },
        take=limit,
        include={
            "departement": True,
            "utilisateur": True
        },
        order={"nom": "asc"}
    )
    
    return {"data": teachers, "count": len(teachers)}

@router.get("/teachers/{teacher_id}")
async def get_teacher_by_id(
    teacher_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a specific teacher by ID"""
    teacher = await prisma.enseignant.find_unique(
        where={"id": teacher_id},
        include={
            "departement": True,
            "utilisateur": True,
            "matieres": True
        }
    )
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    return teacher

@router.post("/teachers", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    data: TeacherCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new teacher with user account"""
    # Verify department exists
    department = await prisma.departement.find_unique(where={"id": data.id_departement})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if email already exists
    existing_user = await prisma.utilisateur.find_unique(where={"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create teacher and user in transaction
    teacher = await prisma.enseignant.create(
        data={
            "nom": data.nom,
            "prenom": data.prenom,
            "email": data.email,
            "id_departement": data.id_departement,
            "image_url": data.image_url
        }
    )
    
    # Create user account
    user = await prisma.utilisateur.create(
        data={
            "nom": data.nom,
            "prenom": data.prenom,
            "email": data.email,
            "role": "TEACHER",
            "mdp_hash": hash_password(data.password),
            "enseignant_id": teacher.id
        }
    )
    
    # Fetch complete teacher data
    teacher = await prisma.enseignant.find_unique(
        where={"id": teacher.id},
        include={
            "departement": True,
            "utilisateur": True
        }
    )
    
    return {
        "message": "Teacher created successfully",
        "data": teacher
    }

@router.put("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: str,
    data: TeacherUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a teacher"""
    existing = await prisma.enseignant.find_unique(where={"id": teacher_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    teacher = await prisma.enseignant.update(
        where={"id": teacher_id},
        data=update_data,
        include={
            "departement": True,
            "utilisateur": True
        }
    )
    
    # Update user account if email/name changed
    if data.email or data.nom or data.prenom:
        user_update = {}
        if data.email: user_update["email"] = data.email
        if data.nom: user_update["nom"] = data.nom
        if data.prenom: user_update["prenom"] = data.prenom
        
        await prisma.utilisateur.update_many(
            where={"enseignant_id": teacher_id},
            data=user_update
        )
    
    return {
        "message": "Teacher updated successfully",
        "data": teacher
    }

@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a teacher"""
    teacher = await prisma.enseignant.find_unique(
        where={"id": teacher_id},
        include={"utilisateur": True}
    )
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Check for related data
    if not force:
        subjects_count = await prisma.matiere.count(where={"id_enseignant": teacher_id})
        sessions_count = await prisma.emploitemps.count(where={"id_enseignant": teacher_id})
        
        if subjects_count > 0 or sessions_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete teacher with {subjects_count} subjects and {sessions_count} sessions"
            )
    
    # Delete user account first
    await prisma.utilisateur.delete_many(where={"enseignant_id": teacher_id})
    
    # Delete teacher
    await prisma.enseignant.delete(where={"id": teacher_id})
    
    return {"message": "Teacher deleted successfully"}


# ============================================================================
# STUDENTS CRUD
# ============================================================================

@router.get("/students")
async def get_all_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department_id: Optional[str] = None,
    specialty_id: Optional[str] = None,
    level_id: Optional[str] = None,
    group_id: Optional[str] = None,
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Get all students with filtering.
    
    Filters:
    - department_id: Filter by department (via specialty)
    - specialty_id: Filter by specialty
    - level_id: Filter by level
    - group_id: Filter by group
    - search: Search by name or email
    """
    where_clause = {}
    
    # Filter by department (get all specialties in department, then filter students)
    if department_id and not specialty_id:
        specialties = await prisma.specialite.find_many(
            where={"id_departement": department_id}
        )
        if specialties:
            where_clause["id_specialite"] = {"in": [s.id for s in specialties]}
    
    if specialty_id:
        where_clause["id_specialite"] = specialty_id
    
    if level_id:
        where_clause["id_niveau"] = level_id
    
    if group_id:
        where_clause["id_groupe"] = group_id
    
    if search:
        where_clause["OR"] = [
            {"nom": {"contains": search, "mode": "insensitive"}},
            {"prenom": {"contains": search, "mode": "insensitive"}},
            {"email": {"contains": search, "mode": "insensitive"}}
        ]
    
    students = await prisma.etudiant.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "groupe": True,
            "specialite": True,
            "niveau": True,
            "utilisateur": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.etudiant.count(where=where_clause)
    
    return {
        "data": students,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/students/search")
async def search_students(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Quick search for students by name, email, specialty, or group"""
    students = await prisma.etudiant.find_many(
        where={
            "OR": [
                {"nom": {"contains": q, "mode": "insensitive"}},
                {"prenom": {"contains": q, "mode": "insensitive"}},
                {"email": {"contains": q, "mode": "insensitive"}},
                {"cne": {"contains": q, "mode": "insensitive"}},
                {
                    "specialite": {
                        "nom": {"contains": q, "mode": "insensitive"}
                    }
                },
                {
                    "groupe": {
                        "nom": {"contains": q, "mode": "insensitive"}
                    }
                }
            ]
        },
        take=limit,
        include={
            "groupe": True,
            "specialite": True,
            "niveau": True,
            "utilisateur": True
        },
        order={"nom": "asc"}
    )
    
    return {"data": students, "count": len(students)}

@router.get("/students/{student_id}")
async def get_student_by_id(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a specific student by ID"""
    student = await prisma.etudiant.find_unique(
        where={"id": student_id},
        include={
            "groupe": True,
            "specialite": True,
            "niveau": True,
            "utilisateur": True
        }
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.post("/students", status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new student with user account"""
    # Verify group and specialty exist
    group = await prisma.groupe.find_unique(where={"id": data.id_groupe})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    specialty = await prisma.specialite.find_unique(where={"id": data.id_specialite})
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    
    # Check if email already exists
    existing_user = await prisma.utilisateur.find_unique(where={"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create student
    student = await prisma.etudiant.create(
        data={
            "nom": data.nom,
            "prenom": data.prenom,
            "email": data.email,
            "id_groupe": data.id_groupe,
            "id_specialite": data.id_specialite,
            "id_niveau": data.id_niveau
        }
    )
    
    # Create user account
    user = await prisma.utilisateur.create(
        data={
            "nom": data.nom,
            "prenom": data.prenom,
            "email": data.email,
            "role": "STUDENT",
            "mdp_hash": hash_password(data.password),
            "etudiant_id": student.id
        }
    )
    
    # Fetch complete student data
    student = await prisma.etudiant.find_unique(
        where={"id": student.id},
        include={
            "groupe": True,
            "specialite": True,
            "utilisateur": True
        }
    )
    
    return {
        "message": "Student created successfully",
        "data": student
    }

@router.put("/students/{student_id}")
async def update_student(
    student_id: str,
    data: StudentUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a student"""
    existing = await prisma.etudiant.find_unique(where={"id": student_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    student = await prisma.etudiant.update(
        where={"id": student_id},
        data=update_data,
        include={
            "groupe": True,
            "specialite": True,
            "utilisateur": True
        }
    )
    
    # Update user account if email/name changed
    if data.email or data.nom or data.prenom:
        user_update = {}
        if data.email: user_update["email"] = data.email
        if data.nom: user_update["nom"] = data.nom
        if data.prenom: user_update["prenom"] = data.prenom
        
        await prisma.utilisateur.update_many(
            where={"etudiant_id": student_id},
            data=user_update
        )
    
    return {
        "message": "Student updated successfully",
        "data": student
    }

@router.delete("/students/{student_id}")
async def delete_student(
    student_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a student"""
    student = await prisma.etudiant.find_unique(
        where={"id": student_id}
    )
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if not force:
        absences_count = await prisma.absence.count(where={"id_etudiant": student_id})
        notes_count = await prisma.note.count(where={"id_etudiant": student_id})
        if absences_count > 0 or notes_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete student with {absences_count} absences and {notes_count} grades"
            )
    
    # Delete user account first
    await prisma.utilisateur.delete_many(where={"etudiant_id": student_id})
    
    # Delete student
    await prisma.etudiant.delete(where={"id": student_id})
    
    return {"message": "Student deleted successfully"}


# ============================================================================
# SUBJECTS CRUD
# ============================================================================

@router.get("/subjects")
async def get_all_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    specialty_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    search: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all subjects"""
    where_clause = {}
    if specialty_id:
        where_clause["id_specialite"] = specialty_id
    if teacher_id:
        where_clause["id_enseignant"] = teacher_id
    if search:
        where_clause["nom"] = {"contains": search, "mode": "insensitive"}
    
    subjects = await prisma.matiere.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "departement": True,
            "niveau": True,
            "specialite": True,
            "enseignant": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.matiere.count(where=where_clause)
    
    return {
        "data": subjects,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/subjects", status_code=status.HTTP_201_CREATED)
async def create_subject(
    data: SubjectCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Create a new subject with strict hierarchy validation.
    
    Validates:
    1. Department exists
    2. Level exists
    3. Specialty exists and belongs to the department
    4. Level is associated with the selected specialty (many-to-many)
    """
    # Verify department exists
    department = await prisma.departement.find_unique(where={"id": data.id_departement})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Verify level exists with its specialty relationship
    level = await prisma.niveau.find_unique(
        where={"id": data.id_niveau},
        include={
            "specialite": {
                "include": {"departement": True}
            }
        }
    )
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # Verify specialty exists
    specialty = await prisma.specialite.find_unique(
        where={"id": data.id_specialite},
        include={"departement": True}
    )
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    
    # VALIDATION 1: Specialty must belong to the selected department
    if specialty.id_departement != data.id_departement:
        raise HTTPException(
            status_code=400,
            detail=f"Specialty '{specialty.nom}' does not belong to department '{department.nom}'"
        )
    
    # VALIDATION 2: Level must be associated with the selected specialty
    if level.id_specialite != data.id_specialite:
        level_specialty_name = level.specialite.nom if level.specialite else 'no specialty'
        raise HTTPException(
            status_code=400,
            detail=f"Level '{level.nom}' is not associated with specialty '{specialty.nom}'. "
                   f"This level is associated with: {level_specialty_name}"
        )
    
    # VALIDATION 3: Level's specialty must belong to the selected department
    if level.specialite and level.specialite.id_departement != data.id_departement:
        raise HTTPException(
            status_code=400,
            detail=f"Level '{level.nom}' is associated with specialty '{level.specialite.nom}' "
                   f"which belongs to department '{level.specialite.departement.nom}', "
                   f"not '{department.nom}'"
        )
    
    # Verify teacher if provided
    if data.id_enseignant:
        teacher = await prisma.enseignant.find_unique(where={"id": data.id_enseignant})
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
    
    subject = await prisma.matiere.create(
        data=data.dict(),
        include={
            "departement": True,
            "niveau": True,
            "specialite": True,
            "enseignant": True
        }
    )
    
    return {
        "message": "Subject created successfully",
        "data": subject
    }

@router.put("/subjects/{subject_id}")
async def update_subject(
    subject_id: str,
    data: SubjectUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a subject"""
    existing = await prisma.matiere.find_unique(where={"id": subject_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    subject = await prisma.matiere.update(
        where={"id": subject_id},
        data=update_data,
        include={
            "departement": True,
            "niveau": True,
            "specialite": True,
            "enseignant": True
        }
    )
    
    return {
        "message": "Subject updated successfully",
        "data": subject
    }

@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a subject"""
    subject = await prisma.matiere.find_unique(
        where={"id": subject_id}
    )
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if not force:
        emploi_temps_count = await prisma.emploitemps.count(where={"id_matiere": subject_id})
        notes_count = await prisma.note.count(where={"id_matiere": subject_id})
        if emploi_temps_count > 0 or notes_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete subject with {emploi_temps_count} sessions and {notes_count} grades"
            )
    
    await prisma.matiere.delete(where={"id": subject_id})
    
    return {"message": "Subject deleted successfully"}


# ============================================================================
# LEVELS & GROUPS CRUD
# ============================================================================

@router.get("/levels")
async def get_all_levels(
    department_id: Optional[str] = None,
    specialty_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all levels with filtering by department or specialty"""
    where_clause = {}
    
    if specialty_id:
        # Direct relationship: level belongs to specialty
        where_clause["id_specialite"] = specialty_id
    elif department_id:
        # Find levels whose specialty belongs to this department
        where_clause["specialite"] = {
            "id_departement": department_id
        }
    
    levels = await prisma.niveau.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "specialite": {
                "include": {
                    "departement": True
                }
            },
            "groupes": True,
            "matieres": True
        },
        order={"nom": "asc"}
    )
    
    total = await prisma.niveau.count(where=where_clause)
    
    return {
        "data": levels,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/levels", status_code=status.HTTP_201_CREATED)
async def create_level(
    data: LevelCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new level belonging to a specialty"""
    # Verify specialty exists
    specialty = await prisma.specialite.find_unique(
        where={"id": data.id_specialite}
    )
    
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    
    # Create the level
    level = await prisma.niveau.create(
        data={
            "nom": data.nom,
            "id_specialite": data.id_specialite
        },
        include={
            "specialite": {
                "include": {"departement": True}
            }
        }
    )
    
    return {"message": "Level created successfully", "data": level}

@router.put("/levels/{level_id}")
async def update_level(
    level_id: str,
    data: LevelUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a level and its specialty"""
    existing = await prisma.niveau.find_unique(where={"id": level_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # Prepare update data
    update_data = {}
    if data.nom:
        update_data["nom"] = data.nom
    if data.id_specialite:
        # Verify specialty exists
        specialty = await prisma.specialite.find_unique(
            where={"id": data.id_specialite}
        )
        if not specialty:
            raise HTTPException(status_code=404, detail="Specialty not found")
        update_data["id_specialite"] = data.id_specialite
    
    # Update level
    level = await prisma.niveau.update(
        where={"id": level_id},
        data=update_data,
        include={
            "specialite": {
                "include": {"departement": True}
            }
        }
    )
    
    return {"message": "Level updated successfully", "data": level}

@router.delete("/levels/{level_id}")
async def delete_level(
    level_id: str,
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a level"""
    level = await prisma.niveau.find_unique(where={"id": level_id})
    
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    if not force:
        groups_count = await prisma.groupe.count(where={"id_niveau": level_id})
        students_count = await prisma.etudiant.count(where={"id_niveau": level_id})
        subjects_count = await prisma.matiere.count(where={"id_niveau": level_id})
        
        if groups_count > 0 or students_count > 0 or subjects_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete level with {groups_count} groups, {students_count} students, and {subjects_count} subjects. Use force=true to delete anyway."
            )
    
    await prisma.niveau.delete(where={"id": level_id})
    
    return {"message": "Level deleted successfully"}

@router.get("/groups")
async def get_all_groups(
    level_id: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all groups"""
    where_clause = {}
    if level_id:
        where_clause["id_niveau"] = level_id
    
    groups = await prisma.groupe.find_many(
        where=where_clause,
        include={
            "niveau": {
                "include": {
                    "specialite": True
                }
            }
        }
    )
    
    return {"data": groups}

@router.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new group"""
    group = await prisma.groupe.create(
        data=data.dict(),
        include={"niveau": True}
    )
    
    return {"message": "Group created successfully", "data": group}
