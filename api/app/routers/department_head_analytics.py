"""
Department Head Analytics System
Provides comprehensive analytics and statistics for department heads
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_department_head
from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import io
import csv


router = APIRouter(
    prefix="/department-head/analytics",
    tags=["Department Head - Analytics"]
)


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


@router.get("/overview")
async def get_analytics_overview(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Get comprehensive analytics overview for department head
    """
    department = await get_dept_head_department(current_user, prisma)
    
    # Parse dates
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
    else:
        # Default to last 3 months
        start_dt = datetime.now(timezone.utc) - timedelta(days=90)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    else:
        end_dt = datetime.now(timezone.utc)
    
    # Get all students in department
    students = await prisma.etudiant.find_many(
        where={
            "specialite": {
                "id_departement": department.id
            }
        }
    )
    student_ids = [s.id for s in students]
    
    # Get all teachers in department
    teachers = await prisma.enseignant.find_many(
        where={"id_departement": department.id},
        include={"utilisateur": True}
    )
    
    # Get all schedules in date range
    schedules = await prisma.emploitemps.find_many(
        where={
            "date": {
                "gte": start_dt,
                "lte": end_dt
            },
            "enseignant": {
                "id_departement": department.id
            }
        },
        include={
            "matiere": True,
            "enseignant": {"include": {"utilisateur": True}},
            "salle": True,
            "groupe": True
        }
    )
    
    # Get absences
    absences = await prisma.absence.find_many(
        where={
            "id_etudiant": {"in": student_ids},
            "createdAt": {
                "gte": start_dt,
                "lte": end_dt
            }
        }
    )
    
    # Get grades
    grades = await prisma.note.find_many(
        where={
            "id_etudiant": {"in": student_ids},
            "createdAt": {
                "gte": start_dt,
                "lte": end_dt
            }
        },
        include={"matiere": True}
    )
    
    # Calculate KPIs
    total_schedules = len(schedules)
    total_hours = sum([
        (schedule.heure_fin - schedule.heure_debut).total_seconds() / 3600
        for schedule in schedules
    ])
    
    # Attendance rate
    total_absences = len(absences)
    justified_absences = len([a for a in absences if a.statut == "JUSTIFIED"])
    total_possible_attendances = total_schedules * len(student_ids) if total_schedules > 0 else 1
    attendance_rate = ((total_possible_attendances - total_absences) / total_possible_attendances * 100) if total_possible_attendances > 0 else 0
    
    # Room utilization
    rooms_usage = {}
    for schedule in schedules:
        room_id = schedule.id_salle
        if room_id not in rooms_usage:
            rooms_usage[room_id] = {
                "room": schedule.salle,
                "hours": 0
            }
        duration = (schedule.heure_fin - schedule.heure_debut).total_seconds() / 3600
        rooms_usage[room_id]["hours"] += duration
    
    # Average room utilization (assuming 8 hours per day, 5 days per week)
    days_in_period = (end_dt - start_dt).days
    total_available_hours = days_in_period * 8 * len(rooms_usage) if len(rooms_usage) > 0 else 1
    total_used_hours = sum([r["hours"] for r in rooms_usage.values()])
    room_utilization_rate = (total_used_hours / total_available_hours * 100) if total_available_hours > 0 else 0
    
    # Subject distribution
    subject_hours = {}
    for schedule in schedules:
        subject_name = schedule.matiere.nom
        duration = (schedule.heure_fin - schedule.heure_debut).total_seconds() / 3600
        if subject_name not in subject_hours:
            subject_hours[subject_name] = 0
        subject_hours[subject_name] += duration
    
    # Sort subjects by hours
    sorted_subjects = sorted(subject_hours.items(), key=lambda x: x[1], reverse=True)
    subject_distribution = [
        {
            "subject": subject,
            "hours": round(hours, 1),
            "percentage": round((hours / total_hours * 100) if total_hours > 0 else 0, 1)
        }
        for subject, hours in sorted_subjects[:10]  # Top 10 subjects
    ]
    
    # Teacher performance
    teacher_stats = {}
    for schedule in schedules:
        teacher_id = schedule.id_enseignant
        if teacher_id not in teacher_stats:
            teacher_stats[teacher_id] = {
                "teacher": schedule.enseignant,
                "total_hours": 0,
                "sessions": 0
            }
        duration = (schedule.heure_fin - schedule.heure_debut).total_seconds() / 3600
        teacher_stats[teacher_id]["total_hours"] += duration
        teacher_stats[teacher_id]["sessions"] += 1
    
    # Sort teachers by hours
    sorted_teachers = sorted(teacher_stats.values(), key=lambda x: x["total_hours"], reverse=True)
    top_teachers = [
        {
            "id": t["teacher"].id,
            "name": f"{t['teacher'].utilisateur.prenom} {t['teacher'].utilisateur.nom}",
            "total_hours": round(t["total_hours"], 1),
            "sessions": t["sessions"]
        }
        for t in sorted_teachers[:5]  # Top 5 teachers
    ]
    
    # Room efficiency
    room_efficiency = []
    for room_id, data in rooms_usage.items():
        room_available_hours = days_in_period * 8  # 8 hours per day
        utilization = (data["hours"] / room_available_hours * 100) if room_available_hours > 0 else 0
        room_efficiency.append({
            "room_code": data["room"].code,
            "room_name": data["room"].code,
            "hours_used": round(data["hours"], 1),
            "utilization_rate": round(utilization, 1)
        })
    
    # Sort by utilization
    room_efficiency.sort(key=lambda x: x["utilization_rate"], reverse=True)
    
    # Weekly attendance trend (last 12 weeks)
    weekly_attendance = []
    for week in range(12):
        week_start = end_dt - timedelta(weeks=12-week)
        week_end = week_start + timedelta(days=7)
        
        week_absences = [a for a in absences if week_start <= a.createdAt <= week_end]
        week_schedules = [s for s in schedules if week_start <= s.date <= week_end]
        
        week_possible = len(week_schedules) * len(student_ids) if len(week_schedules) > 0 else 1
        week_rate = ((week_possible - len(week_absences)) / week_possible * 100) if week_possible > 0 else 0
        
        weekly_attendance.append({
            "week": f"S{week + 1}",
            "rate": round(week_rate, 1),
            "date": week_start.strftime("%Y-%m-%d")
        })
    
    # Grade statistics
    average_grade = sum([g.valeur for g in grades]) / len(grades) if grades else 0
    excellent_grades = len([g for g in grades if g.valeur >= 16])
    good_grades = len([g for g in grades if 14 <= g.valeur < 16])
    average_grades = len([g for g in grades if 10 <= g.valeur < 14])
    poor_grades = len([g for g in grades if g.valeur < 10])
    
    return {
        "period": {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "days": days_in_period
        },
        "kpis": {
            "attendance_rate": round(attendance_rate, 1),
            "room_utilization_rate": round(room_utilization_rate, 1),
            "total_schedules": total_schedules,
            "total_hours": round(total_hours, 1),
            "total_students": len(student_ids),
            "total_teachers": len(teachers),
            "total_absences": total_absences,
            "justified_absences": justified_absences
        },
        "subject_distribution": subject_distribution,
        "top_teachers": top_teachers,
        "room_efficiency": room_efficiency[:5],  # Top 5 rooms
        "weekly_attendance": weekly_attendance,
        "grade_statistics": {
            "average_grade": round(average_grade, 2),
            "total_grades": len(grades),
            "excellent": excellent_grades,
            "good": good_grades,
            "average": average_grades,
            "poor": poor_grades
        },
        "department": {
            "id": department.id,
            "name": department.nom
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Get recent activity in the department
    """
    department = await get_dept_head_department(current_user, prisma)
    
    # Get recent absences
    recent_absences = await prisma.absence.find_many(
        where={
            "etudiant": {
                "specialite": {
                    "id_departement": department.id
                }
            }
        },
        include={
            "etudiant": True,
            "emploitemps": {
                "include": {"matiere": True}
            }
        },
        take=limit
    )
    
    # Sort in Python since Prisma doesn't support order parameter
    recent_absences.sort(key=lambda x: x.createdAt if x.createdAt else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    # Get recent grades
    recent_grades = await prisma.note.find_many(
        where={
            "etudiant": {
                "specialite": {
                    "id_departement": department.id
                }
            }
        },
        include={
            "etudiant": True,
            "matiere": True,
            "enseignant": True
        },
        take=limit
    )
    
    # Sort in Python since Prisma doesn't support order parameter
    recent_grades.sort(key=lambda x: x.createdAt if x.createdAt else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    # Combine and format activities
    activities = []
    
    for absence in recent_absences:
        activities.append({
            "type": "absence",
            "timestamp": absence.createdAt.isoformat(),
            "student": f"{absence.etudiant.prenom} {absence.etudiant.nom}",
            "subject": absence.emploitemps.matiere.nom if absence.emploitemps else "N/A",
            "status": absence.statut,
            "severity": "warning" if absence.statut == "PENDING" else ("success" if absence.statut == "JUSTIFIED" else "error")
        })
    
    for grade in recent_grades:
        severity = "success" if grade.valeur >= 14 else ("warning" if grade.valeur >= 10 else "error")
        teacher_name = "N/A"
        if grade.enseignant:
            teacher_name = f"{grade.enseignant.prenom} {grade.enseignant.nom}"
        
        activities.append({
            "type": "grade",
            "timestamp": grade.createdAt.isoformat(),
            "student": f"{grade.etudiant.prenom} {grade.etudiant.nom}",
            "subject": grade.matiere.nom,
            "grade": grade.valeur,
            "teacher": teacher_name,
            "severity": severity
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "activities": activities[:limit]
    }


@router.get("/export")
async def export_analytics_report(
    format: str = Query("csv", regex="^(csv|excel)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Export analytics report as CSV or Excel
    """
    # Get analytics data
    overview = await get_analytics_overview(start_date, end_date, prisma, current_user)
    
    if format == "csv":
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([f"Rapport d'Analyse - {overview['department']['name']}"])
        writer.writerow([f"Période: {overview['period']['start_date']} à {overview['period']['end_date']}"])
        writer.writerow([])
        
        # KPIs
        writer.writerow(["Indicateurs Clés de Performance (KPI)"])
        writer.writerow(["Métrique", "Valeur"])
        kpis = overview['kpis']
        writer.writerow(["Taux de présence", f"{kpis['attendance_rate']:.1f}%"])
        writer.writerow(["Utilisation des salles", f"{kpis['room_utilization_rate']:.1f}%"])
        writer.writerow(["Total d'emplois du temps", kpis['total_schedules']])
        writer.writerow(["Total d'heures", kpis['total_hours']])
        writer.writerow(["Total d'étudiants", kpis['total_students']])
        writer.writerow(["Total d'enseignants", kpis['total_teachers']])
        writer.writerow(["Total d'absences", kpis['total_absences']])
        writer.writerow(["Absences justifiées", kpis['justified_absences']])
        writer.writerow([])
        
        # Subject distribution
        writer.writerow(["Distribution par Matière"])
        writer.writerow(["Matière", "Heures", "Pourcentage"])
        for subject in overview['subject_distribution']:
            writer.writerow([subject['subject'], subject['hours'], f"{subject['percentage']:.1f}%"])
        writer.writerow([])
        
        # Top teachers
        writer.writerow(["Enseignants les Plus Actifs"])
        writer.writerow(["Nom", "Total d'Heures", "Nombre de Sessions"])
        for teacher in overview['top_teachers']:
            writer.writerow([teacher['name'], teacher['total_hours'], teacher['sessions']])
        writer.writerow([])
        
        # Room efficiency
        writer.writerow(["Efficacité des Salles"])
        writer.writerow(["Code Salle", "Heures Utilisées", "Taux d'Utilisation"])
        for room in overview['room_efficiency']:
            writer.writerow([room['room_code'], room['hours_used'], f"{room['utilization_rate']:.1f}%"])
        writer.writerow([])
        
        # Grade statistics
        if 'grade_statistics' in overview and overview['grade_statistics']:
            writer.writerow(["Statistiques des Notes"])
            writer.writerow(["Métrique", "Valeur"])
            grades = overview['grade_statistics']
            writer.writerow(["Moyenne générale", f"{grades['average_grade']:.2f}"])
            writer.writerow(["Total de notes", grades['total_grades']])
            writer.writerow(["Excellent (≥16)", grades['excellent']])
            writer.writerow(["Bien (14-16)", grades['good']])
            writer.writerow(["Moyen (12-14)", grades['average']])
            writer.writerow(["Insuffisant (<12)", grades['poor']])
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Return as download
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8-sig')),  # utf-8-sig for Excel compatibility
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_report_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    # For Excel format, we'd need openpyxl or xlsxwriter
    # For now, return CSV with .xlsx extension
    return await export_analytics_report("csv", start_date, end_date, prisma, current_user)
