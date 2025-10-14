"""
Notification System API
Handles notifications for schedule changes and absence marking
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from prisma import Prisma
from datetime import datetime
from pydantic import BaseModel

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

# Pydantic Models
class NotificationResponse(BaseModel):
    id: str
    userId: str
    type: str
    title: str
    message: str
    relatedId: Optional[str]
    isRead: bool
    createdAt: datetime

    class Config:
        from_attributes = True

class NotificationStats(BaseModel):
    total: int
    unread: int

# Helper Functions
async def create_notification(
    prisma: Prisma,
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    related_id: Optional[str] = None
):
    """
    Create a notification for a user
    """
    try:
        notification = await prisma.notification.create(
            data={
                "userId": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "relatedId": related_id,
                "isRead": False
            }
        )
        print(f"âœ… Notification created: {notification_type} for user {user_id}")
        return notification
    except Exception as e:
        print(f"âŒ Failed to create notification: {e}")
        return None

async def notify_schedule_change(
    prisma: Prisma,
    teacher_user_id: str,
    action: str,  # "created", "updated", "deleted"
    schedule_data: dict
):
    """
    Notify teacher when chef de dÃ©partement creates/updates/deletes their schedule
    """
    action_titles = {
        "created": "Nouvel emploi du temps",
        "updated": "Emploi du temps modifiÃ©",
        "deleted": "Emploi du temps supprimÃ©"
    }
    
    title = action_titles.get(action, "Modification d'emploi du temps")
    
    message = f"MatiÃ¨re: {schedule_data.get('matiere')}\n"
    message += f"Jour: {schedule_data.get('jour')}\n"
    message += f"Heure: {schedule_data.get('heure_debut')} - {schedule_data.get('heure_fin')}\n"
    message += f"Salle: {schedule_data.get('salle')}"
    
    notification_type = f"SCHEDULE_{action.upper()}"
    
    await create_notification(
        prisma=prisma,
        user_id=teacher_user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        related_id=schedule_data.get('schedule_id')
    )

async def notify_absence_marked(
    prisma: Prisma,
    student_user_id: str,
    absence_data: dict
):
    """
    Notify student when teacher marks them absent
    """
    title = "Absence enregistrÃ©e"
    
    message = f"Vous avez Ã©tÃ© marquÃ©(e) absent(e)\n"
    message += f"MatiÃ¨re: {absence_data.get('matiere')}\n"
    message += f"Date: {absence_data.get('date')}\n"
    message += f"Heure: {absence_data.get('heure')}"
    
    await create_notification(
        prisma=prisma,
        user_id=student_user_id,
        notification_type="ABSENCE_MARKED",
        title=title,
        message=message,
        related_id=absence_data.get('absence_id')
    )

# API Endpoints
@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all notifications for current user"""
    where_clause = {"userId": current_user.id}
    
    if unread_only:
        where_clause["isRead"] = False
    
    notifications = await prisma.notification.find_many(
        where=where_clause,
        order={"createdAt": "desc"}
    )
    
    return notifications

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get notification statistics"""
    total = await prisma.notification.count(
        where={"userId": current_user.id}
    )
    
    unread = await prisma.notification.count(
        where={
            "userId": current_user.id,
            "isRead": False
        }
    )
    
    return {
        "total": total,
        "unread": unread
    }

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = await prisma.notification.find_first(
        where={
            "id": notification_id,
            "userId": current_user.id
        }
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    updated = await prisma.notification.update(
        where={"id": notification_id},
        data={"isRead": True}
    )
    
    return {"message": "Notification marked as read"}

@router.patch("/mark-all-read")
async def mark_all_as_read(
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark all notifications as read"""
    count = await prisma.notification.update_many(
        where={
            "userId": current_user.id,
            "isRead": False
        },
        data={"isRead": True}
    )
    
    return {"message": f"Marked {count} notifications as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a notification"""
    notification = await prisma.notification.find_first(
        where={
            "id": notification_id,
            "userId": current_user.id
        }
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await prisma.notification.delete(
        where={"id": notification_id}
    )
    
    return {"message": "Notification deleted"}

@router.delete("/")
async def delete_all_notifications(
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete all notifications for current user"""
    count = await prisma.notification.delete_many(
        where={"userId": current_user.id}
    )
    
    return {"message": f"Deleted {count} notifications"}
