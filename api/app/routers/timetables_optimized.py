"""
Optimized Timetable API Routes

Clean, focused endpoints following REST principles:
- POST /timetables/semester - Create entire semester schedule
- GET /timetables/student/weekly - Student view (read-only)
- GET /timetables/teacher/weekly - Teacher view (read-only, auto-generated)
- GET /timetables/department/semester - Department overview
- PATCH /timetables/{id} - Update single session
- DELETE /timetables/{id} - Cancel session

Author: Senior Developer
Date: October 2025
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel, Field
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_role
from app.services.timetable_service import (
    TimetableService,
    ScheduleTemplate,
    DayOfWeek,
    RecurrenceType
)

router = APIRouter(prefix="/timetables", tags=["Timetables"])


# ===========================
# REQUEST/RESPONSE MODELS
# ===========================

class SemesterScheduleCreate(BaseModel):
    """Request to create a semester schedule"""
    matiere_id: str = Field(..., description="ID de la matière")
    groupe_id: str = Field(..., description="ID du groupe d'étudiants")
    enseignant_id: str = Field(..., description="ID de l'enseignant")
    salle_id: str = Field(..., description="ID de la salle")
    day_of_week: DayOfWeek = Field(..., description="Jour de la semaine")
    start_time: str = Field(..., description="Heure de début (HH:MM)", example="08:30")
    end_time: str = Field(..., description="Heure de fin (HH:MM)", example="10:00")
    recurrence_type: RecurrenceType = Field(default=RecurrenceType.WEEKLY, description="Type de récurrence")
    semester_start: date = Field(..., description="Date de début du semestre")
    semester_end: date = Field(..., description="Date de fin du semestre")
    
    class Config:
        schema_extra = {
            "example": {
                "matiere_id": "cm123abc",
                "groupe_id": "cm456def",
                "enseignant_id": "cm789ghi",
                "salle_id": "cm012jkl",
                "day_of_week": "MONDAY",
                "start_time": "08:30",
                "end_time": "10:00",
                "recurrence_type": "WEEKLY",
                "semester_start": "2025-09-01",
                "semester_end": "2025-12-31"
            }
        }


class ScheduleUpdate(BaseModel):
    """Update a single schedule session"""
    date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    salle_id: Optional[str] = None
    status: Optional[str] = None


class TimetableResponse(BaseModel):
    """Timetable response"""
    week_start: str
    week_end: str
    timetable: dict
    total_hours: str
    note: Optional[str] = None


# ===========================
# HELPER FUNCTIONS
# ===========================

async def get_current_dept_head(
    current_user = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    """Get current department head"""
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au chef de département"
        )
    
    if current_user.role == "ADMIN":
        return None  # Admin has access to all departments
    
    dept_head = await prisma.chefdepartement.find_unique(
        where={"id_utilisateur": current_user.id},
        include={"departement": True}
    )
    
    if not dept_head:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil chef de département non trouvé"
        )
    
    return dept_head


def parse_time(time_str: str) -> time:
    """Parse time string HH:MM to time object"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format d'heure invalide: {time_str}. Utilisez HH:MM"
        )


# ===========================
# DEPARTMENT HEAD ENDPOINTS
# (Create and manage schedules)
# ===========================

@router.post("/semester", status_code=status.HTTP_201_CREATED)
async def create_semester_schedule(
    schedule_data: SemesterScheduleCreate,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_dept_head)
):
    """
    **Créer un emploi du temps pour tout le semestre**
    
    Le chef de département crée un cours récurrent (ex: chaque lundi 8h30-10h00)
    et le système génère automatiquement toutes les séances du semestre.
    
    L'emploi du temps de l'enseignant est créé automatiquement à partir
    des cours des étudiants.
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    service = TimetableService(prisma)
    
    # Parse times
    start_time = parse_time(schedule_data.start_time)
    end_time = parse_time(schedule_data.end_time)
    
    # Validate times
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'heure de fin doit être après l'heure de début"
        )
    
    # Create template
    template = ScheduleTemplate(
        matiere_id=schedule_data.matiere_id,
        groupe_id=schedule_data.groupe_id,
        enseignant_id=schedule_data.enseignant_id,
        salle_id=schedule_data.salle_id,
        day_of_week=schedule_data.day_of_week,
        start_time=start_time,
        end_time=end_time,
        recurrence_type=schedule_data.recurrence_type,
        semester_start=schedule_data.semester_start,
        semester_end=schedule_data.semester_end
    )
    
    # Get department ID
    department_id = dept_head.id_departement if dept_head else None
    
    if not department_id:
        # For admin, get department from matiere
        matiere = await prisma.matiere.find_unique(
            where={"id": schedule_data.matiere_id},
            include={"specialite": True}
        )
        if matiere:
            department_id = matiere.specialite.id_departement
    
    try:
        result = await service.create_semester_schedule(template, department_id)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "created_count": result["created_count"],
            "conflicts_count": len(result["conflicts"]),
            "conflicts": result["conflicts"][:5] if result["conflicts"] else [],  # Show first 5 conflicts
            "schedule_ids": result["schedule_ids"]
        }
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création: {str(e)}"
        )


@router.get("/department/semester")
async def get_department_semester_schedule(
    semester_start: Optional[date] = Query(None, description="Début du semestre"),
    semester_end: Optional[date] = Query(None, description="Fin du semestre"),
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_dept_head)
):
    """
    **Vue complète du semestre pour le département**
    
    Affiche tous les cours du département pour le semestre.
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    # Default to current semester (Sept-Dec or Jan-May)
    if not semester_start or not semester_end:
        today = date.today()
        if today.month >= 9:  # Fall semester
            semester_start = date(today.year, 9, 1)
            semester_end = date(today.year, 12, 31)
        else:  # Spring semester
            semester_start = date(today.year, 1, 1)
            semester_end = date(today.year, 5, 31)
    
    # Build query
    where_clause = {
        "date": {
            "gte": datetime.combine(semester_start, time.min),
            "lte": datetime.combine(semester_end, time.max)
        }
    }
    
    # Filter by department
    if dept_head:
        where_clause["matiere"] = {
            "specialite": {
                "id_departement": dept_head.id_departement
            }
        }
    
    schedules = await prisma.emploitemps.find_many(
        where=where_clause,
        include={
            "matiere": True,
            "groupe": True,
            "enseignant": True,
            "salle": True
        },
        order=[
            {"date": "asc"},
            {"heure_debut": "asc"}
        ]
    )
    
    # Group by week and day
    weeks = {}
    for schedule in schedules:
        week_num = schedule.date.isocalendar()[1]
        if week_num not in weeks:
            weeks[week_num] = []
        
        weeks[week_num].append({
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "day": schedule.date.strftime("%A"),
            "matiere": schedule.matiere.nom,
            "groupe": schedule.groupe.nom,
            "enseignant": f"{schedule.enseignant.prenom} {schedule.enseignant.nom}",
            "salle": schedule.salle.code,
            "heure_debut": schedule.heure_debut.strftime("%H:%M"),
            "heure_fin": schedule.heure_fin.strftime("%H:%M"),
            "status": schedule.status
        })
    
    return {
        "semester_start": semester_start.isoformat(),
        "semester_end": semester_end.isoformat(),
        "total_sessions": len(schedules),
        "weeks": weeks
    }


@router.patch("/{schedule_id}")
async def update_schedule_session(
    schedule_id: str,
    updates: ScheduleUpdate,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_dept_head)
):
    """
    **Modifier une séance individuelle**
    
    Permet de modifier une séance spécifique sans affecter les autres.
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    service = TimetableService(prisma)
    
    # Get department ID
    department_id = dept_head.id_departement if dept_head else None
    
    if not department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department ID required"
        )
    
    # Prepare update data
    update_data = {}
    if updates.date:
        update_data["date"] = updates.date
    if updates.start_time:
        update_data["heure_debut"] = updates.start_time
    if updates.end_time:
        update_data["heure_fin"] = updates.end_time
    if updates.salle_id:
        update_data["id_salle"] = updates.salle_id
    if updates.status:
        update_data["status"] = updates.status
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune modification fournie"
        )
    
    try:
        result = await service.update_schedule(schedule_id, update_data, department_id)
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{schedule_id}")
async def cancel_schedule_session(
    schedule_id: str,
    reason: Optional[str] = Query(None, description="Raison de l'annulation"),
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_dept_head)
):
    """
    **Annuler une séance**
    
    Marque la séance comme annulée (ne supprime pas l'historique).
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    service = TimetableService(prisma)
    
    department_id = dept_head.id_departement if dept_head else None
    
    if not department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department ID required"
        )
    
    try:
        result = await service.cancel_schedule(schedule_id, department_id, reason)
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


# ===========================
# STUDENT ENDPOINTS (Read-only)
# ===========================

@router.get("/student/weekly", response_model=TimetableResponse)
async def get_student_weekly_timetable(
    week_start: Optional[date] = Query(None, description="Début de la semaine (lundi)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["STUDENT"]))
):
    """
    **Emploi du temps hebdomadaire de l'étudiant (LECTURE SEULE)**
    
    Affiche les cours de l'étudiant pour la semaine.
    Les étudiants ne peuvent pas modifier l'emploi du temps.
    
    **Permissions**: STUDENT
    """
    # Get student info
    student = await prisma.etudiant.find_unique(
        where={"id": current_user.etudiant_id},
        include={"groupe": True}
    )
    
    if not student or not student.groupe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant ou groupe non trouvé"
        )
    
    service = TimetableService(prisma)
    result = await service.get_student_timetable(student.id_groupe, week_start)
    
    return TimetableResponse(**result)


@router.get("/student/today")
async def get_student_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["STUDENT"]))
):
    """
    **Cours du jour pour l'étudiant**
    
    **Permissions**: STUDENT
    """
    # Get student info
    student = await prisma.etudiant.find_unique(
        where={"id": current_user.etudiant_id},
        include={"groupe": True}
    )
    
    if not student or not student.groupe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant ou groupe non trouvé"
        )
    
    today = date.today()
    
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_groupe": student.id_groupe,
            "date": {
                "gte": datetime.combine(today, time.min),
                "lt": datetime.combine(today, time.max)
            },
            "status": {"not": "CANCELED"}
        },
        include={
            "matiere": True,
            "enseignant": True,
            "salle": True
        },
        order={"heure_debut": "asc"}
    )
    
    return {
        "date": today.isoformat(),
        "courses": [
            {
                "id": s.id,
                "matiere": s.matiere.nom,
                "enseignant": f"{s.enseignant.prenom} {s.enseignant.nom}",
                "salle": s.salle.code,
                "heure_debut": s.heure_debut.strftime("%H:%M"),
                "heure_fin": s.heure_fin.strftime("%H:%M"),
                "status": s.status
            }
            for s in schedules
        ]
    }


# ===========================
# TEACHER ENDPOINTS (Read-only, Auto-generated)
# ===========================

@router.get("/teacher/weekly", response_model=TimetableResponse)
async def get_teacher_weekly_timetable(
    week_start: Optional[date] = Query(None, description="Début de la semaine (lundi)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["TEACHER"]))
):
    """
    **Emploi du temps hebdomadaire de l'enseignant (LECTURE SEULE, AUTO-GÉNÉRÉ)**
    
    Affiche les cours de l'enseignant pour la semaine.
    Cet emploi du temps est généré automatiquement à partir des cours
    assignés aux groupes d'étudiants.
    
    Les enseignants ne peuvent pas modifier leur emploi du temps.
    Seul le chef de département peut le faire.
    
    **Permissions**: TEACHER
    """
    # Get teacher info
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil enseignant non trouvé"
        )
    
    service = TimetableService(prisma)
    result = await service.get_teacher_timetable(teacher.id, week_start)
    
    return TimetableResponse(**result)


@router.get("/teacher/today")
async def get_teacher_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["TEACHER"]))
):
    """
    **Cours du jour pour l'enseignant**
    
    **Permissions**: TEACHER
    """
    # Get teacher info
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil enseignant non trouvé"
        )
    
    today = date.today()
    
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_enseignant": teacher.id,
            "date": {
                "gte": datetime.combine(today, time.min),
                "lt": datetime.combine(today, time.max)
            },
            "status": {"not": "CANCELED"}
        },
        include={
            "matiere": True,
            "groupe": True,
            "salle": True
        },
        order={"heure_debut": "asc"}
    )
    
    return {
        "date": today.isoformat(),
        "note": "Emploi du temps généré automatiquement",
        "courses": [
            {
                "id": s.id,
                "matiere": s.matiere.nom,
                "groupe": s.groupe.nom,
                "salle": s.salle.code,
                "heure_debut": s.heure_debut.strftime("%H:%M"),
                "heure_fin": s.heure_fin.strftime("%H:%M"),
                "status": s.status
            }
            for s in schedules
        ]
    }


# ===========================
# RESOURCE ENDPOINTS
# ===========================

@router.get("/resources/available")
async def get_available_resources(
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_dept_head)
):
    """
    **Obtenir toutes les ressources disponibles pour créer un emploi du temps**
    
    Retourne: matières, groupes, enseignants, salles du département
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    department_id = dept_head.id_departement if dept_head else None
    
    where_clause = {}
    if department_id:
        where_clause = {"id_departement": department_id}
    
    # Get matières
    matieres = await prisma.matiere.find_many(
        where={"specialite": where_clause} if department_id else{},
        include={"enseignant": True, "specialite": True}
    )
    
    # Get groupes
    groupes = await prisma.groupe.find_many(
        include={
            "niveau": {
                "include": {"specialite": True}
            }
        }
    )
    
    if department_id:
        groupes = [g for g in groupes if g.niveau.specialite.id_departement == department_id]
    
    # Get enseignants
    enseignants = await prisma.enseignant.find_many(
        where=where_clause if department_id else {}
    )
    
    # Get salles
    salles = await prisma.salle.find_many(
        order={"code": "asc"}
    )
    
    return {
        "matieres": [
            {
                "id": m.id,
                "nom": m.nom,
                "code": m.code if hasattr(m, 'code') and m.code else m.id[:6].upper()
            }
            for m in matieres
        ],
        "groupes": [
            {
                "id": g.id,
                "nom": g.nom,
                "niveau": g.niveau.nom,
                "specialite": g.niveau.specialite.nom
            }
            for g in groupes
        ],
        "enseignants": [
            {
                "id": e.id,
                "nom": e.nom,
                "prenom": e.prenom,
                "email": e.email
            }
            for e in enseignants
        ],
        "salles": [
            {
                "id": s.id,
                "code": s.code,
                "type": s.type,
                "capacite": s.capacite
            }
            for s in salles
        ]
    }


@router.get("/group/{group_id}/weekly", response_model=TimetableResponse)
async def get_group_weekly_timetable(
    group_id: str,
    week_start: Optional[date] = Query(None, description="Début de la semaine (lundi)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["DEPARTMENT_HEAD", "ADMIN"]))
):
    """
    **Emploi du temps hebdomadaire d'un groupe**
    
    Affiche les cours d'un groupe pour la semaine.
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    # Verify group exists
    group = await prisma.groupe.find_unique(where={"id": group_id})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe non trouvé"
        )
    
    service = TimetableService(prisma)
    result = await service.get_student_timetable(group_id, week_start)
    
    return TimetableResponse(**result)


@router.get("/group/{group_id}/semester")
async def get_group_semester_schedule(
    group_id: str,
    semester_start: Optional[date] = Query(None, description="Début du semestre"),
    semester_end: Optional[date] = Query(None, description="Fin du semestre"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["DEPARTMENT_HEAD", "ADMIN"]))
):
    """
    **Emploi du temps complet du semestre pour un groupe**
    
    Retourne toutes les sessions du groupe pour le semestre entier, organisées par semaine.
    
    **Permissions**: DEPARTMENT_HEAD, ADMIN
    """
    # Verify group exists
    group = await prisma.groupe.find_unique(where={"id": group_id})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe non trouvé"
        )
    
    # Default to current academic year if not specified
    if not semester_start:
        semester_start = date(2025, 9, 1)
    if not semester_end:
        semester_end = date(2025, 12, 31)
    
    # Get all schedules for the semester
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_groupe": group_id,
            "date": {
                "gte": datetime.combine(semester_start, time.min),
                "lte": datetime.combine(semester_end, time.max)
            },
            "status": {"not": "CANCELED"}
        },
        include={
            "matiere": True,
            "enseignant": True,
            "salle": True,
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            }
        },
        order=[
            {"date": "asc"},
            {"heure_debut": "asc"}
        ]
    )
    
    # Organize by week
    service = TimetableService(prisma)
    weeks = {}
    current_week_start = semester_start - timedelta(days=semester_start.weekday())
    
    while current_week_start <= semester_end:
        week_end = current_week_start + timedelta(days=6)
        week_key = current_week_start.isoformat()
        
        # Filter schedules for this week
        week_schedules = [
            s for s in schedules 
            if current_week_start <= s.date.date() <= week_end
        ]
        
        if week_schedules:
            timetable = service._organize_by_day(week_schedules)
            weeks[week_key] = {
                "week_start": current_week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "timetable": timetable,
                "total_hours": service._calculate_total_hours(week_schedules),
                "session_count": len(week_schedules)
            }
        
        current_week_start += timedelta(days=7)
    
    return {
        "semester_start": semester_start.isoformat(),
        "semester_end": semester_end.isoformat(),
        "total_sessions": len(schedules),
        "weeks": weeks
    }
