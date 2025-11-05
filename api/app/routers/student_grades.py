"""
Student Grades Viewing System
Allows students to view their own grades and averages
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from typing import Optional
from enum import Enum


router = APIRouter(prefix="/student", tags=["Student Grades"])


class SemesterType(str, Enum):
    SEMESTER_1 = "SEMESTER_1"
    SEMESTER_2 = "SEMESTER_2"


@router.get("/grades")
async def get_student_grades(
    semestre: SemesterType,
    annee_scolaire: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get all grades for the current student
    """
    # Verify user is a student
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    
    # Get student record by email (since there's no direct userId field)
    student = await prisma.etudiant.find_first(
        where={"email": current_user.email},
        include={
            "groupe": True,
            "niveau": True,
            "specialite": True
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student record not found"
        )
    
    # Get all subjects for this student's specialty
    subjects = await prisma.matiere.find_many(
        where={"id_specialite": student.id_specialite}
    )
    
    # Get subject averages
    subject_averages = await prisma.moyenne.find_many(
        where={
            "id_etudiant": student.id,
            "id_matiere": {"not": None},
            "semestre": semestre,
            "annee_scolaire": annee_scolaire
        },
        include={"matiere": True}
    )
    
    # Get general average
    general_average = await prisma.moyenne.find_first(
        where={
            "id_etudiant": student.id,
            "id_matiere": None,
            "semestre": semestre,
            "annee_scolaire": annee_scolaire
        }
    )
    
    # Build subjects with grades
    subjects_detail = []
    for subject in subjects:
        # Find average for this subject
        avg = next((a for a in subject_averages if a.id_matiere == subject.id), None)
        
        # Get all grades for this subject
        grades = await prisma.note.find_many(
            where={
                "id_etudiant": student.id,
                "id_matiere": subject.id,
                "semestre": semestre,
                "annee_scolaire": annee_scolaire
            },
            include={
                "enseignant": {
                    "include": {"utilisateur": True}
                }
            }
        )
        
        # Only include subjects that have grades
        if grades:
            subjects_detail.append({
                "matiere_id": subject.id,
                "matiere_nom": subject.nom,
                "coefficient": subject.coefficient,
                "moyenne": avg.moyenne_matiere if avg else None,
                "validee": avg.validee if avg else False,
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
            "nom": student.nom,
            "prenom": student.prenom,
            "email": student.email,
            "groupe": student.groupe.nom if student.groupe else "N/A",
            "niveau": student.niveau.nom if student.niveau else "N/A",
            "specialite": student.specialite.nom
        },
        "moyenne_generale": general_average.moyenne_generale if general_average else None,
        "rang": general_average.rang if general_average else None,
        "validee": general_average.validee if general_average else False,
        "subjects": subjects_detail,
        "semestre": semestre,
        "annee_scolaire": annee_scolaire
    }
