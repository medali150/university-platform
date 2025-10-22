"""
Messaging System API Router
Enables communication between teachers and students
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/messages", tags=["Messages"])


# ===========================
# REQUEST/RESPONSE MODELS
# ===========================

class MessageCreate(BaseModel):
    """Request to send a new message"""
    id_destinataire: str
    contenu: str
    
    class Config:
        schema_extra = {
            "example": {
                "id_destinataire": "cm123abc",
                "contenu": "Bonjour, j'aimerais discuter de mon absence..."
            }
        }


class UserInfo(BaseModel):
    """User information for message display"""
    id: str
    nom: str
    prenom: str
    email: str
    role: str


class MessageResponse(BaseModel):
    """Message response with full sender/receiver info"""
    id: str
    id_expediteur: str
    id_destinataire: str
    contenu: str
    createdAt: str
    expediteur: UserInfo
    destinataire: UserInfo


class ConversationResponse(BaseModel):
    """Conversation summary"""
    userId: str
    user: UserInfo
    lastMessage: dict
    unreadCount: int


# ===========================
# HELPER FUNCTIONS
# ===========================

def format_user_info(user) -> dict:
    """Format user data for API response"""
    return {
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "email": user.email,
        "role": user.role
    }


def format_message_response(message) -> dict:
    """Format message for API response"""
    return {
        "id": message.id,
        "id_expediteur": message.id_expediteur,
        "id_destinataire": message.id_destinataire,
        "contenu": message.contenu,
        "createdAt": message.createdAt.isoformat(),
        "expediteur": format_user_info(message.expediteur),
        "destinataire": format_user_info(message.destinataire)
    }


# ===========================
# MESSAGE ENDPOINTS
# ===========================

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Send a message to another user
    
    - Teachers can message students
    - Students can message teachers
    - Department heads can message anyone
    """
    
    # Verify receiver exists
    receiver = await prisma.utilisateur.find_unique(
        where={"id": message_data.id_destinataire}
    )
    
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    # Verify role-based permissions
    # Teachers can message students, students can message teachers
    if current_user.role == "STUDENT" and receiver.role == "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot message other students directly"
        )
    
    # Create message
    message = await prisma.message.create(
        data={
            "id_expediteur": current_user.id,
            "id_destinataire": message_data.id_destinataire,
            "contenu": message_data.contenu
        },
        include={
            "expediteur": True,
            "destinataire": True
        }
    )
    
    return format_message_response(message)


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get all conversations for current user
    
    Returns a list of users the current user has messaged with,
    along with the last message and unread count
    """
    
    # Get all messages involving the current user
    sent_messages = await prisma.message.find_many(
        where={"id_expediteur": current_user.id},
        include={"destinataire": True},
        order_by={"createdAt": "desc"}
    )
    
    received_messages = await prisma.message.find_many(
        where={"id_destinataire": current_user.id},
        include={"expediteur": True},
        order_by={"createdAt": "desc"}
    )
    
    # Build conversations map
    conversations_map = {}
    
    # Process sent messages
    for msg in sent_messages:
        other_user_id = msg.id_destinataire
        if other_user_id not in conversations_map:
            conversations_map[other_user_id] = {
                "user": msg.destinataire,
                "last_message": msg,
                "last_timestamp": msg.createdAt
            }
        elif msg.createdAt > conversations_map[other_user_id]["last_timestamp"]:
            conversations_map[other_user_id]["last_message"] = msg
            conversations_map[other_user_id]["last_timestamp"] = msg.createdAt
    
    # Process received messages
    for msg in received_messages:
        other_user_id = msg.id_expediteur
        if other_user_id not in conversations_map:
            conversations_map[other_user_id] = {
                "user": msg.expediteur,
                "last_message": msg,
                "last_timestamp": msg.createdAt
            }
        elif msg.createdAt > conversations_map[other_user_id]["last_timestamp"]:
            conversations_map[other_user_id]["last_message"] = msg
            conversations_map[other_user_id]["last_timestamp"] = msg.createdAt
    
    # Format conversations
    conversations = []
    for user_id, conv_data in conversations_map.items():
        # Count unread messages from this user
        unread_count = await prisma.message.count(
            where={
                "id_expediteur": user_id,
                "id_destinataire": current_user.id
            }
        )
        
        conversations.append({
            "userId": user_id,
            "user": format_user_info(conv_data["user"]),
            "lastMessage": {
                "contenu": conv_data["last_message"].contenu,
                "createdAt": conv_data["last_message"].createdAt.isoformat(),
                "isSent": conv_data["last_message"].id_expediteur == current_user.id
            },
            "unreadCount": unread_count if conv_data["last_message"].id_expediteur != current_user.id else 0
        })
    
    # Sort by last message timestamp
    conversations.sort(key=lambda x: x["lastMessage"]["createdAt"], reverse=True)
    
    return conversations


@router.get("/conversation/{other_user_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    other_user_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get all messages in a conversation with another user
    
    Returns messages in chronological order (oldest first)
    """
    
    # Verify other user exists
    other_user = await prisma.utilisateur.find_unique(
        where={"id": other_user_id}
    )
    
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all messages between these two users
    messages = await prisma.message.find_many(
        where={
            "OR": [
                {
                    "id_expediteur": current_user.id,
                    "id_destinataire": other_user_id
                },
                {
                    "id_expediteur": other_user_id,
                    "id_destinataire": current_user.id
                }
            ]
        },
        include={
            "expediteur": True,
            "destinataire": True
        },
        order_by={"createdAt": "asc"}
    )
    
    return [format_message_response(msg) for msg in messages]


@router.get("/users/search", response_model=List[UserInfo])
async def search_users(
    query: str = Query(..., min_length=2, description="Search query"),
    role: Optional[str] = Query(None, description="Filter by role: TEACHER or STUDENT"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Search for users to start a conversation with
    
    - Students can search for teachers
    - Teachers can search for students THEY TEACH
    - Department heads can search anyone
    """
    
    # Special handling for teachers - only show students they teach
    if current_user.role == "TEACHER":
        # Get all students this teacher teaches
        teacher = await prisma.enseignant.find_unique(
            where={"id_utilisateur": current_user.id}
        )
        
        if not teacher:
            return []
        
        # Find all groups taught by this teacher through schedules
        schedules = await prisma.emploitemps.find_many(
            where={"id_enseignant": teacher.id},
            select={"id_groupe": True},
            distinct=["id_groupe"]
        )
        
        group_ids = [s.id_groupe for s in schedules]
        
        if not group_ids:
            return []
        
        # Get students in these groups
        students = await prisma.etudiant.find_many(
            where={
                "id_groupe": {"in": group_ids}
            },
            include={"utilisateur": True}
        )
        
        # Filter by search query
        filtered_students = []
        for student in students:
            user = student.utilisateur
            if (query.lower() in user.nom.lower() or 
                query.lower() in user.prenom.lower() or 
                query.lower() in user.email.lower()):
                filtered_students.append(format_user_info(user))
        
        return filtered_students[:20]  # Limit to 20 results
    
    # For non-teachers, use the original logic
    where_clause = {
        "id": {"not": current_user.id},  # Exclude self
        "OR": [
            {"nom": {"contains": query, "mode": "insensitive"}},
            {"prenom": {"contains": query, "mode": "insensitive"}},
            {"email": {"contains": query, "mode": "insensitive"}}
        ]
    }
    
    # Role-based filtering
    if current_user.role == "STUDENT":
        # Students can only message teachers
        where_clause["role"] = "TEACHER"
    elif role:
        # Department heads can filter by role if specified
        where_clause["role"] = role
    
    users = await prisma.utilisateur.find_many(
        where=where_clause,
        take=20,  # Limit results
        order_by=[
            {"nom": "asc"},
            {"prenom": "asc"}
        ]
    )
    
    return [format_user_info(user) for user in users]


@router.get("/unread-count")
async def get_unread_count(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get count of unread messages for current user
    
    Returns total number of unread messages
    """
    
    unread_count = await prisma.message.count(
        where={"id_destinataire": current_user.id}
    )
    
    return {"unread_count": unread_count}


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Delete a message (only sender can delete)
    """
    
    message = await prisma.message.find_unique(
        where={"id": message_id}
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only sender can delete their own messages
    if message.id_expediteur != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )
    
    await prisma.message.delete(
        where={"id": message_id}
    )
    
    return {"message": "Message deleted successfully"}


# ===========================
# STATISTICS
# ===========================

@router.get("/stats")
async def get_message_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get messaging statistics for current user
    """
    
    sent_count = await prisma.message.count(
        where={"id_expediteur": current_user.id}
    )
    
    received_count = await prisma.message.count(
        where={"id_destinataire": current_user.id}
    )
    
    # Get conversation count (unique users)
    sent_users = await prisma.message.find_many(
        where={"id_expediteur": current_user.id},
        select={"id_destinataire": True},
        distinct=["id_destinataire"]
    )
    
    received_users = await prisma.message.find_many(
        where={"id_destinataire": current_user.id},
        select={"id_expediteur": True},
        distinct=["id_expediteur"]
    )
    
    unique_users = set([u.id_destinataire for u in sent_users] + [u.id_expediteur for u in received_users])
    
    return {
        "sent_messages": sent_count,
        "received_messages": received_count,
        "total_conversations": len(unique_users),
        "unread_messages": received_count  # Since we don't have isRead field yet
    }
