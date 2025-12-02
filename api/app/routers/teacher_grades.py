"""
Teacher Grade Submission System
Allows teachers to enter and manage grades for their students
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_teacher
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from app.routers.notifications import create_notification


router = APIRouter(
    prefix="/teacher/grades",
    tags=["Teacher - Grade Management"]
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

class GradeSubmission(BaseModel):
    id_etudiant: str
    valeur: float = Field(..., ge=0, le=20, description="Grade value (0-20)")
    type: GradeType
    date_examen: Optional[datetime] = None
    observation: Optional[str] = None


class BulkGradeSubmission(BaseModel):
    id_matiere: str
    semestre: SemesterType
    annee_scolaire: str
    grades: List[GradeSubmission]


class SingleGradeSubmission(BaseModel):
    id_etudiant: str
    id_matiere: str
    valeur: float = Field(..., ge=0, le=20)
    type: GradeType
    semestre: SemesterType
    annee_scolaire: str
    date_examen: Optional[datetime] = None
    observation: Optional[str] = None


class GradeUpdate(BaseModel):
    valeur: Optional[float] = Field(None, ge=0, le=20)
    coefficient: Optional[float] = Field(None, ge=0.1, le=10)
    type: Optional[GradeType] = None
    date_examen: Optional[datetime] = None
    observation: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def verify_teacher_subject_access(teacher_id: str, subject_id: str, prisma: Prisma) -> bool:
    """Verify that teacher teaches this subject"""
    subject = await prisma.matiere.find_first(
        where={
            "id": subject_id,
            "id_enseignant": teacher_id
        }
    )
    return subject is not None


async def verify_student_in_subject(student_id: str, subject_id: str, prisma: Prisma) -> bool:
    """Verify that student is enrolled in a specialty that has this subject"""
    student = await prisma.etudiant.find_first(
        where={"id": student_id},
        include={"specialite": True}
    )
    
    if not student:
        return False
    
    subject = await prisma.matiere.find_first(
        where={
            "id": subject_id,
            "id_specialite": student.id_specialite
        }
    )
    
    return subject is not None


# ============================================================================
# GET TEACHER'S SUBJECTS AND CLASSES
# ============================================================================

@router.get("/my-subjects")
async def get_teacher_subjects(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all subjects taught by the current teacher from their timetable/schedule"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Get unique subjects from teacher's schedule (emploitemps)
    schedules = await prisma.emploitemps.find_many(
        where={"id_enseignant": current_user.enseignant_id},
        include={
            "matiere": {
                "include": {
                    "specialite": {
                        "include": {
                            "departement": True
                        }
                    }
                }
            }
        },
        distinct=["id_matiere"]  # Get unique subjects
    )
    
    # Extract unique subjects from schedules
    subjects_dict = {}
    for schedule in schedules:
        if schedule.matiere and schedule.matiere.id not in subjects_dict:
            subjects_dict[schedule.matiere.id] = {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom,
                "coefficient": schedule.matiere.coefficient,
                "specialite": schedule.matiere.specialite.nom if schedule.matiere.specialite else "",
                "departement": schedule.matiere.specialite.departement.nom if schedule.matiere.specialite and schedule.matiere.specialite.departement else ""
            }
    
    return {
        "subjects": list(subjects_dict.values())
    }


@router.get("/subject/{subject_id}/groups")
async def get_subject_groups(
    subject_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all groups (classes) for a specific subject from teacher's timetable"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Get subject info
    subject = await prisma.matiere.find_unique(
        where={"id": subject_id},
        include={"specialite": True}
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Get unique groups from teacher's schedule for this subject
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_enseignant": current_user.enseignant_id,
            "id_matiere": subject_id
        },
        include={
            "groupe": True
        },
        distinct=["id_groupe"]  # Get unique groups
    )
    
    # Extract unique groups and count students
    groups_with_count = []
    seen_groups = set()
    
    for schedule in schedules:
        if schedule.groupe and schedule.groupe.id not in seen_groups:
            seen_groups.add(schedule.groupe.id)
            student_count = await prisma.etudiant.count(
                where={"id_groupe": schedule.groupe.id}
            )
            groups_with_count.append({
                "id": schedule.groupe.id,
                "nom": schedule.groupe.nom,
                "student_count": student_count
            })
    
    return {
        "subject": {
            "id": subject.id,
            "nom": subject.nom,
            "coefficient": subject.coefficient
        },
        "groups": groups_with_count
    }


@router.get("/subject/{subject_id}/group/{group_id}/students")
async def get_group_students_for_grading(
    subject_id: str,
    group_id: str,
    semestre: SemesterType,
    annee_scolaire: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all students in a group with their existing grades for this subject"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Verify teacher has this subject-group combination in their schedule
    schedule_exists = await prisma.emploitemps.find_first(
        where={
            "id_enseignant": current_user.enseignant_id,
            "id_matiere": subject_id,
            "id_groupe": group_id
        }
    )
    
    if not schedule_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't teach this subject to this group"
        )
    
    # Get all students in the group
    students = await prisma.etudiant.find_many(
        where={"id_groupe": group_id},
        include={
            "utilisateur": True
        }
    )
    
    # Sort students by name in Python
    students.sort(key=lambda s: s.utilisateur.nom)
    
    # Get existing grades for each student
    students_with_grades = []
    for student in students:
        grades = await prisma.note.find_many(
            where={
                "id_etudiant": student.id,
                "id_matiere": subject_id,
                "semestre": semestre,
                "annee_scolaire": annee_scolaire
            }
        )
        
        students_with_grades.append({
            "id": student.id,
            "nom": student.utilisateur.nom,
            "prenom": student.utilisateur.prenom,
            "email": student.utilisateur.email,
            "grades": [
                {
                    "id": grade.id,
                    "valeur": grade.valeur,
                    "coefficient": grade.coefficient,
                    "type": grade.type,
                    "date_examen": grade.date_examen.isoformat() if grade.date_examen else None,
                    "observation": grade.observation,
                    "createdAt": grade.createdAt.isoformat()
                }
                for grade in grades
            ]
        })
    
    return {
        "students": students_with_grades,
        "total_students": len(students_with_grades)
    }


# ============================================================================
# SUBMIT GRADES
# ============================================================================

@router.post("/submit-single")
async def submit_single_grade(
    grade_data: SingleGradeSubmission,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher),
    background_tasks: BackgroundTasks = None
):
    """Submit a single grade for a student"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Verify teacher has this subject in their schedule
    schedule_exists = await prisma.emploitemps.find_first(
        where={
            "id_enseignant": current_user.enseignant_id,
            "id_matiere": grade_data.id_matiere
        }
    )
    
    if not schedule_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't teach this subject"
        )
    
    # Verify student is enrolled in subject's specialty
    student_enrolled = await verify_student_in_subject(
        grade_data.id_etudiant,
        grade_data.id_matiere,
        prisma
    )
    
    if not student_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is not enrolled in this subject"
        )
    
    # Get subject to retrieve its coefficient
    subject = await prisma.matiere.find_unique(
        where={"id": grade_data.id_matiere}
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Create the grade with coefficient from subject
    grade = await prisma.note.create(
        data={
            "valeur": grade_data.valeur,
            "coefficient": subject.coefficient,  # Use coefficient from subject
            "type": grade_data.type,
            "semestre": grade_data.semestre,
            "annee_scolaire": grade_data.annee_scolaire,
            "date_examen": grade_data.date_examen,
            "observation": grade_data.observation,
            "id_etudiant": grade_data.id_etudiant,
            "id_matiere": grade_data.id_matiere,
            "id_enseignant": current_user.enseignant_id
        }
    )
    
    # Notify department head(s) in background
    try:
        # Fetch subject -> specialite -> departement
        subject = await prisma.matiere.find_unique(
            where={"id": grade_data.id_matiere},
            include={"specialite": {"include": {"departement": True}}}
        )

        if subject and subject.specialite and subject.specialite.departement:
            departement_id = subject.specialite.departement.id
            # Find department head(s)
            chefs = await prisma.chefdepartement.find_many(
                where={"id_departement": departement_id},
                include={"utilisateur": True}
            )

            title = "Nouvelle note soumise"
            message = f"Une nouvelle note a été soumise pour la matière {subject.nom} (étudiant id: {grade_data.id_etudiant})."

            for chef in chefs:
                if chef and chef.utilisateur:
                    # Schedule notification creation
                    if background_tasks is not None:
                        background_tasks.add_task(
                            create_notification,
                            prisma,
                            chef.utilisateur.id,
                            "GRADE_SUBMITTED",
                            title,
                            message,
                            grade.id
                        )
                    else:
                        # fallback immediate call
                        await create_notification(
                            prisma,
                            chef.utilisateur.id,
                            "GRADE_SUBMITTED",
                            title,
                            message,
                            grade.id
                        )
    except Exception:
        # Don't block grade submission on notification failure
        pass

    return {
        "success": True,
        "grade_id": grade.id,
        "message": "Grade submitted successfully"
    }


@router.post("/submit-bulk")
async def submit_bulk_grades(
    bulk_data: BulkGradeSubmission,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher),
    background_tasks: BackgroundTasks = None
):
    """Submit multiple grades at once for a subject"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Verify teacher has this subject in their schedule
    schedule_exists = await prisma.emploitemps.find_first(
        where={
            "id_enseignant": current_user.enseignant_id,
            "id_matiere": bulk_data.id_matiere
        }
    )
    
    if not schedule_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't teach this subject"
        )
    
    # Get subject to retrieve its coefficient
    subject = await prisma.matiere.find_unique(
        where={"id": bulk_data.id_matiere}
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    created_grades = []
    errors = []
    
    for grade_submission in bulk_data.grades:
        try:
            # Verify student is enrolled
            student_enrolled = await verify_student_in_subject(
                grade_submission.id_etudiant,
                bulk_data.id_matiere,
                prisma
            )
            
            if not student_enrolled:
                errors.append({
                    "student_id": grade_submission.id_etudiant,
                    "error": "Student not enrolled in this subject"
                })
                continue
            
            # Create grade with coefficient from subject
            grade = await prisma.note.create(
                data={
                    "valeur": grade_submission.valeur,
                    "coefficient": subject.coefficient,  # Use coefficient from subject
                    "type": grade_submission.type,
                    "semestre": bulk_data.semestre,
                    "annee_scolaire": bulk_data.annee_scolaire,
                    "date_examen": grade_submission.date_examen,
                    "observation": grade_submission.observation,
                    "id_etudiant": grade_submission.id_etudiant,
                    "id_matiere": bulk_data.id_matiere,
                    "id_enseignant": current_user.enseignant_id
                }
            )
            
            created_grades.append(grade.id)
            
        except Exception as e:
            errors.append({
                "student_id": grade_submission.id_etudiant,
                "error": str(e)
            })
    
    # After bulk submission, notify department head(s) once summarizing
    try:
        # Fetch subject -> specialite -> departement
        subject = await prisma.matiere.find_unique(
            where={"id": bulk_data.id_matiere},
            include={"specialite": {"include": {"departement": True}}}
        )

        if subject and subject.specialite and subject.specialite.departement:
            departement_id = subject.specialite.departement.id
            chefs = await prisma.chefdepartement.find_many(
                where={"id_departement": departement_id},
                include={"utilisateur": True}
            )

            title = "Nouvelles notes soumises en masse"
            message = f"{len(created_grades)} notes ont été soumises pour la matière {subject.nom} (année {bulk_data.annee_scolaire}, {bulk_data.semestre})."

            for chef in chefs:
                if chef and chef.utilisateur:
                    if background_tasks is not None:
                        background_tasks.add_task(
                            create_notification,
                            prisma,
                            chef.utilisateur.id,
                            "BULK_GRADES_SUBMITTED",
                            title,
                            message,
                            ",".join(created_grades) if created_grades else None
                        )
                    else:
                        await create_notification(
                            prisma,
                            chef.utilisateur.id,
                            "BULK_GRADES_SUBMITTED",
                            title,
                            message,
                            ",".join(created_grades) if created_grades else None
                        )
    except Exception:
        pass

    return {
        "success": True,
        "created_count": len(created_grades),
        "total_submitted": len(bulk_data.grades),
        "errors": errors
    }


# ============================================================================
# UPDATE AND DELETE GRADES
# ============================================================================

@router.patch("/grade/{grade_id}")
async def update_grade(
    grade_id: str,
    update_data: GradeUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Update an existing grade"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Verify grade belongs to this teacher
    grade = await prisma.note.find_unique(
        where={"id": grade_id}
    )
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    if grade.id_enseignant != current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own grades"
        )
    
    # Build update data
    update_dict = {}
    if update_data.valeur is not None:
        update_dict["valeur"] = update_data.valeur
    if update_data.coefficient is not None:
        update_dict["coefficient"] = update_data.coefficient
    if update_data.type is not None:
        update_dict["type"] = update_data.type
    if update_data.date_examen is not None:
        update_dict["date_examen"] = update_data.date_examen
    if update_data.observation is not None:
        update_dict["observation"] = update_data.observation
    
    update_dict["updatedAt"] = datetime.now()
    
    # Update grade
    updated_grade = await prisma.note.update(
        where={"id": grade_id},
        data=update_dict
    )
    
    return {
        "success": True,
        "grade": {
            "id": updated_grade.id,
            "valeur": updated_grade.valeur,
            "coefficient": updated_grade.coefficient,
            "type": updated_grade.type
        }
    }


@router.delete("/grade/{grade_id}")
async def delete_grade(
    grade_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Delete a grade"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Verify grade belongs to this teacher
    grade = await prisma.note.find_unique(
        where={"id": grade_id}
    )
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    if grade.id_enseignant != current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own grades"
        )
    
    # Delete grade
    await prisma.note.delete(
        where={"id": grade_id}
    )
    
    return {
        "success": True,
        "message": "Grade deleted successfully"
    }


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats")
async def get_teacher_grade_stats(
    semestre: Optional[SemesterType] = Query(None),
    annee_scolaire: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get statistics about grades submitted by teacher"""
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    # Build where clause
    where_clause = {"id_enseignant": current_user.enseignant_id}
    if semestre:
        where_clause["semestre"] = semestre
    if annee_scolaire:
        where_clause["annee_scolaire"] = annee_scolaire
    
    # Count total grades
    total_grades = await prisma.note.count(where=where_clause)
    
    # Count by type
    exam_grades = await prisma.note.count(
        where={**where_clause, "type": "EXAM"}
    )
    continuous_grades = await prisma.note.count(
        where={**where_clause, "type": "CONTINUOUS"}
    )
    practical_grades = await prisma.note.count(
        where={**where_clause, "type": "PRACTICAL"}
    )
    
    # Get subjects with grade counts
    subjects = await prisma.matiere.find_many(
        where={"id_enseignant": current_user.enseignant_id},
        include={"specialite": True}
    )
    
    subjects_stats = []
    for subject in subjects:
        grade_count = await prisma.note.count(
            where={
                **where_clause,
                "id_matiere": subject.id
            }
        )
        
        subjects_stats.append({
            "subject_id": subject.id,
            "subject_name": subject.nom,
            "specialty": subject.specialite.nom,
            "grade_count": grade_count
        })
    
    return {
        "total_grades": total_grades,
        "by_type": {
            "exam": exam_grades,
            "continuous": continuous_grades,
            "practical": practical_grades
        },
        "by_subject": subjects_stats
    }
