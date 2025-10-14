"""
Fixed timetable management API router with correct field names
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
import logging
from datetime import datetime, time

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/timetable", tags=["Timetable Management"])
logger = logging.getLogger(__name__)

def get_day_of_week(date_obj):
    """Get day of week number from date (1=Monday, 7=Sunday)"""
    if date_obj:
        return date_obj.isoweekday()
    return 1

@router.get("/student", response_model=List[dict])
async def get_student_timetable(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["STUDENT", "ADMIN", "DEPARTMENT_HEAD"]))
):
    """Get student's weekly timetable"""
    try:
        # If admin or department head, get all schedules (for overview)
        if current_user.role in ["ADMIN", "DEPARTMENT_HEAD"]:
            schedules = await prisma.emploitemps.find_many(
                include={
                    "matiere": True,
                    "enseignant": {
                        "include": {"utilisateur": True}
                    },
                    "salle": True,
                    "groupe": True
                },
                order={
                    "date": "asc"
                }
            )
        else:
            # For students, get their group's timetable
            if not current_user.etudiant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil étudiant non trouvé - utilisateur non lié à un étudiant"
                )
            
            student = await prisma.etudiant.find_unique(
                where={"id": current_user.etudiant_id},
                include={"groupe": True}
            )
            
            if not student or not student.groupe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil étudiant ou groupe non trouvé"
                )
            
            schedules = await prisma.emploitemps.find_many(
                where={"id_groupe": student.groupe.id},
                include={
                    "matiere": True,
                    "enseignant": {
                        "include": {"utilisateur": True}
                    },
                    "salle": True,
                    "groupe": True
                },
                order={
                    "date": "asc"
                }
            )
        
        # Transform data for frontend
        timetable_entries = []
        for schedule in schedules:
            # Get day of week from date
            day_of_week = get_day_of_week(schedule.date)
            
            # Create time slot based on schedule times
            time_slot = {
                "id": f"{schedule.heure_debut}_{schedule.heure_fin}",
                "start_time": schedule.heure_debut.strftime("%H:%M") if schedule.heure_debut else "00:00",
                "end_time": schedule.heure_fin.strftime("%H:%M") if schedule.heure_fin else "00:00",
                "label": f"{schedule.heure_debut.strftime('%Hh%M') if schedule.heure_debut else '00h00'} à {schedule.heure_fin.strftime('%Hh%M') if schedule.heure_fin else '00h00'}"
            }
            
            entry = {
                "id": schedule.id,
                "day_of_week": day_of_week,
                "time_slot": time_slot,
                "subject": {
                    "nom": schedule.matiere.nom if schedule.matiere else "Non assignée",
                    "code": getattr(schedule.matiere, 'code', None) if schedule.matiere else None
                },
                "teacher": {
                    "nom": schedule.enseignant.utilisateur.nom if schedule.enseignant and schedule.enseignant.utilisateur else "Non assigné",
                    "prenom": schedule.enseignant.utilisateur.prenom if schedule.enseignant and schedule.enseignant.utilisateur else "Non assigné"
                },
                "room": {
                    "nom": schedule.salle.code if schedule.salle else "Non assignée",
                    "type": schedule.salle.type if schedule.salle else "OTHER"
                },
                "group": {
                    "nom": schedule.groupe.nom if schedule.groupe else "Non assigné"
                }
            }
            timetable_entries.append(entry)
        
        return timetable_entries
        
    except Exception as e:
        logger.error(f"Error fetching student timetable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'emploi du temps: {str(e)}"
        )

@router.get("/teacher", response_model=List[dict])
async def get_teacher_timetable(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["TEACHER", "ADMIN", "DEPARTMENT_HEAD"]))
):
    """Get teacher's weekly timetable"""
    try:
        # If admin or department head, get all schedules
        if current_user.role in ["ADMIN", "DEPARTMENT_HEAD"]:
            schedules = await prisma.emploitemps.find_many(
                include={
                    "matiere": True,
                    "enseignant": {
                        "include": {"utilisateur": True}
                    },
                    "salle": True,
                    "groupe": True
                },
                order={
                    "date": "asc"
                }
            )
        else:
            # For teachers, get their assigned schedules
            if not current_user.enseignant_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil enseignant non trouvé - utilisateur non lié à un enseignant"
                )
            
            teacher = await prisma.enseignant.find_unique(
                where={"id": current_user.enseignant_id}
            )
            
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil enseignant non trouvé"
                )
            
            schedules = await prisma.emploitemps.find_many(
                where={"id_enseignant": teacher.id},
                include={
                    "matiere": True,
                    "enseignant": {
                        "include": {"utilisateur": True}
                    },
                    "salle": True,
                    "groupe": True
                },
                order={
                    "date": "asc"
                }
            )
        
        # Transform data for frontend (same as student endpoint)
        timetable_entries = []
        for schedule in schedules:
            day_of_week = get_day_of_week(schedule.date)
            
            time_slot = {
                "id": f"{schedule.heure_debut}_{schedule.heure_fin}",
                "start_time": schedule.heure_debut.strftime("%H:%M") if schedule.heure_debut else "00:00",
                "end_time": schedule.heure_fin.strftime("%H:%M") if schedule.heure_fin else "00:00",
                "label": f"{schedule.heure_debut.strftime('%Hh%M') if schedule.heure_debut else '00h00'} à {schedule.heure_fin.strftime('%Hh%M') if schedule.heure_fin else '00h00'}"
            }
            
            entry = {
                "id": schedule.id,
                "day_of_week": day_of_week,
                "time_slot": time_slot,
                "subject": {
                    "nom": schedule.matiere.nom if schedule.matiere else "Non assignée",
                    "code": getattr(schedule.matiere, 'code', None) if schedule.matiere else None
                },
                "teacher": {
                    "nom": schedule.enseignant.utilisateur.nom if schedule.enseignant and schedule.enseignant.utilisateur else "Non assigné",
                    "prenom": schedule.enseignant.utilisateur.prenom if schedule.enseignant and schedule.enseignant.utilisateur else "Non assigné"
                },
                "room": {
                    "nom": schedule.salle.code if schedule.salle else "Non assignée",
                    "type": schedule.salle.type if schedule.salle else "OTHER"
                },
                "group": {
                    "nom": schedule.groupe.nom if schedule.groupe else "Non assigné"
                }
            }
            timetable_entries.append(entry)
        
        return timetable_entries
        
    except Exception as e:
        logger.error(f"Error fetching teacher timetable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'emploi du temps: {str(e)}"
        )

@router.get("/weekly-overview", response_model=dict)
async def get_weekly_overview(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN", "DEPARTMENT_HEAD", "TEACHER"]))
):
    """Get weekly timetable overview with statistics"""
    try:
        # Get all schedules for the week
        schedules = await prisma.emploitemps.find_many(
            include={
                "matiere": True,
                "enseignant": {
                    "include": {"utilisateur": True}
                },
                "salle": True,
                "groupe": True
            }
        )
        
        # Calculate statistics
        total_classes = len(schedules)
        unique_subjects = len(set(schedule.matiere.nom for schedule in schedules if schedule.matiere))
        unique_teachers = len(set(f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}" 
                                for schedule in schedules 
                                if schedule.enseignant and schedule.enseignant.utilisateur))
        unique_rooms = len(set(schedule.salle.code for schedule in schedules if schedule.salle))
        
        # Group by day
        daily_schedule = {}
        for i in range(1, 8):  # Monday to Sunday
            daily_schedule[i] = [s for s in schedules if get_day_of_week(s.date) == i]
        
        return {
            "statistics": {
                "total_classes": total_classes,
                "unique_subjects": unique_subjects,
                "unique_teachers": unique_teachers,
                "unique_rooms": unique_rooms,
                "total_hours": total_classes * 1.5  # Assuming 1.5 hours per class
            },
            "daily_schedule": daily_schedule,
            "schedules": [
                {
                    "id": schedule.id,
                    "day_of_week": get_day_of_week(schedule.date),
                    "subject": schedule.matiere.nom if schedule.matiere else "Non assignée",
                    "teacher": f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}" if schedule.enseignant and schedule.enseignant.utilisateur else "Non assigné",
                    "room": schedule.salle.code if schedule.salle else "Non assignée",
                    "group": schedule.groupe.nom if schedule.groupe else "Non assigné",
                    "start_time": schedule.heure_debut.strftime("%H:%M") if schedule.heure_debut else "00:00",
                    "end_time": schedule.heure_fin.strftime("%H:%M") if schedule.heure_fin else "00:00",
                    "date": schedule.date.isoformat() if schedule.date else None
                }
                for schedule in schedules
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching weekly overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du planning hebdomadaire: {str(e)}"
        )