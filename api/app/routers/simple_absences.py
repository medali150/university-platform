"""
Simple absences endpoint for the frontend
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from app.services.enhanced_notification_service import AbsenceNotificationService

router = APIRouter(prefix="/simple-absences", tags=["Simple Absences"])

@router.get("/all")
async def get_all_absences(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all absences with complete data structure"""
    try:
        absences = await prisma.absence.find_many(
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
                        "groupe": True,
                        "salle": True
                    }
                }
            },
            order={"createdAt": "desc"}
        )
        
        # Transform the data to match frontend interface
        transformed_absences = []
        for absence in absences:
            student_user = absence.etudiant.utilisateur
            teacher_user = absence.emploitemps.enseignant.utilisateur
            
            transformed_absence = {
                "id": absence.id,
                "student": {
                    "nom": student_user.nom,
                    "prenom": student_user.prenom,
                    "email": student_user.email
                },
                "subject": {
                    "nom": absence.emploitemps.matiere.nom
                },
                "teacher": {
                    "nom": teacher_user.nom,
                    "prenom": teacher_user.prenom
                },
                "emploitemps": {
                    "date": absence.emploitemps.date.isoformat() if absence.emploitemps.date else None,
                    "heure_debut": absence.emploitemps.heure_debut.strftime("%H:%M:%S") if absence.emploitemps.heure_debut else None,
                    "heure_fin": absence.emploitemps.heure_fin.strftime("%H:%M:%S") if absence.emploitemps.heure_fin else None,
                    "groupe": {
                        "nom": absence.emploitemps.groupe.nom if absence.emploitemps.groupe else "N/A"
                    }
                },
                "motif": absence.motif or "Non spécifié",
                "statut": absence.statut,
                "justification_text": absence.justification_text,
                "createdAt": absence.createdAt.isoformat() if absence.createdAt else None,
                "updatedAt": absence.updatedAt.isoformat() if absence.updatedAt else None
            }
            transformed_absences.append(transformed_absence)
        
        return transformed_absences
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching absences: {str(e)}")

@router.put("/{absence_id}/status")
async def update_absence_status(
    absence_id: str,
    status_data: dict,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Update absence status"""
    try:
        # Note: AbsenceNotificationService uses static methods
        
        # Check if absence exists and get full data
        absence = await prisma.absence.find_unique(
            where={"id": absence_id},
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
            }
        )
        if not absence:
            raise HTTPException(status_code=404, detail="Absence not found")
        
        old_status = absence.statut
        new_status = status_data.get("status")
        
        # Update the status
        updated_absence = await prisma.absence.update(
            where={"id": absence_id},
            data={"statut": new_status}
        )
        
        # Send appropriate notifications based on status change
        try:
            if new_status == "justified" and old_status in ["unjustified", "pending_review"]:
                # Notify student that their justification was accepted
                await AbsenceNotificationService.notify_student_justification_reviewed(
                    student_email=absence.etudiant.utilisateur.email if absence.etudiant.utilisateur else "unknown@example.com",
                    student_name=f"{absence.etudiant.utilisateur.prenom} {absence.etudiant.utilisateur.nom}" if absence.etudiant.utilisateur else "Unknown Student",
                    subject_name=absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                    absence_date=absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                    review_status="approved",
                    reviewer_name=f"{current_user.prenom} {current_user.nom}" if current_user.prenom and current_user.nom else "Administrator",
                    review_comment="Justification accepted"
                )
            elif new_status == "unjustified" and old_status == "pending_review":
                # Notify student that their justification was rejected
                await AbsenceNotificationService.notify_student_justification_reviewed(
                    student_email=absence.etudiant.utilisateur.email if absence.etudiant.utilisateur else "unknown@example.com",
                    student_name=f"{absence.etudiant.utilisateur.prenom} {absence.etudiant.utilisateur.nom}" if absence.etudiant.utilisateur else "Unknown Student",
                    subject_name=absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                    absence_date=absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                    review_status="rejected",
                    reviewer_name=f"{current_user.prenom} {current_user.nom}" if current_user.prenom and current_user.nom else "Administrator",
                    review_comment="Justification not accepted"
                )
            elif new_status == "pending_review" and old_status == "unjustified":
                # Notify teacher that student submitted justification
                if absence.emploitemps.enseignant:
                    await AbsenceNotificationService.notify_teacher_absence_justified(
                        teacher_email=absence.emploitemps.enseignant.utilisateur.email if absence.emploitemps.enseignant.utilisateur else "unknown@example.com",
                        teacher_name=f"{absence.emploitemps.enseignant.utilisateur.prenom} {absence.emploitemps.enseignant.utilisateur.nom}" if absence.emploitemps.enseignant.utilisateur else "Unknown Teacher",
                        student_name=f"{absence.etudiant.utilisateur.prenom} {absence.etudiant.utilisateur.nom}" if absence.etudiant.utilisateur else "Unknown Student",
                        subject_name=absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                        absence_date=absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                        justification_text=absence.motif or "No justification provided",
                        absence_id=absence_id
                    )
        except Exception as e:
            # Log the error but don't fail the status update
            print(f"Failed to send status update notification: {e}")
        
        return {"success": True, "message": "Status updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")