from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma
from datetime import datetime, time
from pydantic import BaseModel

from app.db.prisma_client import get_prisma
from app.core.deps import require_department_head, get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/department-head/timetable", tags=["Department Head - Timetable Management"])

# Pydantic models for timetable management
class TimeSlot(BaseModel):
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"

class ScheduleCreate(BaseModel):
    date: str           # Format: "YYYY-MM-DD"
    start_time: str     # Format: "HH:MM"
    end_time: str       # Format: "HH:MM"
    subject_id: str
    group_id: str
    teacher_id: str
    room_id: str

class ScheduleUpdate(BaseModel):
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    subject_id: Optional[str] = None
    group_id: Optional[str] = None
    teacher_id: Optional[str] = None
    room_id: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: str
    date: datetime
    heure_debut: datetime
    heure_fin: datetime
    salle: dict
    matiere: dict
    groupe: dict
    enseignant: dict
    status: str
    createdAt: datetime

class BulkScheduleCreate(BaseModel):
    schedules: List[ScheduleCreate]
    apply_weekly: bool = False  # Apply same schedule for multiple weeks
    weeks_count: int = 1

class SubjectCreate(BaseModel):
    nom: str
    id_specialite: str
    id_enseignant: str

class SubjectUpdate(BaseModel):
    nom: Optional[str] = None
    id_specialite: Optional[str] = None
    id_enseignant: Optional[str] = None

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

@router.get("/groups")
async def get_department_groups(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all groups in the department head's department"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Get groups through specialties in the department
    groups = await prisma.groupe.find_many(
        where={
            "niveau": {
                "specialite": {
                    "id_departement": department.id
                }
            }
        },
        include={
            "niveau": {
                "include": {
                    "specialite": {
                        "include": {"departement": True}
                    }
                }
            }
        },
        order=[{"nom": "asc"}]
    )
    
    return groups

@router.get("/teachers")
async def get_department_teachers(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all teachers in the department head's department"""
    department = await get_dept_head_department(current_user, prisma)
    
    teachers = await prisma.enseignant.find_many(
        where={"id_departement": department.id},
        include={"utilisateur": True},
        order=[{"nom": "asc"}]
    )
    
    return teachers

@router.get("/subjects")
async def get_department_subjects(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all subjects in the department head's department"""
    department = await get_dept_head_department(current_user, prisma)
    
    subjects = await prisma.matiere.find_many(
        where={
            "specialite": {
                "id_departement": department.id
            }
        },
        include={
            "specialite": {
                "include": {"departement": True}
            },
            "enseignant": True
        },
        order=[{"nom": "asc"}]
    )
    
    return subjects

@router.get("/subjects/by-speciality/{speciality_id}")
async def get_subjects_by_speciality(
    speciality_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all subjects for a specific speciality"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify the speciality belongs to the department
    speciality = await prisma.specialite.find_first(
        where={
            "id": speciality_id,
            "id_departement": department.id
        }
    )
    
    if not speciality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spécialité non trouvée ou non autorisée"
        )
    
    subjects = await prisma.matiere.find_many(
        where={"id_specialite": speciality_id},
        include={
            "specialite": True,
            "enseignant": True
        },
        order=[{"nom": "asc"}]
    )
    
    return subjects

@router.get("/specialities")
async def get_department_specialities(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all specialities in the department head's department"""
    department = await get_dept_head_department(current_user, prisma)
    
    specialities = await prisma.specialite.find_many(
        where={"id_departement": department.id},
        include={
            "departement": True,
            "_count": {
                "select": {
                    "matieres": True,
                    "niveaux": True,
                    "etudiants": True
                }
            }
        },
        order=[{"nom": "asc"}]
    )
    
    return specialities

@router.get("/rooms")
async def get_available_rooms(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all available rooms"""
    rooms = await prisma.salle.find_many(
        order=[{"code": "asc"}]
    )
    
    return rooms

# SUBJECT MANAGEMENT

@router.post("/subjects")
async def create_subject(
    subject_data: SubjectCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create a new subject for the department"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify the speciality belongs to the department
    speciality = await prisma.specialite.find_first(
        where={
            "id": subject_data.id_specialite,
            "id_departement": department.id
        }
    )
    
    if not speciality:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La spécialité sélectionnée n'appartient pas à votre département"
        )
    
    # Verify the teacher belongs to the department
    teacher = await prisma.enseignant.find_first(
        where={
            "id": subject_data.id_enseignant,
            "id_departement": department.id
        }
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'enseignant sélectionné n'appartient pas à votre département"
        )
    
    # Check if subject already exists in this speciality
    existing_subject = await prisma.matiere.find_first(
        where={
            "nom": subject_data.nom,
            "id_specialite": subject_data.id_specialite
        }
    )
    
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une matière avec ce nom existe déjà dans cette spécialité"
        )
    
    subject = await prisma.matiere.create(
        data={
            "nom": subject_data.nom,
            "id_specialite": subject_data.id_specialite,
            "id_enseignant": subject_data.id_enseignant
        },
        include={
            "specialite": {
                "include": {"departement": True}
            },
            "enseignant": True
        }
    )
    
    return subject

@router.put("/subjects/{subject_id}")
async def update_subject(
    subject_id: str,
    subject_data: SubjectUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Update a subject"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify the subject belongs to the department
    subject = await prisma.matiere.find_first(
        where={
            "id": subject_id,
            "specialite": {
                "id_departement": department.id
            }
        }
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée ou non autorisée"
        )
    
    update_data = {}
    
    if subject_data.nom is not None:
        update_data["nom"] = subject_data.nom
    
    if subject_data.id_specialite is not None:
        # Verify the new speciality belongs to the department
        speciality = await prisma.specialite.find_first(
            where={
                "id": subject_data.id_specialite,
                "id_departement": department.id
            }
        )
        
        if not speciality:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La spécialité sélectionnée n'appartient pas à votre département"
            )
        
        update_data["id_specialite"] = subject_data.id_specialite
    
    if subject_data.id_enseignant is not None:
        # Verify the teacher belongs to the department
        teacher = await prisma.enseignant.find_first(
            where={
                "id": subject_data.id_enseignant,
                "id_departement": department.id
            }
        )
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'enseignant sélectionné n'appartient pas à votre département"
            )
        
        update_data["id_enseignant"] = subject_data.id_enseignant
    
    updated_subject = await prisma.matiere.update(
        where={"id": subject_id},
        data=update_data,
        include={
            "specialite": {
                "include": {"departement": True}
            },
            "enseignant": True
        }
    )
    
    return updated_subject

@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Delete a subject"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify the subject belongs to the department
    subject = await prisma.matiere.find_first(
        where={
            "id": subject_id,
            "specialite": {
                "id_departement": department.id
            }
        }
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière non trouvée ou non autorisée"
        )
    
    # Check if subject is used in any schedules
    schedule_count = await prisma.emploitemps.count(
        where={"id_matiere": subject_id}
    )
    
    if schedule_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de supprimer cette matière car elle est utilisée dans {schedule_count} emploi(s) du temps"
        )
    
    await prisma.matiere.delete(where={"id": subject_id})
    
    return {"message": "Matière supprimée avec succès"}

@router.get("/schedules")
async def get_department_schedules(
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    teacher_id: Optional[str] = Query(None, description="Filter by teacher ID"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get schedules for the department head's department"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Build where clause
    where_clause = {
        "groupe": {
            "niveau": {
                "specialite": {
                    "id_departement": department.id
                }
            }
        }
    }
    
    if group_id:
        where_clause["id_groupe"] = group_id
    
    if teacher_id:
        where_clause["id_enseignant"] = teacher_id
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        where_clause["date"] = {"gte": date_from_obj}
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        if "date" in where_clause:
            where_clause["date"]["lte"] = date_to_obj
        else:
            where_clause["date"] = {"lte": date_to_obj}
    
    schedules = await prisma.emploitemps.find_many(
        where=where_clause,
        include={
            "salle": True,
            "matiere": True,
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {"specialite": True}
                    }
                }
            },
            "enseignant": {
                "include": {"utilisateur": True}
            }
        },
        order=[
            {"date": "asc"},
            {"heure_debut": "asc"}
        ]
    )
    
    return schedules

@router.post("/schedules")
async def create_schedule(
    schedule_data: ScheduleCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create a new schedule entry"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Validate that the group belongs to the department
    group = await prisma.groupe.find_unique(
        where={"id": schedule_data.group_id},
        include={
            "niveau": {
                "include": {
                    "specialite": True
                }
            }
        }
    )
    
    if not group or group.niveau.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Group does not belong to your department"
        )
    
    # Validate teacher belongs to department
    teacher = await prisma.enseignant.find_unique(
        where={"id": schedule_data.teacher_id}
    )
    
    if not teacher or teacher.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher does not belong to your department"
        )
    
    # Validate subject belongs to department
    subject = await prisma.matiere.find_unique(
        where={"id": schedule_data.subject_id},
        include={"specialite": True}
    )
    
    if not subject or subject.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subject does not belong to your department"
        )
    
    # Validate room exists
    room = await prisma.salle.find_unique(where={"id": schedule_data.room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Parse date and times
    schedule_date = datetime.strptime(schedule_data.date, "%Y-%m-%d").date()
    start_time_obj = datetime.strptime(schedule_data.start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(schedule_data.end_time, "%H:%M").time()
    
    # Create datetime objects for the schedule
    start_datetime = datetime.combine(schedule_date, start_time_obj)
    end_datetime = datetime.combine(schedule_date, end_time_obj)
    
    # Check for conflicts (same room, same time)
    existing_schedule = await prisma.emploitemps.find_first(
        where={
            "date": schedule_date,
            "id_salle": schedule_data.room_id,
            "OR": [
                {
                    "AND": [
                        {"heure_debut": {"lte": start_datetime}},
                        {"heure_fin": {"gt": start_datetime}}
                    ]
                },
                {
                    "AND": [
                        {"heure_debut": {"lt": end_datetime}},
                        {"heure_fin": {"gte": end_datetime}}
                    ]
                },
                {
                    "AND": [
                        {"heure_debut": {"gte": start_datetime}},
                        {"heure_fin": {"lte": end_datetime}}
                    ]
                }
            ]
        }
    )
    
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is already booked for this time slot"
        )
    
    # Create the schedule
    new_schedule = await prisma.emploitemps.create(
        data={
            "date": schedule_date,
            "heure_debut": start_datetime,
            "heure_fin": end_datetime,
            "id_salle": schedule_data.room_id,
            "id_matiere": schedule_data.subject_id,
            "id_groupe": schedule_data.group_id,
            "id_enseignant": schedule_data.teacher_id,
            "status": "PLANNED"
        },
        include={
            "salle": True,
            "matiere": True,
            "groupe": True,
            "enseignant": {
                "include": {"utilisateur": True}
            }
        }
    )
    
    return new_schedule

@router.post("/schedules/bulk")
async def create_bulk_schedules(
    bulk_data: BulkScheduleCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Create multiple schedule entries at once"""
    department = await get_dept_head_department(current_user, prisma)
    
    created_schedules = []
    errors = []
    
    for week_offset in range(bulk_data.weeks_count):
        for schedule_data in bulk_data.schedules:
            try:
                # Adjust date for weekly repetition
                original_date = datetime.strptime(schedule_data.date, "%Y-%m-%d").date()
                adjusted_date = original_date.replace(
                    year=original_date.year,
                    month=original_date.month,
                    day=original_date.day + (week_offset * 7)
                )
                
                # Create adjusted schedule data
                adjusted_schedule = ScheduleCreate(
                    date=adjusted_date.strftime("%Y-%m-%d"),
                    start_time=schedule_data.start_time,
                    end_time=schedule_data.end_time,
                    subject_id=schedule_data.subject_id,
                    group_id=schedule_data.group_id,
                    teacher_id=schedule_data.teacher_id,
                    room_id=schedule_data.room_id
                )
                
                # Create individual schedule (reuse the single create logic)
                new_schedule = await create_schedule(adjusted_schedule, prisma, current_user)
                created_schedules.append(new_schedule)
                
            except Exception as e:
                errors.append({
                    "schedule": schedule_data.dict(),
                    "week": week_offset + 1,
                    "error": str(e)
                })
    
    return {
        "created_count": len(created_schedules),
        "created_schedules": created_schedules,
        "errors": errors
    }

@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    schedule_update: ScheduleUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Update an existing schedule entry"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Find the schedule and verify it belongs to the department
    schedule = await prisma.emploitemps.find_unique(
        where={"id": schedule_id},
        include={
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {"specialite": True}
                    }
                }
            }
        }
    )
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    if schedule.groupe.niveau.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Schedule does not belong to your department"
        )
    
    # Build update data
    update_data = {}
    
    if schedule_update.date:
        update_data["date"] = datetime.strptime(schedule_update.date, "%Y-%m-%d").date()
    
    if schedule_update.start_time:
        start_time_obj = datetime.strptime(schedule_update.start_time, "%H:%M").time()
        schedule_date = update_data.get("date", schedule.date)
        update_data["heure_debut"] = datetime.combine(schedule_date, start_time_obj)
    
    if schedule_update.end_time:
        end_time_obj = datetime.strptime(schedule_update.end_time, "%H:%M").time()
        schedule_date = update_data.get("date", schedule.date)
        update_data["heure_fin"] = datetime.combine(schedule_date, end_time_obj)
    
    if schedule_update.room_id:
        update_data["id_salle"] = schedule_update.room_id
    
    if schedule_update.subject_id:
        update_data["id_matiere"] = schedule_update.subject_id
    
    if schedule_update.teacher_id:
        update_data["id_enseignant"] = schedule_update.teacher_id
    
    if schedule_update.group_id:
        update_data["id_groupe"] = schedule_update.group_id
    
    # Update the schedule
    updated_schedule = await prisma.emploitemps.update(
        where={"id": schedule_id},
        data=update_data,
        include={
            "salle": True,
            "matiere": True,
            "groupe": True,
            "enseignant": {
                "include": {"utilisateur": True}
            }
        }
    )
    
    return updated_schedule

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Delete a schedule entry"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Find the schedule and verify it belongs to the department
    schedule = await prisma.emploitemps.find_unique(
        where={"id": schedule_id},
        include={
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {"specialite": True}
                    }
                }
            }
        }
    )
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    if schedule.groupe.niveau.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Schedule does not belong to your department"
        )
    
    # Delete the schedule
    await prisma.emploitemps.delete(where={"id": schedule_id})
    
    return {"message": "Schedule deleted successfully"}

@router.get("/conflicts")
async def check_schedule_conflicts(
    date_from: Optional[str] = Query(None, description="Check conflicts from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Check conflicts to date (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Check for scheduling conflicts in the department"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Build date filter
    date_filter = {}
    if date_from:
        date_filter["gte"] = datetime.strptime(date_from, "%Y-%m-%d").date()
    if date_to:
        date_filter["lte"] = datetime.strptime(date_to, "%Y-%m-%d").date()
    
    where_clause = {
        "groupe": {
            "niveau": {
                "specialite": {
                    "id_departement": department.id
                }
            }
        }
    }
    
    if date_filter:
        where_clause["date"] = date_filter
    
    schedules = await prisma.emploitemps.find_many(
        where=where_clause,
        include={
            "salle": True,
            "enseignant": {"include": {"utilisateur": True}},
            "groupe": True
        },
        order=[
            {"date": "asc"},
            {"heure_debut": "asc"}
        ]
    )
    
    conflicts = []
    
    # Check for room conflicts
    room_schedules = {}
    teacher_schedules = {}
    
    for schedule in schedules:
        schedule_key = f"{schedule.date}_{schedule.id_salle}"
        teacher_key = f"{schedule.date}_{schedule.id_enseignant}"
        
        # Check room conflicts
        if schedule_key in room_schedules:
            for existing in room_schedules[schedule_key]:
                if (schedule.heure_debut < existing.heure_fin and 
                    schedule.heure_fin > existing.heure_debut):
                    conflicts.append({
                        "type": "room_conflict",
                        "room": schedule.salle.code,
                        "date": schedule.date.isoformat(),
                        "schedules": [
                            {
                                "id": schedule.id,
                                "time": f"{schedule.heure_debut.strftime('%H:%M')}-{schedule.heure_fin.strftime('%H:%M')}",
                                "group": schedule.groupe.nom
                            },
                            {
                                "id": existing.id,
                                "time": f"{existing.heure_debut.strftime('%H:%M')}-{existing.heure_fin.strftime('%H:%M')}",
                                "group": existing.groupe.nom
                            }
                        ]
                    })
        else:
            room_schedules[schedule_key] = []
        
        room_schedules[schedule_key].append(schedule)
        
        # Check teacher conflicts
        if teacher_key in teacher_schedules:
            for existing in teacher_schedules[teacher_key]:
                if (schedule.heure_debut < existing.heure_fin and 
                    schedule.heure_fin > existing.heure_debut):
                    conflicts.append({
                        "type": "teacher_conflict",
                        "teacher": f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}",
                        "date": schedule.date.isoformat(),
                        "schedules": [
                            {
                                "id": schedule.id,
                                "time": f"{schedule.heure_debut.strftime('%H:%M')}-{schedule.heure_fin.strftime('%H:%M')}",
                                "group": schedule.groupe.nom
                            },
                            {
                                "id": existing.id,
                                "time": f"{existing.heure_debut.strftime('%H:%M')}-{existing.heure_fin.strftime('%H:%M')}",
                                "group": existing.groupe.nom
                            }
                        ]
                    })
        else:
            teacher_schedules[teacher_key] = []
        
        teacher_schedules[teacher_key].append(schedule)
    
    return {
        "conflicts_found": len(conflicts),
        "conflicts": conflicts
    }