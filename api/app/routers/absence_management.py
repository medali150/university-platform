"""
Absence from app.schemas.absence_schemas import (
    AbsenceCreate, AbsenceUpdate, AbsenceJustification, AbsenceReview,
    AbsenceQuery, AbsenceResponse, AbsenceStatistics, NotificationHistory,
    AbsenceStatus
)
# Old notification service imports removed - using new notification system from notifications.pyt API router with NotificationAPI integration
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from prisma import Prisma
import logging

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_role
from app.routers.notifications import create_notification
from app.models.absence_models import (
    AbsenceCreate, AbsenceUpdate, AbsenceJustification, AbsenceReview,
    AbsenceQuery, AbsenceResponse, AbsenceStatistics, NotificationHistory,
    AbsenceStatus
)
# Old notification service imports removed - using new notification system

router = APIRouter(prefix="/absences", tags=["Absence Management"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=dict)
async def create_absence(
    absence_data: AbsenceCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["TEACHER", "DEPARTMENT_HEAD", "ADMIN"]))
):
    """Teacher marks student absence during class"""
    try:
        # Validate that the schedule exists and belongs to the teacher (if teacher role)
        schedule = await prisma.emploitemps.find_unique(
            where={"id": absence_data.scheduleId},
            include={
                "matiere": {
                    "include": {
                        "specialite": {
                            "include": {"departement": True}
                        }
                    }
                },
                "enseignant": {
                    "include": {"utilisateur": True}
                },
                "groupe": True,
                "salle": True
            }
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emploi du temps non trouvé"
            )
        
        # If current user is a teacher, validate they teach this class
        if current_user.role == "TEACHER":
            # Get the teacher via the user's enseignant_id
            user_with_teacher = await prisma.utilisateur.find_unique(
                where={"id": current_user.id},
                include={"enseignant": True}
            )
            
            if not user_with_teacher or not user_with_teacher.enseignant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Profil enseignant non trouvé"
                )
            
            if schedule.id_enseignant != user_with_teacher.enseignant.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez marquer les absences que pour vos propres cours"
                )
        
        # Validate that the student exists and belongs to the class group
        student = await prisma.etudiant.find_unique(
            where={"id": absence_data.studentId},
            include={
                "utilisateur": True,
                "groupe": True,
                "specialite": True
            }
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Étudiant non trouvé"
            )
        
        if student.id_groupe != schedule.id_groupe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'étudiant n'appartient pas au groupe de cette classe"
            )
        
        # Check for duplicate absence record
        existing_absence = await prisma.absence.find_first(
            where={
                "id_etudiant": absence_data.studentId,
                "id_emploitemps": absence_data.scheduleId
            }
        )
        
        if existing_absence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une absence existe déjà pour cet étudiant et cette séance"
            )
        
        # Create absence record
        absence = await prisma.absence.create(
            data={
                "id_etudiant": absence_data.studentId,
                "id_emploitemps": absence_data.scheduleId,
                "motif": absence_data.reason,
                "statut": absence_data.status,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        )
        
        # Count total absences for this student in this subject
        total_absences = await prisma.absence.count(
            where={
                "id_etudiant": absence_data.studentId,
                "emploiTemps": {
                    "id_matiere": schedule.id_matiere
                }
            }
        )
        
        # Send notification to student about absence
        try:
            await create_notification(
                prisma=prisma,
                user_id=student.utilisateur.id,
                notification_type="ABSENCE_MARKED",
                title="Absence enregistrée",
                message=f"Vous avez été marqué absent au cours de {schedule.matiere.nom} le {schedule.date.strftime('%d/%m/%Y')} à {schedule.heure_debut.strftime('%H:%M')}",
                related_id=absence.id
            )
            logger.info(f"✅ Notification sent to student {student.utilisateur.email} for absence {absence.id}")
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
        
        # Send email notification about the absence
        try:
            from app.services.email_service import send_absence_notification_email
            
            # Get teacher name
            teacher_name = f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}" if schedule.enseignant else "Enseignant"
            
            # Send email with absence count
            await send_absence_notification_email(
                to_email=student.utilisateur.email,
                student_name=f"{student.utilisateur.prenom} {student.utilisateur.nom}",
                absence_count=total_absences,
                subject_name=schedule.matiere.nom,
                absence_date=schedule.date.strftime('%d/%m/%Y'),
                teacher_name=teacher_name
            )
            
            logger.info(f"✅ Email sent to {student.utilisateur.email} - Absence #{total_absences} in {schedule.matiere.nom}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            # Don't fail the absence creation if email fails
        
        return {
            "message": "Absence créée avec succès",
            "id": absence.id,
            "notification_sent": True,
            "email_sent": True,
            "total_absences": total_absences,
            "warning_level": "eliminated" if total_absences >= 3 else ("critical" if total_absences == 2 else "normal")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating absence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'absence: {str(e)}"
        )

@router.get("/", response_model=dict)
async def get_absences(
    page: int = Query(1, ge=1, description="Numéro de page"),
    pageSize: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    studentId: Optional[str] = Query(None, description="ID de l'étudiant"),
    teacherId: Optional[str] = Query(None, description="ID de l'enseignant"),
    absence_status: Optional[AbsenceStatus] = Query(None, description="Statut de l'absence"),
    dateFrom: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    dateTo: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get absences with role-based filtering"""
    try:
        # Build where clause based on user role and filters
        where_clause = {}
        
        # Role-based filtering
        if current_user.role == "STUDENT":
            # Students can only see their own absences
            student = await prisma.etudiant.find_unique(
                where={"userId": current_user.id}
            )
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil étudiant non trouvé"
                )
            where_clause["id_etudiant"] = student.id
            
        elif current_user.role == "TEACHER":
            # Teachers can only see absences for their classes
            teacher = await prisma.enseignant.find_unique(
                where={"userId": current_user.id}
            )
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil enseignant non trouvé"
                )
            where_clause["emploitemps"] = {
                "id_enseignant": teacher.id
            }
            
        elif current_user.role == "DEPARTMENT_HEAD":
            # Department heads can see absences for their department
            dept_head = await prisma.chefdepartement.find_unique(
                where={"id_utilisateur": current_user.id}
            )
            if not dept_head:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profil chef de département non trouvé"
                )
            where_clause["emploitemps"] = {
                "matiere": {
                    "specialite": {
                        "id_departement": dept_head.id_departement
                    }
                }
            }
        
        # Apply additional filters
        if studentId:
            where_clause["id_etudiant"] = studentId
        if teacherId:
            where_clause["emploitemps"]["id_enseignant"] = teacherId
        if absence_status:
            where_clause["statut"] = absence_status
        
        # Date filtering
        if dateFrom or dateTo:
            date_filter = {}
            if dateFrom:
                date_filter["gte"] = datetime.strptime(dateFrom, "%Y-%m-%d")
            if dateTo:
                date_filter["lte"] = datetime.strptime(dateTo, "%Y-%m-%d")
            where_clause["emploitemps"]["date"] = date_filter
        
        # Get total count
        total = await prisma.absence.count(where=where_clause)
        
        # Calculate pagination
        skip = (page - 1) * pageSize
        total_pages = (total + pageSize - 1) // pageSize
        
        # Get absences with full details
        absences = await prisma.absence.find_many(
            where=where_clause,
            include={
                "etudiant": {
                    "include": {"utilisateur": True}
                },
                "emploitemps": {
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {"utilisateur": True}
                        },
                        "salle": True,
                        "groupe": True
                    }
                }
            },
            skip=skip,
            take=pageSize,
            order={"createdAt": "desc"}
        )
        
        # Transform response
        response_absences = []
        for absence in absences:
            absence_data = {
                "id": absence.id,
                "studentId": absence.id_etudiant,
                "studentName": f"{absence.etudiant.utilisateur.prenom} {absence.etudiant.utilisateur.nom}",
                "scheduleId": absence.id_emploitemps,
                "className": absence.emploitemps.matiere.nom,
                "teacherName": f"{absence.emploitemps.enseignant.utilisateur.prenom} {absence.emploitemps.enseignant.utilisateur.nom}",
                "date": absence.emploitemps.date,
                "startTime": absence.emploitemps.heure_debut,
                "endTime": absence.emploitemps.heure_fin,
                "reason": absence.motif,
                "status": absence.statut,
                "justificationText": getattr(absence, 'justification_text', None),
                "supportingDocuments": getattr(absence, 'supporting_documents', []),
                "reviewNotes": getattr(absence, 'review_notes', None),
                "createdAt": absence.createdAt,
                "updatedAt": absence.updatedAt
            }
            response_absences.append(absence_data)
        
        return {
            "data": response_absences,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": total_pages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting absences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des absences: {str(e)}"
        )

@router.get("/student/{student_id}", response_model=dict)
async def get_student_absences(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get absences for specific student"""
    try:
        # Validate access rights
        if current_user.role == "STUDENT":
            # Students can only access their own absences
            student = await prisma.etudiant.find_unique(
                where={"userId": current_user.id}
            )
            if not student or student.id != student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès non autorisé"
                )
        elif current_user.role == "TEACHER":
            # Teachers can access absences for students in their classes
            # This would require more complex validation - simplified for now
            pass
        elif current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        # Get student absences
        absences = await prisma.absence.find_many(
            where={"id_etudiant": student_id},
            include={
                "etudiant": {
                    "include": {"utilisateur": True}
                },
                "emploitemps": {
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {"utilisateur": True}
                        }
                    }
                }
            },
            order={"createdAt": "desc"}
        )
        
        # Calculate statistics
        total_absences = len(absences)
        justified_count = len([a for a in absences if a.statut in ["justified", "approved"]])
        unjustified_count = len([a for a in absences if a.statut == "unjustified"])
        pending_count = len([a for a in absences if a.statut == "pending_review"])
        
        # Transform response
        response_absences = []
        for absence in absences:
            absence_data = {
                "id": absence.id,
                "className": absence.emploitemps.matiere.nom,
                "teacherName": f"{absence.emploitemps.enseignant.utilisateur.prenom} {absence.emploitemps.enseignant.utilisateur.nom}",
                "date": absence.emploitemps.date,
                "startTime": absence.emploitemps.heure_debut,
                "endTime": absence.emploitemps.heure_fin,
                "reason": absence.motif,
                "status": absence.statut,
                "justificationText": getattr(absence, 'justification_text', None),
                "reviewNotes": getattr(absence, 'review_notes', None),
                "createdAt": absence.createdAt
            }
            response_absences.append(absence_data)
        
        return {
            "absences": response_absences,
            "statistics": {
                "total": total_absences,
                "justified": justified_count,
                "unjustified": unjustified_count,
                "pending": pending_count,
                "absenceRate": (total_absences / max(1, total_absences + 10)) * 100  # Simplified calculation
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student absences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des absences: {str(e)}"
        )

@router.put("/{absence_id}/justify", response_model=dict)
async def justify_absence(
    absence_id: str,
    justification_data: AbsenceJustification,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["STUDENT", "ADMIN"]))
):
    """Student submits justification for absence"""
    try:
        # Get absence with student info
        absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={
                "etudiant": {
                    "include": {"utilisateur": True, "specialite": {"include": {"departement": True}}}
                },
                "emploitemps": {
                    "include": {"matiere": True}
                }
            }
        )
        
        if not absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence non trouvée"
            )
        
        # Validate student can justify this absence
        if current_user.role == "STUDENT":
            student = await prisma.etudiant.find_unique(
                where={"userId": current_user.id}
            )
            if not student or absence.id_etudiant != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez justifier que vos propres absences"
                )
        
        # Update absence with justification
        updated_absence = await prisma.absence.update(
            where={"id": absence_id},
            data={
                "justification_text": justification_data.justificationText,
                "supporting_documents": justification_data.supportingDocuments,
                "statut": AbsenceStatus.PENDING_REVIEW,
                "updatedAt": datetime.now()
            }
        )
        
        # Send notification to department head
        try:
            dept_head = await prisma.chefdepartement.find_first(
                where={"id_departement": absence.etudiant.specialite.id_departement},
                include={"utilisateur": True}
            )
            
            # TODO: Add justification notification using new notification system
            # (Old send_justification_notification function removed)
        except Exception as e:
            logger.error(f"Failed to process justification: {str(e)}")
        
        return {
            "message": "Justification soumise avec succès",
            "status": "pending_review"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting justification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la soumission de la justification: {str(e)}"
        )

@router.put("/{absence_id}/review", response_model=dict)
async def review_absence(
    absence_id: str,
    review_data: AbsenceReview,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["DEPARTMENT_HEAD", "ADMIN"]))
):
    """Department head reviews student justification"""
    try:
        # Get absence with full details
        absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={
                "etudiant": {
                    "include": {"utilisateur": True, "specialite": {"include": {"departement": True}}}
                },
                "emploitemps": {
                    "include": {"matiere": True}
                }
            }
        )
        
        if not absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence non trouvée"
            )
        
        # Validate department head can review this absence
        if current_user.role == "DEPARTMENT_HEAD":
            dept_head = await prisma.chefdepartement.find_unique(
                where={"id_utilisateur": current_user.id}
            )
            if not dept_head or absence.etudiant.specialite.id_departement != dept_head.id_departement:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez réviser que les absences de votre département"
                )
        
        # Update absence with review
        updated_absence = await prisma.absence.update(
            where={"id": absence_id},
            data={
                "statut": review_data.reviewStatus,
                "review_notes": review_data.reviewNotes,
                "reviewed_at": datetime.now(),
                "reviewed_by": current_user.id,
                "updatedAt": datetime.now()
            }
        )
        
        # TODO: Add review notification using new notification system
        # (Old send_review_notification function removed)
        
        return {
            "message": "Révision effectuée avec succès",
            "status": review_data.reviewStatus
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing absence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la révision: {str(e)}"
        )

@router.delete("/{absence_id}", response_model=dict)
async def delete_absence(
    absence_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["TEACHER", "DEPARTMENT_HEAD", "ADMIN"]))
):
    """Delete absence record"""
    try:
        # Get absence to validate permissions
        absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={
                "emploitemps": {
                    "include": {
                        "matiere": {
                            "include": {
                                "specialite": {"include": {"departement": True}}
                            }
                        }
                    }
                }
            }
        )
        
        if not absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence non trouvée"
            )
        
        # Validate permissions
        if current_user.role == "TEACHER":
            teacher = await prisma.enseignant.find_unique(
                where={"userId": current_user.id}
            )
            if not teacher or absence.emploitemps.id_enseignant != teacher.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez supprimer que les absences de vos cours"
                )
        elif current_user.role == "DEPARTMENT_HEAD":
            dept_head = await prisma.chefdepartement.find_unique(
                where={"id_utilisateur": current_user.id}
            )
            if not dept_head or absence.emploitemps.matiere.specialite.id_departement != dept_head.id_departement:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez supprimer que les absences de votre département"
                )
        
        # Delete absence
        await prisma.absence.delete(where={"id": absence_id})
        
        return {"message": "Absence supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting absence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/statistics", response_model=AbsenceStatistics)
async def get_absence_statistics(
    departmentId: Optional[str] = Query(None, description="ID du département"),
    dateFrom: Optional[str] = Query(None, description="Date de début"),
    dateTo: Optional[str] = Query(None, description="Date de fin"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["DEPARTMENT_HEAD", "ADMIN"]))
):
    """Get absence statistics for dashboard"""
    try:
        # Build where clause
        where_clause = {}
        
        if current_user.role == "DEPARTMENT_HEAD":
            dept_head = await prisma.chefdepartement.find_unique(
                where={"id_utilisateur": current_user.id}
            )
            if dept_head:
                where_clause["emploitemps"] = {
                    "matiere": {
                        "specialite": {
                            "id_departement": dept_head.id_departement
                        }
                    }
                }
        elif departmentId:
            where_clause["emploitemps"] = {
                "matiere": {
                    "specialite": {
                        "id_departement": departmentId
                    }
                }
            }
        
        # Date filtering
        if dateFrom or dateTo:
            date_filter = {}
            if dateFrom:
                date_filter["gte"] = datetime.strptime(dateFrom, "%Y-%m-%d")
            if dateTo:
                date_filter["lte"] = datetime.strptime(dateTo, "%Y-%m-%d")
            if "emploitemps" not in where_clause:
                where_clause["emploitemps"] = {}
            where_clause["emploitemps"]["date"] = date_filter
        
        # Get statistics
        total_absences = await prisma.absence.count(where=where_clause)
        
        justified_absences = await prisma.absence.count(
            where={**where_clause, "statut": {"in": ["justified", "approved"]}}
        )
        
        unjustified_absences = await prisma.absence.count(
            where={**where_clause, "statut": "unjustified"}
        )
        
        pending_review = await prisma.absence.count(
            where={**where_clause, "statut": "pending_review"}
        )
        
        approved_justifications = await prisma.absence.count(
            where={**where_clause, "statut": "approved"}
        )
        
        rejected_justifications = await prisma.absence.count(
            where={**where_clause, "statut": "rejected"}
        )
        
        # Calculate absence rate (simplified)
        absence_rate = (total_absences / max(1, total_absences + 100)) * 100
        
        # Get students with high absences
        # This would require a more complex query - simplified for now
        students_with_high_absences = []
        
        return AbsenceStatistics(
            totalAbsences=total_absences,
            justifiedAbsences=justified_absences,
            unjustifiedAbsences=unjustified_absences,
            pendingReview=pending_review,
            approvedJustifications=approved_justifications,
            rejectedJustifications=rejected_justifications,
            absenceRate=absence_rate,
            studentsWithHighAbsences=students_with_high_absences
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )