"""
Semester Timetable Management System
Chef de Département creates complete semester schedules
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from datetime import datetime, time, timedelta
from pydantic import BaseModel

from app.db.prisma_client import get_prisma
from app.core.deps import require_department_head
from app.routers.department_head_timetable import get_dept_head_department

router = APIRouter(prefix="/department-head/semester-timetable", tags=["Department Head - Semester Timetable"])

class RecurringScheduleSlot(BaseModel):
    """A recurring schedule slot for the semester"""
    week_day: int  # 1=Monday, 2=Tuesday, ..., 7=Sunday
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    subject_id: str
    group_id: str
    teacher_id: str
    room_id: str

class SemesterTimetableCreate(BaseModel):
    """Create complete semester timetable"""
    semester: str  # e.g., "2024-2025-S1" or "2024-2025-S2"
    start_date: str  # First day of semester (YYYY-MM-DD)
    end_date: str    # Last day of semester (YYYY-MM-DD)
    schedules: List[RecurringScheduleSlot]
    exclude_dates: List[str] = []  # Holidays/breaks (YYYY-MM-DD format)

class SemesterInfo(BaseModel):
    name: str
    start_date: str
    end_date: str
    is_active: bool

@router.post("/create-semester")
async def create_semester_timetable(
    timetable_data: SemesterTimetableCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Create complete semester timetable
    
    This creates recurring schedules for the entire semester.
    Chef de Département creates this once per semester.
    """
    try:
        department = await get_dept_head_department(current_user, prisma)
        
        # Parse dates
        start_date = datetime.strptime(timetable_data.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(timetable_data.end_date, "%Y-%m-%d").date()
        exclude_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in timetable_data.exclude_dates]
        
        # Delete existing schedules for this semester (if updating)
        await prisma.emploitemps.delete_many(
            where={
                "semester": timetable_data.semester,
                "groupe": {
                    "niveau": {
                        "specialite": {
                            "id_departement": department.id
                        }
                    }
                }
            }
        )
        
        created_schedules = []
        
        # Create schedules for each recurring slot
        for slot in timetable_data.schedules:
            # Validate that group belongs to department
            group = await prisma.groupe.find_unique(
                where={"id": slot.group_id},
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
                    detail=f"Group {slot.group_id} does not belong to your department"
                )
            
            # Generate all dates for this day of week in the semester
            current_date = start_date
            while current_date <= end_date:
                # Check if this is the right day of week
                if current_date.weekday() + 1 == slot.week_day:  # Python weekday: 0=Monday
                    # Skip if in exclude dates
                    if current_date not in exclude_dates:
                        # Parse times
                        start_time = datetime.strptime(slot.start_time, "%H:%M").time()
                        end_time = datetime.strptime(slot.end_time, "%H:%M").time()
                        
                        # Create schedule entry
                        schedule = await prisma.emploitemps.create(
                            data={
                                "date": datetime.combine(current_date, time(0, 0)),
                                "heure_debut": datetime.combine(current_date, start_time),
                                "heure_fin": datetime.combine(current_date, end_time),
                                "id_salle": slot.room_id,
                                "id_matiere": slot.subject_id,
                                "id_groupe": slot.group_id,
                                "id_enseignant": slot.teacher_id,
                                "semester": timetable_data.semester,
                                "week_day": slot.week_day,
                                "is_recurring": True,
                                "status": "PLANNED"
                            }
                        )
                        created_schedules.append(schedule.id)
                
                current_date += timedelta(days=1)
        
        return {
            "message": f"Emploi du temps semestriel créé avec succès",
            "semester": timetable_data.semester,
            "total_schedules": len(created_schedules),
            "start_date": timetable_data.start_date,
            "end_date": timetable_data.end_date,
            "schedules_created": len(created_schedules)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'emploi du temps: {str(e)}"
        )

@router.get("/current-semester")
async def get_current_semester_info(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get information about the current semester"""
    # Determine current semester based on date
    now = datetime.now()
    year = now.year
    
    # Semester 1: September - January
    # Semester 2: February - June
    if now.month >= 9 or now.month <= 1:
        semester = f"{year}-{year+1}-S1"
        start_date = f"{year}-09-01"
        end_date = f"{year+1}-01-31"
    else:
        semester = f"{year-1 if now.month <= 6 else year}-{year if now.month <= 6 else year+1}-S2"
        start_date = f"{year}-02-01"
        end_date = f"{year}-06-30"
    
    # Check if timetable exists for this semester
    department = await get_dept_head_department(current_user, prisma)
    
    schedule_count = await prisma.emploitemps.count(
        where={
            "semester": semester,
            "groupe": {
                "niveau": {
                    "specialite": {
                        "id_departement": department.id
                    }
                }
            }
        }
    )
    
    return {
        "semester": semester,
        "start_date": start_date,
        "end_date": end_date,
        "is_active": schedule_count > 0,
        "schedule_count": schedule_count
    }

@router.get("/semester/{semester}/schedules")
async def get_semester_schedules(
    semester: str,
    group_id: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get all schedules for a semester"""
    department = await get_dept_head_department(current_user, prisma)
    
    where_clause = {
        "semester": semester,
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
    
    schedules = await prisma.emploitemps.find_many(
        where=where_clause,
        include={
            "salle": True,
            "matiere": True,
            "groupe": True,
            "enseignant": {
                "include": {
                    "utilisateur": True
                }
            }
        },
        order_by=[
            {"date": "asc"},
            {"heure_debut": "asc"}
        ]
    )
    
    return {
        "semester": semester,
        "total": len(schedules),
        "schedules": schedules
    }

@router.delete("/semester/{semester}")
async def delete_semester_timetable(
    semester: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Delete entire semester timetable"""
    department = await get_dept_head_department(current_user, prisma)
    
    result = await prisma.emploitemps.delete_many(
        where={
            "semester": semester,
            "groupe": {
                "niveau": {
                    "specialite": {
                        "id_departement": department.id
                    }
                }
            }
        }
    )
    
    return {
        "message": f"Emploi du temps du semestre {semester} supprimé",
        "deleted_count": result
    }

@router.put("/schedule/{schedule_id}")
async def update_single_schedule(
    schedule_id: str,
    update_data: dict,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Update a single schedule entry"""
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify schedule belongs to department
    schedule = await prisma.emploitemps.find_unique(
        where={"id": schedule_id},
        include={
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            }
        }
    )
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emploi du temps non trouvé"
        )
    
    if schedule.groupe.niveau.specialite.id_departement != department.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cet emploi du temps n'appartient pas à votre département"
        )
    
    # Update the schedule
    updated_schedule = await prisma.emploitemps.update(
        where={"id": schedule_id},
        data=update_data
    )
    
    return {
        "message": "Emploi du temps mis à jour avec succès",
        "schedule": updated_schedule
    }
