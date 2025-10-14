"""
Absence notifications API endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    timestamp: str
    read: bool
    data: Dict[str, Any] = {}

@router.get("/absence", response_model=Dict[str, Any])
async def get_absence_notifications(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get absence-related notifications for the current user"""
    try:
        notifications = []
        
        # For students: get their absence notifications
        if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
            # Get recent absences marked for this student
            recent_absences = await prisma.absence.find_many(
                where={
                    "id_etudiant": current_user.etudiant_id,
                    "created_at": {
                        "gte": datetime.now() - timedelta(days=30)
                    }
                },
                include={
                    "emploitemps": {
                        "include": {
                            "matiere": True,
                            "enseignant": {
                                "include": {"utilisateur": True}
                            }
                        }
                    }
                },
                order={"created_at": "desc"},
                take=20
            )
            
            for absence in recent_absences:
                # Absence marked notification
                notifications.append({
                    "id": f"absence_{absence.id}",
                    "type": "absence_marked",
                    "title": "Absence Marked",
                    "message": f"You have been marked absent for {absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else 'Unknown Subject'}",
                    "timestamp": absence.created_at.isoformat() if absence.created_at else datetime.now().isoformat(),
                    "read": False,  # In a real implementation, this would be tracked in a separate table
                    "data": {
                        "absence_id": absence.id,
                        "teacher_name": absence.emploitemps.enseignant.utilisateur.nom if absence.emploitemps.enseignant and absence.emploitemps.enseignant.utilisateur else "Unknown Teacher",
                        "subject_name": absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                        "absence_date": absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date"
                    }
                })
                
                # Status change notifications
                if absence.statut == "justified":
                    notifications.append({
                        "id": f"justified_{absence.id}",
                        "type": "justification_reviewed",
                        "title": "Justification Approved",
                        "message": f"Your absence justification for {absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else 'Unknown Subject'} has been approved",
                        "timestamp": absence.updated_at.isoformat() if absence.updated_at else datetime.now().isoformat(),
                        "read": False,
                        "data": {
                            "absence_id": absence.id,
                            "subject_name": absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                            "absence_date": absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                            "decision": "approved"
                        }
                    })
                elif absence.statut == "unjustified" and absence.motif and "justification" in absence.motif.lower():
                    notifications.append({
                        "id": f"rejected_{absence.id}",
                        "type": "justification_reviewed",
                        "title": "Justification Rejected",
                        "message": f"Your absence justification for {absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else 'Unknown Subject'} has been rejected",
                        "timestamp": absence.updated_at.isoformat() if absence.updated_at else datetime.now().isoformat(),
                        "read": False,
                        "data": {
                            "absence_id": absence.id,
                            "subject_name": absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                            "absence_date": absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                            "decision": "rejected"
                        }
                    })
            
            # Check for high absence count alerts
            total_absences = len(recent_absences)
            if total_absences >= 5:
                notifications.append({
                    "id": f"high_absences_{current_user.etudiant_id}",
                    "type": "high_absences",
                    "title": "High Absence Count Alert",
                    "message": f"You have {total_absences} absences in the last 30 days. Please contact your academic advisor.",
                    "timestamp": datetime.now().isoformat(),
                    "read": False,
                    "data": {
                        "absence_count": total_absences
                    }
                })
        
        # For teachers: get justification requests
        elif hasattr(current_user, 'enseignant_id') and current_user.enseignant_id:
            # Get recent justification requests for their classes
            justification_requests = await prisma.absence.find_many(
                where={
                    "statut": "pending_review",
                    "emploitemps": {
                        "id_enseignant": current_user.enseignant_id
                    }
                },
                include={
                    "etudiant": {
                        "include": {"utilisateur": True}
                    },
                    "emploitemps": {
                        "include": {"matiere": True}
                    }
                },
                order={"updated_at": "desc"},
                take=10
            )
            
            for absence in justification_requests:
                notifications.append({
                    "id": f"justification_{absence.id}",
                    "type": "teacher_justification",
                    "title": "Justification Submitted",
                    "message": f"{absence.etudiant.utilisateur.nom if absence.etudiant.utilisateur else 'A student'} submitted an absence justification for {absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else 'your class'}",
                    "timestamp": absence.updated_at.isoformat() if absence.updated_at else datetime.now().isoformat(),
                    "read": False,
                    "data": {
                        "absence_id": absence.id,
                        "student_name": absence.etudiant.utilisateur.nom if absence.etudiant.utilisateur else "Unknown Student",
                        "subject_name": absence.emploitemps.matiere.nom_matiere if absence.emploitemps.matiere else "Unknown Subject",
                        "absence_date": absence.emploitemps.date.strftime("%Y-%m-%d") if absence.emploitemps.date else "Unknown Date",
                        "justification_text": absence.motif or "No justification provided"
                    }
                })
        
        # Sort notifications by timestamp (newest first)
        notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "success": True,
            "notifications": notifications,
            "unread_count": len(notifications)  # In a real implementation, this would be calculated properly
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        # In a real implementation, you would update a notifications table
        # For now, we'll just return success
        return {"success": True, "message": "Notification marked as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")

@router.get("/summary")
async def get_notification_summary(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get a summary of unread notifications"""
    try:
        # Get the full notifications and count unread
        notifications_response = await get_absence_notifications(prisma, current_user)
        notifications = notifications_response.get("notifications", [])
        
        unread_count = len([n for n in notifications if not n.get("read", True)])
        
        return {
            "success": True,
            "unread_count": unread_count,
            "latest_notification": notifications[0] if notifications else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notification summary: {str(e)}")