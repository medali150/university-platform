from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from datetime import datetime, date, timedelta
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_student

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/schedule")
async def get_student_schedule(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student's schedule for a date range"""
    
    if not current_user.etudiant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No student record found for this user"
        )
    
    # Get student record
    student = await prisma.etudiant.find_unique(
        where={"id": current_user.etudiant_id},
        include={
            "groupe": True
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Parse dates or use default range (current week)
    if start_date:
        start_dt = datetime.fromisoformat(start_date).date()
    else:
        today = date.today()
        start_dt = today - timedelta(days=today.weekday())  # Start of week (Monday)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date).date()
    else:
        start_dt_obj = start_dt if isinstance(start_dt, date) else start_dt.date()
        end_dt = start_dt_obj + timedelta(days=6)  # End of week (Sunday)
    
    # Convert to datetime for query
    start_datetime = datetime.combine(start_dt, datetime.min.time())
    end_datetime = datetime.combine(end_dt, datetime.max.time())
    
    # Get schedule for student's group
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_groupe": student.id_groupe,
            "date": {
                "gte": start_datetime,
                "lte": end_datetime
            }
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
        order=[{"date": "asc"}, {"heure_debut": "asc"}]
    )
    
    # Check if student has absences for each schedule
    schedule_ids = [schedule.id for schedule in schedules]
    absences = await prisma.absence.find_many(
        where={
            "id_etudiant": student.id,
            "id_emploi": {"in": schedule_ids}
        }
    )
    
    # Create absence map for quick lookup
    absence_map = {absence.id_emploi: absence for absence in absences}
    
    # Format response
    formatted_schedules = []
    for schedule in schedules:
        absence = absence_map.get(schedule.id)
        
        formatted_schedule = {
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "heure_debut": schedule.heure_debut.isoformat(),
            "heure_fin": schedule.heure_fin.isoformat(),
            "status": schedule.status,
            "matiere": {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            },
            "enseignant": {
                "id": schedule.enseignant.id,
                "nom": schedule.enseignant.nom,
                "prenom": schedule.enseignant.prenom
            },
            "salle": {
                "id": schedule.salle.id,
                "code": schedule.salle.code,
                "type": schedule.salle.type
            },
            "groupe": {
                "id": schedule.groupe.id,
                "nom": schedule.groupe.nom,
                "niveau": schedule.groupe.niveau.nom,
                "specialite": schedule.groupe.niveau.specialite.nom
            },
            "absence": {
                "id": absence.id if absence else None,
                "status": absence.statut if absence else None,
                "motif": absence.motif if absence else None,
                "is_absent": bool(absence)
            } if absence else None
        }
        formatted_schedules.append(formatted_schedule)
    
    return {
        "schedules": formatted_schedules,
        "student_info": {
            "id": student.id,
            "nom": student.nom,
            "prenom": student.prenom,
            "email": student.email,
            "groupe": {
                "id": student.groupe.id,
                "nom": student.groupe.nom
            }
        },
        "date_range": {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat()
        }
    }


@router.get("/schedule/today")
async def get_student_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student's schedule for today"""
    
    if not current_user.etudiant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No student record found for this user"
        )
    
    # Get student record
    student = await prisma.etudiant.find_unique(
        where={"id": current_user.etudiant_id},
        include={
            "groupe": True
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get today's date range
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # Get today's schedule
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_groupe": student.id_groupe,
            "date": {
                "gte": start_of_day,
                "lte": end_of_day
            }
        },
        include={
            "matiere": True,
            "enseignant": True,
            "salle": True
        },
        order={"heure_debut": "asc"}
    )
    
    # Check absences for today's classes
    schedule_ids = [schedule.id for schedule in schedules]
    absences = await prisma.absence.find_many(
        where={
            "id_etudiant": student.id,
            "id_emploi": {"in": schedule_ids}
        }
    )
    
    absence_map = {absence.id_emploi: absence for absence in absences}
    
    return [
        {
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "heure_debut": schedule.heure_debut.isoformat(),
            "heure_fin": schedule.heure_fin.isoformat(),
            "status": schedule.status,
            "matiere": {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            },
            "enseignant": {
                "id": schedule.enseignant.id,
                "nom": schedule.enseignant.nom,
                "prenom": schedule.enseignant.prenom
            },
            "salle": {
                "id": schedule.salle.id,
                "code": schedule.salle.code,
                "type": schedule.salle.type
            },
            "absence": {
                "id": absence.id if absence else None,
                "status": absence.statut if absence else None,
                "motif": absence.motif if absence else None,
                "is_absent": bool(absence)
            } if (absence := absence_map.get(schedule.id)) else None
        } for schedule in schedules
    ]


@router.get("/profile")
async def get_student_profile(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student profile information"""
    
    if not current_user.etudiant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No student record found for this user"
        )
    
    student = await prisma.etudiant.find_unique(
        where={"id": current_user.etudiant_id},
        include={
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": {
                                "include": {
                                    "departement": True
                                }
                            }
                        }
                    }
                }
            },
            "specialite": True
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return {
        "id": student.id,
        "nom": student.nom,
        "prenom": student.prenom,
        "email": student.email,
        "groupe": {
            "id": student.groupe.id,
            "nom": student.groupe.nom,
            "niveau": {
                "id": student.groupe.niveau.id,
                "nom": student.groupe.niveau.nom,
                "specialite": {
                    "id": student.groupe.niveau.specialite.id,
                    "nom": student.groupe.niveau.specialite.nom,
                    "departement": {
                        "id": student.groupe.niveau.specialite.departement.id,
                        "nom": student.groupe.niveau.specialite.departement.nom
                    }
                }
            }
        },
        "specialite": {
            "id": student.specialite.id,
            "nom": student.specialite.nom
        }
    }