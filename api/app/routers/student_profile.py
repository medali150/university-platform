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
    
    if not hasattr(current_user, 'etudiant_id') or not current_user.etudiant_id:
        # Try to find student record by email
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
            include={"groupe": True}
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student record found for this user"
            )
        
        # Update user with student link
        try:
            await prisma.utilisateur.update(
                where={"id": current_user.id},
                data={"etudiant_id": student.id}
            )
            current_user.etudiant_id = student.id
        except:
            pass
    else:
        # Get student record
        student = await prisma.etudiant.find_unique(
            where={"id": current_user.etudiant_id},
            include={"groupe": True}
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
    
    # Only query absences if there are schedules
    absences = []
    if schedule_ids:
        absences = await prisma.absence.find_many(
            where={
                "id_etudiant": student.id,
                "id_emploitemps": {"in": schedule_ids}
            }
        )    # Create absence map for quick lookup
    absence_map = {absence.id_emploitemps: absence for absence in absences}
    
    # Calculate the Monday of the current week for date references
    if isinstance(start_dt, date):
        target_monday = start_dt - timedelta(days=start_dt.weekday())
    else:
        target_monday = start_dt.date() - timedelta(days=start_dt.weekday())
    
    target_sunday = target_monday + timedelta(days=6)
    
    # Calculate week offset (0 = current week)
    today = date.today()
    today_monday = today - timedelta(days=today.weekday())
    week_offset = (target_monday - today_monday).days // 7
    
    # Define standard university time slots (like your example)
    time_slots = [
        {"id": "slot1", "start": "08:30", "end": "10:00", "label": "8h30 à 10h00"},
        {"id": "slot2", "start": "10:10", "end": "11:40", "label": "10h10 à 11h40"},
        {"id": "slot3", "start": "11:50", "end": "13:20", "label": "11h50 à 13h20"},
        {"id": "slot4", "start": "14:30", "end": "16:00", "label": "14h30 à 16h00"},
        {"id": "slot5", "start": "16:10", "end": "17:40", "label": "16h10 à 17h40"}
    ]
    
    # Days of the week
    days = [
        {"id": "monday", "name": "Lundi", "date": target_monday},
        {"id": "tuesday", "name": "Mardi", "date": target_monday + timedelta(days=1)},
        {"id": "wednesday", "name": "Mercredi", "date": target_monday + timedelta(days=2)},
        {"id": "thursday", "name": "Jeudi", "date": target_monday + timedelta(days=3)},
        {"id": "friday", "name": "Vendredi", "date": target_monday + timedelta(days=4)},
        {"id": "saturday", "name": "Samedi", "date": target_monday + timedelta(days=5)}
    ]
    
    # Create timetable structure organized by day (for frontend compatibility)
    timetable_by_day = {
        "lundi": [],
        "mardi": [],
        "mercredi": [],
        "jeudi": [],
        "vendredi": [],
        "samedi": []
    }
    
    # Fill timetable with schedule data
    for schedule in schedules:
        if not schedule.heure_debut or not schedule.date:
            continue
            
        # Get day of week (0=Monday, 1=Tuesday, etc.)
        schedule_date = schedule.date.date() if hasattr(schedule.date, 'date') else schedule.date
        day_of_week = schedule_date.weekday()
        
        if day_of_week > 5:  # Skip Sunday
            continue
            
        day_name_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"][day_of_week]
        
        # Get time
        schedule_start_time = schedule.heure_debut.time() if hasattr(schedule.heure_debut, 'time') else schedule.heure_debut
        schedule_end_time = schedule.heure_fin.time() if hasattr(schedule.heure_fin, 'time') else schedule.heure_fin
        start_time_str = schedule_start_time.strftime("%H:%M")
        end_time_str = schedule_end_time.strftime("%H:%M")
        
        # Get absence status
        absence = absence_map.get(schedule.id)
        
        # Create course info
        course_info = {
            "id": schedule.id,
            "subject": schedule.matiere.nom if schedule.matiere else "Matière inconnue",
            "teacher": f"{schedule.enseignant.prenom} {schedule.enseignant.nom}" if schedule.enseignant else "Enseignant inconnu",
            "room": schedule.salle.code if schedule.salle else "Salle inconnue",
            "start_time": start_time_str,
            "end_time": end_time_str,
            "absence": {
                "is_absent": bool(absence),
                "status": absence.statut if absence else None,
                "reason": absence.motif if absence else None
            } if absence else None,
            "status": getattr(schedule, 'status', 'PLANNED')
        }
        
        timetable_by_day[day_name_fr].append(course_info)

    return {
        "timetable": timetable_by_day,
        "week_start": target_monday.strftime("%d/%m/%Y"),
        "week_end": target_sunday.strftime("%d/%m/%Y"),
        "student_info": {
            "id": student.id,
            "name": f"{student.prenom} {student.nom}",
            "email": student.email,
            "group": {
                "id": student.groupe.id if student.groupe else student.id_groupe,
                "name": student.groupe.nom if student.groupe else "Groupe inconnu"
            }
        },
        "total_courses": len(schedules),
        "note": "Emploi du temps récurrent pour le semestre"
    }

@router.get("/schedule/today")
async def get_student_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student's schedule for today"""
    
    if not hasattr(current_user, 'etudiant_id') or not current_user.etudiant_id:
        # Try to find student record by email
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
            include={"groupe": True}
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student record found for this user"
            )
        
        # Update user with student link
        try:
            await prisma.utilisateur.update(
                where={"id": current_user.id},
                data={"etudiant_id": student.id}
            )
            current_user.etudiant_id = student.id
        except:
            pass
    else:
        # Get student record
        student = await prisma.etudiant.find_unique(
            where={"id": current_user.etudiant_id},
            include={"groupe": True}
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
    
    # Only query absences if there are schedules
    absences = []
    if schedule_ids:
        absences = await prisma.absence.find_many(
            where={
                "id_etudiant": student.id,
                "id_emploitemps": {"in": schedule_ids}
            }
        )
    
    absence_map = {absence.id_emploitemps: absence for absence in absences}
    
    # Format today's schedules safely
    formatted_schedules = []
    for schedule in schedules:
        absence = absence_map.get(schedule.id)
        
        formatted_schedule = {
            "id": schedule.id,
            "date": schedule.date.isoformat() if schedule.date else None,
            "heure_debut": schedule.heure_debut.isoformat() if schedule.heure_debut else None,
            "heure_fin": schedule.heure_fin.isoformat() if schedule.heure_fin else None,
            "status": getattr(schedule, 'status', None),
            "matiere": {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            } if schedule.matiere else None,
            "enseignant": {
                "id": schedule.enseignant.id,
                "nom": schedule.enseignant.nom,
                "prenom": schedule.enseignant.prenom
            } if schedule.enseignant else None,
            "salle": {
                "id": schedule.salle.id,
                "code": schedule.salle.code,
                "type": schedule.salle.type
            } if schedule.salle else None,
            "absence": {
                "id": absence.id if absence else None,
                "status": absence.statut if absence else None,
                "motif": absence.motif if absence else None,
                "is_absent": bool(absence)
            } if absence else None
        }
        formatted_schedules.append(formatted_schedule)
    
    return formatted_schedules


@router.get("/profile")
async def get_student_profile(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student profile information"""
    
    if not hasattr(current_user, 'etudiant_id') or not current_user.etudiant_id:
        # Try to find student record by email
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
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
                detail="No student record found for this user"
            )
        
        # Update user with student link for future requests
        try:
            await prisma.utilisateur.update(
                where={"id": current_user.id},
                data={"etudiant_id": student.id}
            )
            current_user.etudiant_id = student.id
        except:
            pass  # Continue even if update fails
        
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
    
    # If we reach here, etudiant_id is set
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


@router.get("/debug")
async def debug_student_data(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Debug endpoint to check student data"""
    
    try:
        # Find student record
        student = None
        if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
            student = await prisma.etudiant.find_unique(
                where={"id": current_user.etudiant_id}
            )
        
        if not student:
            # Try to find by email
            student = await prisma.etudiant.find_first(
                where={"email": current_user.email}
            )
        
        if not student:
            return {
                "error": "No student record found",
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "role": current_user.role,
                    "has_etudiant_id": hasattr(current_user, 'etudiant_id'),
                    "etudiant_id": getattr(current_user, 'etudiant_id', None)
                }
            }
        
        # Check if student has a group
        group_info = None
        if student.id_groupe:
            try:
                group = await prisma.groupe.find_unique(
                    where={"id": student.id_groupe}
                )
                if group:
                    group_info = {"id": group.id, "nom": group.nom}
            except Exception as e:
                group_info = {"error": str(e)}
        
        return {
            "success": True,
            "student": {
                "id": student.id,
                "nom": student.nom,
                "prenom": student.prenom,
                "email": student.email,
                "id_groupe": student.id_groupe,
                "id_specialite": student.id_specialite
            },
            "group": group_info,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role,
                "etudiant_id": getattr(current_user, 'etudiant_id', None)
            }
        }
    
    except Exception as e:
        return {
            "error": f"Debug failed: {str(e)}",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            }
        }


@router.get("/schedule/test")
async def test_schedule_query(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Test schedule query step by step to find the issue"""
    
    try:
        # Find student record
        student = None
        if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
            student = await prisma.etudiant.find_unique(
                where={"id": current_user.etudiant_id},
                include={"groupe": True}
            )
        
        if not student:
            student = await prisma.etudiant.find_first(
                where={"email": current_user.email},
                include={"groupe": True}
            )
        
        if not student:
            return {"error": "No student record found"}
        
        # Test 1: Check if we can query emploitemps table at all
        try:
            emploitemps_count = await prisma.emploitemps.count()
            result = {"step_1_emploitemps_count": emploitemps_count}
        except Exception as e:
            return {"error": f"Step 1 failed - can't access emploitemps table: {str(e)}"}
        
        # Test 2: Try to find any emploitemps for this group
        try:
            group_schedules_count = await prisma.emploitemps.count(
                where={"id_groupe": student.id_groupe}
            )
            result["step_2_group_schedules_count"] = group_schedules_count
        except Exception as e:
            return {"error": f"Step 2 failed - can't query by group: {str(e)}"}
        
        # Test 3: Try simple query without includes
        try:
            simple_schedules = await prisma.emploitemps.find_many(
                where={"id_groupe": student.id_groupe},
                take=1
            )
            result["step_3_simple_query"] = len(simple_schedules)
            if simple_schedules:
                schedule = simple_schedules[0]
                result["step_3_sample"] = {
                    "id": schedule.id,
                    "date": str(schedule.date) if schedule.date else None,
                    "id_matiere": getattr(schedule, 'id_matiere', None),
                    "id_enseignant": getattr(schedule, 'id_enseignant', None),
                    "id_salle": getattr(schedule, 'id_salle', None)
                }
        except Exception as e:
            return {"error": f"Step 3 failed - simple query: {str(e)}"}
        
        # Test 4: Try query with includes
        try:
            include_schedules = await prisma.emploitemps.find_many(
                where={"id_groupe": student.id_groupe},
                include={
                    "matiere": True,
                    "enseignant": True,
                    "salle": True
                },
                take=1
            )
            result["step_4_with_includes"] = len(include_schedules)
        except Exception as e:
            return {"error": f"Step 4 failed - includes: {str(e)}"}
        
        return {
            "success": True,
            "student_id": student.id,
            "group_id": student.id_groupe,
            "tests": result
        }
    
    except Exception as e:
        return {"error": f"Overall test failed: {str(e)}"}


@router.post("/admin/create-sample-schedule")
async def create_sample_schedule_for_group(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)  # Temporary - any user can test
):
    """Create sample schedule entries for the student's group (ADMIN ONLY - TEMPORARY)"""
    
    try:
        # Get student's group
        student = None
        if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
            student = await prisma.etudiant.find_unique(
                where={"id": current_user.etudiant_id},
                include={"groupe": True}
            )
        
        if not student:
            student = await prisma.etudiant.find_first(
                where={"email": current_user.email},
                include={"groupe": True}
            )
        
        if not student:
            return {"error": "Student record not found"}
        
        group_id = student.id_groupe
        group_name = student.groupe.nom if student.groupe else "Unknown Group"
        
        # Get available resources
        subjects = await prisma.matiere.find_many(take=3)
        teachers = await prisma.enseignant.find_many(take=3)
        rooms = await prisma.salle.find_many(take=3)
        
        if not subjects or not teachers or not rooms:
            return {"error": "Missing required resources (subjects, teachers, or rooms)"}
        
        # Create sample schedule for next week
        from datetime import datetime, timedelta, date
        
        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        # Sample schedule template
        schedule_template = [
            {"day": 0, "start_hour": 8, "start_min": 0, "duration": 2, "subject_idx": 0, "teacher_idx": 0, "room_idx": 0},
            {"day": 0, "start_hour": 10, "start_min": 30, "duration": 2, "subject_idx": 1, "teacher_idx": 1, "room_idx": 1},
            {"day": 1, "start_hour": 8, "start_min": 0, "duration": 2, "subject_idx": 2, "teacher_idx": 2, "room_idx": 0},
            {"day": 1, "start_hour": 14, "start_min": 0, "duration": 2, "subject_idx": 0, "teacher_idx": 0, "room_idx": 2},
            {"day": 2, "start_hour": 10, "start_min": 30, "duration": 2, "subject_idx": 1, "teacher_idx": 1, "room_idx": 1},
        ]
        
        created_schedules = []
        
        for schedule_info in schedule_template:
            try:
                # Calculate date and times
                schedule_date = next_monday + timedelta(days=schedule_info["day"])
                start_time = datetime.combine(schedule_date, datetime.min.time())
                start_time = start_time.replace(hour=schedule_info["start_hour"], minute=schedule_info["start_min"])
                end_time = start_time + timedelta(hours=schedule_info["duration"])
                
                # Select resources
                subject = subjects[schedule_info["subject_idx"] % len(subjects)]
                teacher = teachers[schedule_info["teacher_idx"] % len(teachers)]
                room = rooms[schedule_info["room_idx"] % len(rooms)]
                
                # Create schedule entry
                new_schedule = await prisma.emploitemps.create(
                    data={
                        "date": start_time,
                        "heure_debut": start_time,
                        "heure_fin": end_time,
                        "id_salle": room.id,
                        "id_matiere": subject.id,
                        "id_groupe": group_id,
                        "id_enseignant": teacher.id,
                        "status": "PLANNED"
                    }
                )
                
                created_schedules.append({
                    "id": new_schedule.id,
                    "date": schedule_date.strftime("%Y-%m-%d"),
                    "time": f"{schedule_info['start_hour']:02d}:{schedule_info['start_min']:02d}-{end_time.hour:02d}:{end_time.minute:02d}",
                    "subject": subject.nom,
                    "teacher": f"{teacher.prenom} {teacher.nom}",
                    "room": room.code
                })
                
            except Exception as e:
                print(f"Failed to create schedule entry: {e}")
        
        return {
            "success": True,
            "message": f"Created {len(created_schedules)} schedule entries for group: {group_name}",
            "group_id": group_id,
            "group_name": group_name,
            "schedules_created": created_schedules
        }
        
    except Exception as e:
        return {"error": f"Failed to create sample schedules: {str(e)}"}


@router.get("/timetable")
async def get_student_timetable(
    week_offset: Optional[int] = 0,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student's weekly timetable in university table format (like your example)"""
    
    try:
        # Find student record
        student = None
        if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
            student = await prisma.etudiant.find_unique(
                where={"id": current_user.etudiant_id},
                include={"groupe": True}
            )
        
        if not student:
            student = await prisma.etudiant.find_first(
                where={"email": current_user.email},
                include={"groupe": True}
            )
        
        if not student:
            return {"error": "Student record not found"}
        
        # Calculate the target week
        today = date.today()
        monday_of_current_week = today - timedelta(days=today.weekday())
        target_monday = monday_of_current_week + timedelta(weeks=week_offset)
        target_sunday = target_monday + timedelta(days=6)
        
        # Get schedules for the week
        start_datetime = datetime.combine(target_monday, datetime.min.time())
        end_datetime = datetime.combine(target_sunday, datetime.max.time())
        
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
                "salle": True
            },
            order=[{"date": "asc"}, {"heure_debut": "asc"}]
        )
        
        # Define standard time slots (based on your university example)
        time_slots = [
            {"id": "slot1", "start": "08:30", "end": "10:00", "label": "8h30 à 10h00"},
            {"id": "slot2", "start": "10:10", "end": "11:40", "label": "10h10 à 11h40"},
            {"id": "slot3", "start": "11:50", "end": "13:20", "label": "11h50 à 13h20"},
            {"id": "slot4", "start": "14:30", "end": "16:00", "label": "14h30 à 16h00"},
            {"id": "slot5", "start": "16:10", "end": "17:40", "label": "16h10 à 17h40"}
        ]
        
        # Days of the week
        days = [
            {"id": "lundi", "name": "Lundi", "date": target_monday},
            {"id": "mardi", "name": "Mardi", "date": target_monday + timedelta(days=1)},
            {"id": "mercredi", "name": "Mercredi", "date": target_monday + timedelta(days=2)},
            {"id": "jeudi", "name": "Jeudi", "date": target_monday + timedelta(days=3)},
            {"id": "vendredi", "name": "Vendredi", "date": target_monday + timedelta(days=4)},
            {"id": "samedi", "name": "Samedi", "date": target_monday + timedelta(days=5)}
        ]
        
        # Initialize timetable structure
        timetable = {}
        for slot in time_slots:
            timetable[slot["id"]] = {
                "time_info": slot,
                "courses": {}
            }
            for day in days:
                timetable[slot["id"]]["courses"][day["id"]] = None
        
        # Fill timetable with actual schedule data
        for schedule in schedules:
            if not schedule.heure_debut or not schedule.date:
                continue
                
            # Get day of week
            schedule_date = schedule.date.date() if hasattr(schedule.date, 'date') else schedule.date
            day_of_week = schedule_date.weekday()  # 0=Monday, 1=Tuesday, etc.
            
            if day_of_week > 5:  # Skip Sunday
                continue
                
            day_keys = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
            day_key = day_keys[day_of_week]
            
            # Get schedule time
            start_time = schedule.heure_debut.time() if hasattr(schedule.heure_debut, 'time') else schedule.heure_debut
            end_time = schedule.heure_fin.time() if hasattr(schedule.heure_fin, 'time') else schedule.heure_fin
            
            # Find matching time slot
            matching_slot = None
            for slot in time_slots:
                slot_start = datetime.strptime(slot["start"], "%H:%M").time()
                slot_end = datetime.strptime(slot["end"], "%H:%M").time()
                
                # Check if schedule overlaps with this time slot
                if (slot_start <= start_time < slot_end) or (slot_start < end_time <= slot_end):
                    matching_slot = slot["id"]
                    break
            
            if matching_slot:
                # Create course entry (like your university example)
                course_entry = {
                    "subject": schedule.matiere.nom if schedule.matiere else "Matière inconnue",
                    "teacher": f"{schedule.enseignant.prenom} {schedule.enseignant.nom}" if schedule.enseignant else "Enseignant inconnu",
                    "room": schedule.salle.code if schedule.salle else "TI 11",  # Default room format
                    "time": {
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M") if end_time else None
                    },
                    "schedule_id": schedule.id
                }
                
                timetable[matching_slot]["courses"][day_key] = course_entry
        
        return {
            "success": True,
            "timetable": timetable,
            "time_slots": time_slots,
            "days": days,
            "week_info": {
                "start_date": target_monday.strftime("%Y-%m-%d"),
                "end_date": target_sunday.strftime("%Y-%m-%d"),
                "week_offset": week_offset,
                "is_current_week": week_offset == 0
            },
            "student_info": {
                "name": f"{student.prenom} {student.nom}",
                "group": student.groupe.nom if student.groupe else "Groupe inconnu",
                "group_id": student.id_groupe
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get timetable: {str(e)}"}


@router.post("/admin/create-university-schedule")
async def create_university_schedule_template(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)  # Temporary - for testing
):
    """Create a realistic university schedule template (like your example)"""
    
    try:
        # Get student's group
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email},
            include={"groupe": True}
        )
        
        if not student:
            return {"error": "Student record not found"}
        
        group_id = student.id_groupe
        
        # Get available resources
        subjects = await prisma.matiere.find_many()
        teachers = await prisma.enseignant.find_many()
        rooms = await prisma.salle.find_many()
        
        if not subjects or not teachers or not rooms:
            return {"error": "Missing resources - need subjects, teachers, and rooms"}
        
        # Create subjects map (try to match realistic university subjects)
        subject_map = {}
        for subject in subjects:
            name_lower = subject.nom.lower()
            if "algo" in name_lower or "program" in name_lower:
                subject_map["programming"] = subject
            elif "math" in name_lower:
                subject_map["math"] = subject
            elif "arch" in name_lower or "system" in name_lower:
                subject_map["architecture"] = subject
            elif "english" in name_lower or "anglais" in name_lower:
                subject_map["english"] = subject
            elif "express" in name_lower or "technique" in name_lower:
                subject_map["expression"] = subject
            elif "logic" in name_lower:
                subject_map["logic"] = subject
            elif "business" in name_lower or "culture" in name_lower:
                subject_map["business"] = subject
        
        # If we don't have enough specific subjects, use available ones
        available_subjects = list(subjects)
        
        # Define university timetable template (based on your example)
        timetable_template = [
            # Monday
            {"day": 0, "slot": "08:30-10:00", "subject_key": "programming", "teacher_idx": 0, "room": "TI 12"},
            {"day": 0, "slot": "10:10-11:40", "subject_key": "english", "teacher_idx": 1, "room": "DSI 23"},
            {"day": 0, "slot": "11:50-13:20", "subject_key": "english", "teacher_idx": 1, "room": "DSI 31"},
            {"day": 0, "slot": "14:30-16:00", "subject_key": "expression", "teacher_idx": 2, "room": "TI 12"},
            
            # Tuesday  
            {"day": 1, "slot": "08:30-10:00", "subject_key": "programming", "teacher_idx": 0, "room": "TI 11"},
            {"day": 1, "slot": "10:10-11:40", "subject_key": "math", "teacher_idx": 3, "room": "TI 11"},
            {"day": 1, "slot": "11:50-13:20", "subject_key": "math", "teacher_idx": 3, "room": "TI 11"},
            {"day": 1, "slot": "14:30-16:00", "subject_key": "english", "teacher_idx": 1, "room": "TI 11"},
            
            # Wednesday
            {"day": 2, "slot": "08:30-10:00", "subject_key": "architecture", "teacher_idx": 4, "room": "TI 11"},
            {"day": 2, "slot": "10:10-11:40", "subject_key": "logic", "teacher_idx": 5, "room": "TI 11"},
            {"day": 2, "slot": "11:50-13:20", "subject_key": "business", "teacher_idx": 6, "room": "TI 11"},
            {"day": 2, "slot": "14:30-16:00", "subject_key": "math", "teacher_idx": 3, "room": "TI 12"},
            
            # Thursday
            {"day": 3, "slot": "08:30-10:00", "subject_key": "programming", "teacher_idx": 0, "room": "TI 11"},
            {"day": 3, "slot": "10:10-11:40", "subject_key": "expression", "teacher_idx": 2, "room": "TI 11"},
            {"day": 3, "slot": "11:50-13:20", "subject_key": "logic", "teacher_idx": 5, "room": "TI 6"},
            
            # Friday
            {"day": 4, "slot": "08:30-10:00", "subject_key": "english", "teacher_idx": 1, "room": "RSI 21"},
        ]
        
        # Calculate next Monday for schedule creation
        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        created_schedules = []
        
        for template_entry in timetable_template:
            try:
                # Parse time slot
                time_slot = template_entry["slot"]
                start_time_str, end_time_str = time_slot.split("-")
                
                # Create datetime objects
                schedule_date = next_monday + timedelta(days=template_entry["day"])
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
                
                start_datetime = datetime.combine(schedule_date, start_time)
                end_datetime = datetime.combine(schedule_date, end_time)
                
                # Select subject
                subject_key = template_entry["subject_key"]
                subject = subject_map.get(subject_key, available_subjects[0])
                
                # Select teacher
                teacher_idx = template_entry["teacher_idx"] % len(teachers)
                teacher = teachers[teacher_idx]
                
                # Get or create room
                room_code = template_entry["room"]
                room = None
                for r in rooms:
                    if r.code == room_code:
                        room = r
                        break
                
                if not room:
                    # Try to find existing room first
                    existing_room = await prisma.salle.find_first(
                        where={"code": room_code}
                    )
                    
                    if existing_room:
                        room = existing_room
                    else:
                        # Create room if it doesn't exist
                        try:
                            room = await prisma.salle.create(
                                data={
                                    "code": room_code,
                                    "type": "LECTURE",
                                    "capacite": 30
                                }
                            )
                        except Exception as room_error:
                            # If creation fails due to unique constraint, try to find it again
                            room = await prisma.salle.find_first(
                                where={"code": room_code}
                            )
                            if not room:
                                raise room_error
                
                # Check if schedule already exists for this time slot and group
                existing_schedule = await prisma.emploitemps.find_first(
                    where={
                        "id_groupe": group_id,
                        "date": start_datetime,
                        "heure_debut": start_datetime,
                        "heure_fin": end_datetime
                    }
                )
                
                if existing_schedule:
                    # Update existing schedule instead of creating new one
                    schedule = await prisma.emploitemps.update(
                        where={"id": existing_schedule.id},
                        data={
                            "id_salle": room.id,
                            "id_matiere": subject.id,
                            "id_enseignant": teacher.id,
                            "status": "PLANNED"
                        }
                    )
                else:
                    # Create new schedule entry
                    schedule = await prisma.emploitemps.create(
                        data={
                            "date": start_datetime,
                            "heure_debut": start_datetime,
                            "heure_fin": end_datetime,
                            "id_salle": room.id,
                            "id_matiere": subject.id,
                            "id_groupe": group_id,
                            "id_enseignant": teacher.id,
                            "status": "PLANNED"
                        }
                    )
                
                created_schedules.append({
                    "day": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][template_entry["day"]],
                    "time": time_slot,
                    "subject": subject.nom,
                    "teacher": f"{teacher.prenom} {teacher.nom}",
                    "room": room_code
                })
                
            except Exception as e:
                print(f"Failed to create schedule entry: {e}")
        
        return {
            "success": True,
            "message": f"Created university timetable with {len(created_schedules)} courses",
            "group_id": group_id,
            "group_name": student.groupe.nom if student.groupe else "Unknown",
            "schedules_created": created_schedules,
            "week_start": next_monday.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        return {"error": f"Failed to create university schedule: {str(e)}"}