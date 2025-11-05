"""
Student Averages Management System for Department Head
Handles grade calculations, averages, and grade reports (Relevé de Notes)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from prisma import Prisma
import prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_department_head, get_current_user
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


router = APIRouter(
    prefix="/department-head/averages",
    tags=["Department Head - Student Averages"]
)


# ============================================================================
# ENUMS
# ============================================================================

class GradeType(str, Enum):
    EXAM = "EXAM"
    CONTINUOUS = "CONTINUOUS"
    PRACTICAL = "PRACTICAL"
    PROJECT = "PROJECT"
    ORAL = "ORAL"


class SemesterType(str, Enum):
    SEMESTER_1 = "SEMESTER_1"
    SEMESTER_2 = "SEMESTER_2"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GradeInput(BaseModel):
    valeur: float = Field(..., ge=0, le=20, description="Grade value (0-20)")
    type: GradeType
    coefficient: float = Field(default=1.0, ge=0.1, le=10)
    id_etudiant: str
    id_matiere: str
    semestre: SemesterType
    annee_scolaire: str
    date_examen: Optional[datetime] = None
    observation: Optional[str] = None


class AverageResponse(BaseModel):
    id: str
    id_etudiant: str
    student_name: str
    id_matiere: Optional[str]
    matiere_nom: Optional[str]
    semestre: str
    annee_scolaire: str
    moyenne_matiere: Optional[float]
    moyenne_generale: Optional[float]
    rang: Optional[int]
    validee: bool
    observation: Optional[str]


class StudentAveragesSummary(BaseModel):
    student_id: str
    student_name: str
    student_email: str
    groupe: str
    niveau: str
    specialite: str
    moyenne_generale: Optional[float]
    rang: Optional[int]
    total_matieres: int
    matieres_validees: int
    status: str  # "excellent", "good", "average", "needs_improvement"


class GradeReportRequest(BaseModel):
    student_ids: List[str]
    semestre: SemesterType
    annee_scolaire: str
    send_notification: bool = True
    send_email: bool = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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


def calculate_subject_average(grades: List[Dict]) -> float:
    """Calculate weighted average for a subject"""
    if not grades:
        return 0.0
    
    total_weighted = sum(g['valeur'] * g['coefficient'] for g in grades)
    total_coefficients = sum(g['coefficient'] for g in grades)
    
    if total_coefficients == 0:
        return 0.0
    
    return round(total_weighted / total_coefficients, 2)


def calculate_general_average(subject_averages: List[Dict]) -> float:
    """Calculate general average from subject averages with coefficients"""
    if not subject_averages:
        return 0.0
    
    total_weighted = sum(avg['moyenne'] * avg['coefficient'] for avg in subject_averages)
    total_coefficients = sum(avg['coefficient'] for avg in subject_averages)
    
    if total_coefficients == 0:
        return 0.0
    
    return round(total_weighted / total_coefficients, 2)


def get_status_from_average(average: float) -> str:
    """Determine student status based on average"""
    if average >= 16:
        return "excellent"
    elif average >= 14:
        return "good"
    elif average >= 10:
        return "average"
    else:
        return "needs_improvement"


# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

@router.get("/dashboard")
async def get_averages_dashboard(
    semestre: Optional[SemesterType] = Query(None),
    annee_scolaire: Optional[str] = Query(None),
    groupe_id: Optional[str] = Query(None),
    specialite_id: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Get dashboard overview of student averages
    """
    department = await get_dept_head_department(current_user, prisma)
    
    # Default to current academic year if not specified
    if not annee_scolaire:
        current_year = datetime.now().year
        annee_scolaire = f"{current_year}-{current_year + 1}"
    
    # Build filter for students in department
    where_student = {
        "specialite": {
            "id_departement": department.id
        }
    }
    
    if groupe_id:
        where_student["id_groupe"] = groupe_id
    
    if specialite_id:
        where_student["id_specialite"] = specialite_id
    
    # Get all students in department
    students = await prisma.etudiant.find_many(
        where=where_student,
        include={
            "utilisateur": True,
            "groupe": True,
            "specialite": True,
            "niveau": True
        }
    )
    
    # Get averages for each student
    students_summary = []
    total_students = len(students)
    excellent_count = 0
    good_count = 0
    average_count = 0
    needs_improvement_count = 0
    
    for student in students:
        # Get general average for this student
        where_moyenne = {
            "id_etudiant": student.id,
            "id_matiere": None,  # General average
            "annee_scolaire": annee_scolaire
        }
        
        if semestre:
            where_moyenne["semestre"] = semestre
        
        # Get general average (should be unique per student/semester/year)
        moyenne_record = await prisma.moyenne.find_first(
            where=where_moyenne
        )
        
        # Count validated subject averages
        subject_averages = await prisma.moyenne.count(
            where={
                "id_etudiant": student.id,
                "id_matiere": {"not": None},
                "annee_scolaire": annee_scolaire,
                **({"semestre": semestre} if semestre else {})
            }
        )
        
        validated_averages = await prisma.moyenne.count(
            where={
                "id_etudiant": student.id,
                "id_matiere": {"not": None},
                "annee_scolaire": annee_scolaire,
                "validee": True,
                **({"semestre": semestre} if semestre else {})
            }
        )
        
        moyenne_generale = moyenne_record.moyenne_generale if moyenne_record else None
        status = get_status_from_average(moyenne_generale) if moyenne_generale else "no_grades"
        
        # Count status
        if moyenne_generale:
            if status == "excellent":
                excellent_count += 1
            elif status == "good":
                good_count += 1
            elif status == "average":
                average_count += 1
            else:
                needs_improvement_count += 1
        
        students_summary.append({
            "student_id": student.id,
            "student_name": f"{student.utilisateur.prenom} {student.utilisateur.nom}",
            "student_email": student.utilisateur.email,
            "groupe": student.groupe.nom if student.groupe else "N/A",
            "niveau": student.niveau.nom if student.niveau else "N/A",
            "specialite": student.specialite.nom,
            "moyenne_generale": moyenne_generale,
            "rang": moyenne_record.rang if moyenne_record else None,
            "total_matieres": subject_averages,
            "matieres_validees": validated_averages,
            "status": status
        })
    
    # Sort by moyenne_generale descending
    students_summary.sort(
        key=lambda x: (x['moyenne_generale'] is not None, x['moyenne_generale'] or 0),
        reverse=True
    )
    
    # Calculate statistics
    averages_list = [s['moyenne_generale'] for s in students_summary if s['moyenne_generale'] is not None]
    
    statistics = {
        "total_students": total_students,
        "students_with_grades": len(averages_list),
        "average_generale": round(sum(averages_list) / len(averages_list), 2) if averages_list else 0,
        "highest_average": max(averages_list) if averages_list else 0,
        "lowest_average": min(averages_list) if averages_list else 0,
        "excellent_count": excellent_count,
        "good_count": good_count,
        "average_count": average_count,
        "needs_improvement_count": needs_improvement_count
    }
    
    return {
        "statistics": statistics,
        "students": students_summary,
        "filters": {
            "semestre": semestre,
            "annee_scolaire": annee_scolaire,
            "groupe_id": groupe_id,
            "specialite_id": specialite_id
        }
    }


# ============================================================================
# CALCULATE AVERAGES
# ============================================================================

@router.post("/calculate")
async def calculate_averages(
    semestre: SemesterType,
    annee_scolaire: str,
    groupe_id: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Calculate or recalculate averages for students
    """
    department = await get_dept_head_department(current_user, prisma)
    
    # Determine which students to calculate
    where_student = {
        "specialite": {
            "id_departement": department.id
        }
    }
    
    if student_id:
        where_student["id"] = student_id
    elif groupe_id:
        where_student["id_groupe"] = groupe_id
    
    students = await prisma.etudiant.find_many(
        where=where_student,
        include={"utilisateur": True}
    )
    
    calculated_count = 0
    errors = []
    
    for student in students:
        try:
            # Get all subjects for this student's specialty
            subjects = await prisma.matiere.find_many(
                where={"id_specialite": student.id_specialite},
                select={"id": True, "nom": True, "coefficient": True}
            )
            
            subject_averages = []
            
            for subject in subjects:
                # Get all grades for this student in this subject
                grades = await prisma.note.find_many(
                    where={
                        "id_etudiant": student.id,
                        "id_matiere": subject['id'],
                        "semestre": semestre,
                        "annee_scolaire": annee_scolaire
                    }
                )
                
                if not grades:
                    continue
                
                # Calculate subject average
                grades_data = [
                    {"valeur": g.valeur, "coefficient": g.coefficient}
                    for g in grades
                ]
                subject_avg = calculate_subject_average(grades_data)
                
                # Store or update subject average
                await prisma.moyenne.upsert(
                    where={
                        "id_etudiant_id_matiere_semestre_annee_scolaire": {
                            "id_etudiant": student.id,
                            "id_matiere": subject['id'],
                            "semestre": semestre,
                            "annee_scolaire": annee_scolaire
                        }
                    },
                    data={
                        "create": {
                            "id_etudiant": student.id,
                            "id_matiere": subject['id'],
                            "semestre": semestre,
                            "annee_scolaire": annee_scolaire,
                            "moyenne_matiere": subject_avg
                        },
                        "update": {
                            "moyenne_matiere": subject_avg,
                            "updatedAt": datetime.now()
                        }
                    }
                )
                
                subject_averages.append({
                    "moyenne": subject_avg,
                    "coefficient": subject['coefficient']
                })
            
            # Calculate general average
            if subject_averages:
                general_avg = calculate_general_average(subject_averages)
                
                # Store or update general average
                await prisma.moyenne.upsert(
                    where={
                        "id_etudiant_id_matiere_semestre_annee_scolaire": {
                            "id_etudiant": student.id,
                            "id_matiere": None,
                            "semestre": semestre,
                            "annee_scolaire": annee_scolaire
                        }
                    },
                    data={
                        "create": {
                            "id_etudiant": student.id,
                            "id_matiere": None,
                            "semestre": semestre,
                            "annee_scolaire": annee_scolaire,
                            "moyenne_generale": general_avg
                        },
                        "update": {
                            "moyenne_generale": general_avg,
                            "updatedAt": datetime.now()
                        }
                    }
                )
                
                calculated_count += 1
        
        except Exception as e:
            errors.append({
                "student_id": student.id,
                "student_name": f"{student.utilisateur.prenom} {student.utilisateur.nom}",
                "error": str(e)
            })
    
    # Calculate ranks
    await calculate_ranks(prisma, semestre, annee_scolaire, department.id)
    
    return {
        "success": True,
        "calculated_count": calculated_count,
        "total_students": len(students),
        "errors": errors
    }


async def calculate_ranks(prisma: Prisma, semestre: SemesterType, annee_scolaire: str, department_id: str):
    """Calculate ranks for all students"""
    # Get all general averages and sort by moyenne_generale
    averages = await prisma.moyenne.find_many(
        where={
            "id_matiere": None,
            "semestre": semestre,
            "annee_scolaire": annee_scolaire,
            "etudiant": {
                "specialite": {
                    "id_departement": department_id
                }
            }
        },
        include={"etudiant": True}
    )
    
    # Sort in Python since Prisma doesn't support order_by
    averages.sort(key=lambda x: x.moyenne_generale if x.moyenne_generale else 0, reverse=True)
    
    # Assign ranks
    for rank, avg in enumerate(averages, start=1):
        await prisma.moyenne.update(
            where={"id": avg.id},
            data={"rang": rank}
        )


# ============================================================================
# STUDENT DETAILS
# ============================================================================

@router.get("/student/{student_id}")
async def get_student_averages_detail(
    student_id: str,
    semestre: SemesterType,
    annee_scolaire: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Get detailed averages breakdown for a specific student
    """
    department = await get_dept_head_department(current_user, prisma)
    
    # Verify student belongs to department
    student = await prisma.etudiant.find_first(
        where={
            "id": student_id,
            "specialite": {
                "id_departement": department.id
            }
        },
        include={
            "utilisateur": True,
            "groupe": True,
            "niveau": True,
            "specialite": True
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or not in your department"
        )
    
    # Get subject averages
    subject_averages = await prisma.moyenne.find_many(
        where={
            "id_etudiant": student_id,
            "id_matiere": {"not": None},
            "semestre": semestre,
            "annee_scolaire": annee_scolaire
        },
        include={"matiere": True}
    )
    
    # Get general average
    general_average = await prisma.moyenne.find_first(
        where={
            "id_etudiant": student_id,
            "id_matiere": None,
            "semestre": semestre,
            "annee_scolaire": annee_scolaire
        }
    )
    
    # Format subject details with grades
    subjects_detail = []
    for avg in subject_averages:
        # Get all grades for this subject
        grades = await prisma.note.find_many(
            where={
                "id_etudiant": student_id,
                "id_matiere": avg.id_matiere,
                "semestre": semestre,
                "annee_scolaire": annee_scolaire
            },
            include={"enseignant": {"include": {"utilisateur": True}}}
        )
        
        subjects_detail.append({
            "matiere_id": avg.id_matiere,
            "matiere_nom": avg.matiere.nom,
            "coefficient": avg.matiere.coefficient,
            "moyenne": avg.moyenne_matiere,
            "validee": avg.validee,
            "observation": avg.observation,
            "grades": [
                {
                    "id": g.id,
                    "valeur": g.valeur,
                    "type": g.type,
                    "coefficient": g.coefficient,
                    "date_examen": g.date_examen.isoformat() if g.date_examen else None,
                    "enseignant": f"{g.enseignant.utilisateur.prenom} {g.enseignant.utilisateur.nom}",
                    "observation": g.observation
                }
                for g in grades
            ]
        })
    
    return {
        "student": {
            "id": student.id,
            "nom": student.utilisateur.nom,
            "prenom": student.utilisateur.prenom,
            "email": student.utilisateur.email,
            "groupe": student.groupe.nom if student.groupe else "N/A",
            "niveau": student.niveau.nom if student.niveau else "N/A",
            "specialite": student.specialite.nom
        },
        "moyenne_generale": general_average.moyenne_generale if general_average else None,
        "rang": general_average.rang if general_average else None,
        "validee": general_average.validee if general_average else False,
        "observation": general_average.observation if general_average else None,
        "subjects": subjects_detail,
        "semestre": semestre,
        "annee_scolaire": annee_scolaire
    }


# ============================================================================
# VALIDATE AVERAGES
# ============================================================================

@router.patch("/validate")
async def validate_averages(
    student_ids: List[str],
    semestre: SemesterType,
    annee_scolaire: str,
    observation: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Validate student averages
    """
    department = await get_dept_head_department(current_user, prisma)
    
    validated_count = 0
    
    for student_id in student_ids:
        # Verify student belongs to department
        student = await prisma.etudiant.find_first(
            where={
                "id": student_id,
                "specialite": {
                    "id_departement": department.id
                }
            }
        )
        
        if not student:
            continue
        
        # Update all averages for this student
        await prisma.moyenne.update_many(
            where={
                "id_etudiant": student_id,
                "semestre": semestre,
                "annee_scolaire": annee_scolaire
            },
            data={
                "validee": True,
                "validee_par": current_user.id,
                "date_validation": datetime.now(),
                **({"observation": observation} if observation else {})
            }
        )
        
        validated_count += 1
    
    return {
        "success": True,
        "validated_count": validated_count
    }


# ============================================================================
# GENERATE GRADE REPORTS
# ============================================================================

@router.post("/generate-reports")
async def generate_grade_reports(
    request: GradeReportRequest,
    background_tasks: BackgroundTasks,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Generate Relevé de Notes (grade reports) for students
    """
    department = await get_dept_head_department(current_user, prisma)
    
    generated_reports = []
    errors = []
    
    for student_id in request.student_ids:
        try:
            # Verify student belongs to department
            student = await prisma.etudiant.find_first(
                where={
                    "id": student_id,
                    "specialite": {
                        "id_departement": department.id
                    }
                },
                include={"utilisateur": True}
            )
            
            if not student:
                errors.append({
                    "student_id": student_id,
                    "error": "Student not found or not in your department"
                })
                continue
            
            # Get general average
            moyenne = await prisma.moyenne.find_first(
                where={
                    "id_etudiant": student_id,
                    "id_matiere": None,
                    "semestre": request.semestre,
                    "annee_scolaire": request.annee_scolaire
                }
            )
            
            if not moyenne or not moyenne.moyenne_generale:
                errors.append({
                    "student_id": student_id,
                    "student_name": f"{student.utilisateur.prenom} {student.utilisateur.nom}",
                    "error": "No average calculated"
                })
                continue
            
            # Count total students for rank context
            total_students = await prisma.etudiant.count(
                where={
                    "specialite": {
                        "id_departement": department.id
                    }
                }
            )
            
            # Create or update grade report
            report = await prisma.relevenotes.upsert(
                where={
                    "id_etudiant_semestre_annee_scolaire": {
                        "id_etudiant": student_id,
                        "semestre": request.semestre,
                        "annee_scolaire": request.annee_scolaire
                    }
                },
                data={
                    "create": {
                        "id_etudiant": student_id,
                        "semestre": request.semestre,
                        "annee_scolaire": request.annee_scolaire,
                        "moyenne_generale": moyenne.moyenne_generale,
                        "rang": moyenne.rang,
                        "total_etudiants": total_students,
                        "appreciation": get_appreciation(moyenne.moyenne_generale),
                        "genere_par": current_user.id,
                        "envoye": False
                    },
                    "update": {
                        "moyenne_generale": moyenne.moyenne_generale,
                        "rang": moyenne.rang,
                        "total_etudiants": total_students,
                        "appreciation": get_appreciation(moyenne.moyenne_generale),
                        "genere_par": current_user.id,
                        "date_generation": datetime.now()
                    }
                }
            )
            
            generated_reports.append({
                "report_id": report.id,
                "student_id": student_id,
                "student_name": f"{student.utilisateur.prenom} {student.utilisateur.nom}",
                "moyenne": moyenne.moyenne_generale,
                "rang": moyenne.rang
            })
            
            # Send notification if requested
            if request.send_notification:
                background_tasks.add_task(
                    send_report_notification,
                    prisma,
                    student.utilisateur.id,
                    report.id,
                    request.semestre,
                    request.annee_scolaire
                )
        
        except Exception as e:
            errors.append({
                "student_id": student_id,
                "error": str(e)
            })
    
    return {
        "success": True,
        "generated_count": len(generated_reports),
        "reports": generated_reports,
        "errors": errors
    }


def get_appreciation(moyenne: float) -> str:
    """Get appreciation text based on average"""
    if moyenne >= 16:
        return "Très bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"


async def send_report_notification(
    prisma: Prisma,
    user_id: str,
    report_id: str,
    semestre: SemesterType,
    annee_scolaire: str
):
    """Send notification to student about grade report"""
    from app.routers.notifications import create_notification
    
    await create_notification(
        prisma=prisma,
        user_id=user_id,
        notification_type="GRADE_REPORT_AVAILABLE",
        title="Relevé de Notes Disponible",
        message=f"Votre relevé de notes pour le {semestre} ({annee_scolaire}) est maintenant disponible.",
        related_id=report_id
    )
