"""
Makeup Sessions Management API
Handles creation, approval, and management of makeup sessions for cancelled or missed classes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from prisma import Prisma
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/makeup-sessions", tags=["Makeup Sessions"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MakeupSessionCreate(BaseModel):
    id_emploitemps_origin: str
    id_matiere: str
    id_enseignant: str
    id_groupe: str
    id_salle: Optional[str] = None
    date_originale: str  # ISO format date
    heure_debut_origin: str  # Format: "HH:MM"
    heure_fin_origin: str  # Format: "HH:MM"
    date_proposee: str  # ISO format date
    heure_debut_proposee: str  # Format: "HH:MM"
    heure_fin_proposee: str  # Format: "HH:MM"
    motif: str


class MakeupSessionUpdate(BaseModel):
    date_proposee: Optional[str] = None
    heure_debut_proposee: Optional[str] = None
    heure_fin_proposee: Optional[str] = None
    id_salle: Optional[str] = None
    motif: Optional[str] = None


class MakeupSessionReview(BaseModel):
    statut: str  # APPROVED, REJECTED
    notes_validation: Optional[str] = None


class MakeupSessionResponse(BaseModel):
    id: str
    subject: dict
    teacher: dict
    group: dict
    room: Optional[dict]
    originalDate: str
    originalStartTime: str
    originalEndTime: str
    proposedDate: str
    proposedStartTime: str
    proposedEndTime: str
    reason: str
    status: str
    validationNotes: Optional[str]
    createdBy: str
    validatedBy: Optional[str]
    createdAt: str
    updatedAt: str
    studentCount: int


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_makeup_session(session: any, student_count: int = 0) -> dict:
    """Format a makeup session for API response"""
    return {
        "id": session.id,
        "subject": {
            "id": session.matiere.id,
            "nom": session.matiere.nom
        },
        "teacher": {
            "id": session.enseignant.id,
            "nom": session.enseignant.nom,
            "prenom": session.enseignant.prenom,
            "fullName": f"{session.enseignant.prenom} {session.enseignant.nom}"
        },
        "group": {
            "id": session.groupe.id,
            "nom": session.groupe.nom
        },
        "room": {
            "id": session.salle.id,
            "code": session.salle.code,
            "capacite": session.salle.capacite
        } if session.salle else None,
        "originalDate": session.date_originale.isoformat(),
        "originalStartTime": session.heure_debut_origin,
        "originalEndTime": session.heure_fin_origin,
        "proposedDate": session.date_proposee.isoformat(),
        "proposedStartTime": session.heure_debut_proposee,
        "proposedEndTime": session.heure_fin_proposee,
        "reason": session.motif,
        "status": session.statut,
        "validationNotes": session.notes_validation,
        "createdBy": session.cree_par,
        "validatedBy": session.valide_par,
        "createdAt": session.createdAt.isoformat(),
        "updatedAt": session.updatedAt.isoformat(),
        "studentCount": student_count
    }


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/", response_model=List[dict])
async def get_makeup_sessions(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, APPROVED, REJECTED, SCHEDULED, COMPLETED"),
    teacher_id: Optional[str] = Query(None, description="Filter by teacher ID"),
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    from_date: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    to_date: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all makeup sessions with optional filters
    - Teachers can see their sessions
    - Department heads can see all sessions in their department
    - Admins can see all sessions
    - Students can see sessions for their group
    """
    
    where_clause = {}
    
    # Role-based filtering
    if current_user.role == "TEACHER":
        # Get teacher record
        teacher = await prisma.enseignant.find_first(
            where={"email": current_user.email}
        )
        if teacher:
            where_clause["id_enseignant"] = teacher.id
    
    elif current_user.role == "STUDENT":
        # Get student record and their group
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
            include={"groupe": True}
        )
        if student and student.groupe:
            where_clause["id_groupe"] = student.groupe.id
    
    elif current_user.role == "DEPARTMENT_HEAD":
        # Get department head's department
        chef = await prisma.chefdepartement.find_first(
            where={"id_utilisateur": current_user.id},
            include={"departement": True}
        )
        if chef:
            # Get all teachers in this department
            teachers = await prisma.enseignant.find_many(
                where={"id_departement": chef.id_departement}
            )
            teacher_ids = [t.id for t in teachers]
            where_clause["id_enseignant"] = {"in": teacher_ids}
    
    # Apply additional filters
    if status:
        where_clause["statut"] = status
    
    if teacher_id:
        where_clause["id_enseignant"] = teacher_id
    
    if group_id:
        where_clause["id_groupe"] = group_id
    
    if from_date:
        where_clause["date_proposee"] = {"gte": datetime.fromisoformat(from_date)}
    
    if to_date:
        if "date_proposee" in where_clause:
            where_clause["date_proposee"]["lte"] = datetime.fromisoformat(to_date)
        else:
            where_clause["date_proposee"] = {"lte": datetime.fromisoformat(to_date)}
    
    # Fetch sessions
    sessions = await prisma.sessionrattrapage.find_many(
        where=where_clause,
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        },
        order={"date_proposee": "desc"}
    )
    
    # Format response
    result = []
    for session in sessions:
        student_count = len(session.groupe.etudiants) if session.groupe.etudiants else 0
        result.append(format_makeup_session(session, student_count))
    
    return result


@router.get("/{session_id}", response_model=dict)
async def get_makeup_session(
    session_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific makeup session by ID"""
    
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id},
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True,
            "emploiTempsOriginal": True
        }
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    student_count = len(session.groupe.etudiants) if session.groupe.etudiants else 0
    return format_makeup_session(session, student_count)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_makeup_session(
    session_data: MakeupSessionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new makeup session
    Only teachers, department heads, and admins can create makeup sessions
    """
    
    if current_user.role not in ["TEACHER", "DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers, department heads, and admins can create makeup sessions"
        )
    
    # Verify the original schedule exists
    original_schedule = await prisma.emploitemps.find_unique(
        where={"id": session_data.id_emploitemps_origin}
    )
    if not original_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original schedule not found"
        )
    
    # Parse dates
    try:
        date_originale = datetime.fromisoformat(session_data.date_originale).date()
        date_proposee = datetime.fromisoformat(session_data.date_proposee).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        )
    
    # Create the makeup session
    new_session = await prisma.sessionrattrapage.create(
        data={
            "id_emploitemps_origin": session_data.id_emploitemps_origin,
            "id_matiere": session_data.id_matiere,
            "id_enseignant": session_data.id_enseignant,
            "id_groupe": session_data.id_groupe,
            "id_salle": session_data.id_salle,
            "date_originale": datetime.combine(date_originale, datetime.min.time()),
            "heure_debut_origin": session_data.heure_debut_origin,
            "heure_fin_origin": session_data.heure_fin_origin,
            "date_proposee": datetime.combine(date_proposee, datetime.min.time()),
            "heure_debut_proposee": session_data.heure_debut_proposee,
            "heure_fin_proposee": session_data.heure_fin_proposee,
            "motif": session_data.motif,
            "statut": "PENDING",
            "cree_par": current_user.id
        },
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        }
    )
    
    student_count = len(new_session.groupe.etudiants) if new_session.groupe.etudiants else 0
    return format_makeup_session(new_session, student_count)


@router.put("/{session_id}", response_model=dict)
async def update_makeup_session(
    session_id: str,
    session_data: MakeupSessionUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a makeup session
    Only the creator, department heads, and admins can update
    """
    
    # Get the session
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    # Check permissions
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"] and session.cree_par != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this session"
        )
    
    # Only allow updates if status is PENDING or REJECTED
    if session.statut not in ["PENDING", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update session with status {session.statut}"
        )
    
    # Prepare update data
    update_data = {}
    
    if session_data.date_proposee:
        date_proposee = datetime.fromisoformat(session_data.date_proposee).date()
        update_data["date_proposee"] = datetime.combine(date_proposee, datetime.min.time())
    
    if session_data.heure_debut_proposee:
        update_data["heure_debut_proposee"] = session_data.heure_debut_proposee
    
    if session_data.heure_fin_proposee:
        update_data["heure_fin_proposee"] = session_data.heure_fin_proposee
    
    if session_data.id_salle is not None:
        update_data["id_salle"] = session_data.id_salle
    
    if session_data.motif:
        update_data["motif"] = session_data.motif
    
    # Reset status to PENDING if it was rejected
    if session.statut == "REJECTED":
        update_data["statut"] = "PENDING"
        update_data["notes_validation"] = None
        update_data["valide_par"] = None
    
    # Update the session
    updated_session = await prisma.sessionrattrapage.update(
        where={"id": session_id},
        data=update_data,
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        }
    )
    
    student_count = len(updated_session.groupe.etudiants) if updated_session.groupe.etudiants else 0
    return format_makeup_session(updated_session, student_count)


@router.put("/{session_id}/review", response_model=dict)
async def review_makeup_session(
    session_id: str,
    review_data: MakeupSessionReview,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Approve or reject a makeup session
    Only department heads and admins can review
    """
    
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only department heads and admins can review makeup sessions"
        )
    
    # Get the session
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    # Validate status
    if review_data.statut not in ["APPROVED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be APPROVED or REJECTED"
        )
    
    # Update the session
    updated_session = await prisma.sessionrattrapage.update(
        where={"id": session_id},
        data={
            "statut": review_data.statut,
            "notes_validation": review_data.notes_validation,
            "valide_par": current_user.id
        },
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        }
    )
    
    student_count = len(updated_session.groupe.etudiants) if updated_session.groupe.etudiants else 0
    return format_makeup_session(updated_session, student_count)


@router.put("/{session_id}/schedule", response_model=dict)
async def schedule_makeup_session(
    session_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Mark an approved session as scheduled
    Only department heads and admins can schedule
    """
    
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only department heads and admins can schedule makeup sessions"
        )
    
    # Get the session
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    if session.statut != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved sessions can be scheduled"
        )
    
    # Update status to SCHEDULED
    updated_session = await prisma.sessionrattrapage.update(
        where={"id": session_id},
        data={"statut": "SCHEDULED"},
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        }
    )
    
    student_count = len(updated_session.groupe.etudiants) if updated_session.groupe.etudiants else 0
    return format_makeup_session(updated_session, student_count)


@router.put("/{session_id}/complete", response_model=dict)
async def complete_makeup_session(
    session_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Mark a scheduled session as completed
    Only teachers, department heads and admins can complete
    """
    
    if current_user.role not in ["TEACHER", "DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers, department heads and admins can complete makeup sessions"
        )
    
    # Get the session
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    if session.statut != "SCHEDULED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled sessions can be marked as completed"
        )
    
    # Update status to COMPLETED
    updated_session = await prisma.sessionrattrapage.update(
        where={"id": session_id},
        data={"statut": "COMPLETED"},
        include={
            "matiere": True,
            "enseignant": True,
            "groupe": {
                "include": {
                    "etudiants": True
                }
            },
            "salle": True
        }
    )
    
    student_count = len(updated_session.groupe.etudiants) if updated_session.groupe.etudiants else 0
    return format_makeup_session(updated_session, student_count)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_makeup_session(
    session_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a makeup session
    Only the creator, department heads, and admins can delete
    Only PENDING or REJECTED sessions can be deleted
    """
    
    # Get the session
    session = await prisma.sessionrattrapage.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Makeup session not found"
        )
    
    # Check permissions
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"] and session.cree_par != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this session"
        )
    
    # Only allow deletion if status is PENDING or REJECTED
    if session.statut not in ["PENDING", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete session with status {session.statut}"
        )
    
    # Delete the session
    await prisma.sessionrattrapage.delete(
        where={"id": session_id}
    )
    
    return None


@router.get("/stats/summary", response_model=dict)
async def get_makeup_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get statistics about makeup sessions"""
    
    where_clause = {}
    
    # Role-based filtering
    if current_user.role == "TEACHER":
        teacher = await prisma.enseignant.find_first(
            where={"email": current_user.email}
        )
        if teacher:
            where_clause["id_enseignant"] = teacher.id
    
    elif current_user.role == "STUDENT":
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
            include={"groupe": True}
        )
        if student and student.groupe:
            where_clause["id_groupe"] = student.groupe.id
    
    elif current_user.role == "DEPARTMENT_HEAD":
        chef = await prisma.chefdepartement.find_first(
            where={"id_utilisateur": current_user.id}
        )
        if chef:
            teachers = await prisma.enseignant.find_many(
                where={"id_departement": chef.id_departement}
            )
            teacher_ids = [t.id for t in teachers]
            where_clause["id_enseignant"] = {"in": teacher_ids}
    
    # Get counts by status
    total = await prisma.sessionrattrapage.count(where=where_clause)
    pending = await prisma.sessionrattrapage.count(where={**where_clause, "statut": "PENDING"})
    approved = await prisma.sessionrattrapage.count(where={**where_clause, "statut": "APPROVED"})
    rejected = await prisma.sessionrattrapage.count(where={**where_clause, "statut": "REJECTED"})
    scheduled = await prisma.sessionrattrapage.count(where={**where_clause, "statut": "SCHEDULED"})
    completed = await prisma.sessionrattrapage.count(where={**where_clause, "statut": "COMPLETED"})
    
    # Get unique student count
    sessions = await prisma.sessionrattrapage.find_many(
        where=where_clause,
        include={
            "groupe": {
                "include": {
                    "etudiants": True
                }
            }
        }
    )
    
    unique_students = set()
    for session in sessions:
        if session.groupe and session.groupe.etudiants:
            unique_students.update([s.id for s in session.groupe.etudiants])
    
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "scheduled": scheduled,
        "completed": completed,
        "uniqueStudents": len(unique_students)
    }
