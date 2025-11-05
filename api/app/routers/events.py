"""
Events & News System API Router
Department heads can post events, formations, and news
Students can view, react, and comment
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_department_head
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Events & News"])


# ===========================
# REQUEST/RESPONSE MODELS
# ===========================

class EventCreate(BaseModel):
    """Request to create a new event"""
    titre: str
    type: str  # FORMATION, NEWS, ANNOUNCEMENT, EXAM, OTHER
    description: Optional[str] = None
    date: str  # ISO format datetime
    lieu: Optional[str] = None  # Location
    
    class Config:
        schema_extra = {
            "example": {
                "titre": "Formation sur Python Avancé",
                "type": "FORMATION",
                "description": "Formation intensive de 3 jours sur Python...",
                "date": "2025-11-15T09:00:00",
                "lieu": "Salle A201"
            }
        }


class EventUpdate(BaseModel):
    """Request to update an event"""
    titre: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    lieu: Optional[str] = None


class CommentCreate(BaseModel):
    """Request to add a comment"""
    contenu: str
    
    class Config:
        schema_extra = {
            "example": {
                "contenu": "Est-ce que cette formation est obligatoire ?"
            }
        }


class ReactionCreate(BaseModel):
    """Request to add a reaction"""
    type: str  # LIKE, LOVE, INTERESTED, GOING, NOT_GOING
    
    class Config:
        schema_extra = {
            "example": {
                "type": "INTERESTED"
            }
        }


# ===========================
# HELPER FUNCTIONS
# ===========================

def format_user_info(user) -> dict:
    """Format user data for API response"""
    return {
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "role": user.role
    }


async def get_event_with_details(event, prisma: Prisma, current_user_id: str):
    """Get event with comments, reactions, and stats"""
    
    # Get comments
    comments = await prisma.eventcomment.find_many(
        where={"id_evenement": event.id},
        include={"utilisateur": True}
    )
    
    # Get reactions
    reactions = await prisma.eventreaction.find_many(
        where={"id_evenement": event.id},
        include={"utilisateur": True}
    )
    
    # Check if current user reacted
    user_reaction = next((r for r in reactions if r.id_utilisateur == current_user_id), None)
    
    # Get creator info
    creator = await prisma.utilisateur.find_unique(
        where={"id": event.id_createur}
    )
    
    # Count reaction types
    reaction_counts = {}
    for reaction in reactions:
        reaction_counts[reaction.type] = reaction_counts.get(reaction.type, 0) + 1
    
    return {
        "id": event.id,
        "titre": event.titre,
        "type": event.type,
        "description": event.description,
        "date": event.date.isoformat() if event.date else None,
        "lieu": event.lieu,
        "createdAt": event.createdAt.isoformat(),
        "updatedAt": event.updatedAt.isoformat(),
        "creator": format_user_info(creator) if creator else None,
        "comments": [
            {
                "id": c.id,
                "contenu": c.contenu,
                "createdAt": c.createdAt.isoformat(),
                "user": format_user_info(c.utilisateur)
            }
            for c in sorted(comments, key=lambda x: x.createdAt, reverse=True)
        ],
        "reactions": {
            "counts": reaction_counts,
            "total": len(reactions),
            "userReaction": user_reaction.type if user_reaction else None
        },
        "stats": {
            "commentsCount": len(comments),
            "reactionsCount": len(reactions)
        }
    }


# ===========================
# EVENT ENDPOINTS
# ===========================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """
    Create a new event (Department heads only)
    
    Event types:
    - FORMATION: Training/workshop
    - NEWS: General news
    - ANNOUNCEMENT: Important announcements
    - EXAM: Exam schedules
    - OTHER: Other events
    """
    
    # Parse date
    event_date = datetime.fromisoformat(event_data.date.replace('Z', '+00:00'))
    
    event = await prisma.evenement.create(
        data={
            "titre": event_data.titre,
            "type": event_data.type,
            "description": event_data.description,
            "date": event_date,
            "lieu": event_data.lieu,
            "id_createur": current_user.id
        }
    )
    
    return await get_event_with_details(event, prisma, current_user.id)


@router.get("/")
async def get_events(
    type: Optional[str] = Query(None, description="Filter by event type"),
    upcoming: Optional[bool] = Query(None, description="Show only upcoming events"),
    limit: int = Query(50, ge=1, le=100),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Get all events
    
    - Students can see all events
    - Teachers can see all events
    - Department heads can see all events
    """
    
    where_clause = {}
    
    if type:
        where_clause["type"] = type
    
    if upcoming:
        where_clause["date"] = {"gte": datetime.now()}
    
    events = await prisma.evenement.find_many(
        where=where_clause,
        take=limit
    )
    
    # Sort in Python
    events.sort(key=lambda e: e.date if e.date else datetime.min, reverse=True)
    
    # Get details for each event
    result = []
    for event in events:
        event_details = await get_event_with_details(event, prisma, current_user.id)
        result.append(event_details)
    
    return result


@router.get("/{event_id}")
async def get_event(
    event_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get a single event with all details"""
    
    event = await prisma.evenement.find_unique(
        where={"id": event_id}
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return await get_event_with_details(event, prisma, current_user.id)


@router.put("/{event_id}")
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Update an event (Only creator or department head)"""
    
    event = await prisma.evenement.find_unique(
        where={"id": event_id}
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is creator
    if event.id_createur != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event creator can update this event"
        )
    
    # Build update data
    update_data = {}
    if event_data.titre is not None:
        update_data["titre"] = event_data.titre
    if event_data.type is not None:
        update_data["type"] = event_data.type
    if event_data.description is not None:
        update_data["description"] = event_data.description
    if event_data.date is not None:
        update_data["date"] = datetime.fromisoformat(event_data.date.replace('Z', '+00:00'))
    if event_data.lieu is not None:
        update_data["lieu"] = event_data.lieu
    
    updated_event = await prisma.evenement.update(
        where={"id": event_id},
        data=update_data
    )
    
    return await get_event_with_details(updated_event, prisma, current_user.id)


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Delete an event (Only creator)"""
    
    event = await prisma.evenement.find_unique(
        where={"id": event_id}
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is creator
    if event.id_createur != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event creator can delete this event"
        )
    
    # Delete related comments and reactions first
    await prisma.eventcomment.delete_many(where={"id_evenement": event_id})
    await prisma.eventreaction.delete_many(where={"id_evenement": event_id})
    
    await prisma.evenement.delete(where={"id": event_id})
    
    return {"message": "Event deleted successfully"}


# ===========================
# COMMENT ENDPOINTS
# ===========================

@router.post("/{event_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    event_id: str,
    comment_data: CommentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Add a comment to an event"""
    
    # Verify event exists
    event = await prisma.evenement.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    comment = await prisma.eventcomment.create(
        data={
            "id_evenement": event_id,
            "id_utilisateur": current_user.id,
            "contenu": comment_data.contenu
        },
        include={"utilisateur": True}
    )
    
    return {
        "id": comment.id,
        "contenu": comment.contenu,
        "createdAt": comment.createdAt.isoformat(),
        "user": format_user_info(comment.utilisateur)
    }


@router.delete("/{event_id}/comments/{comment_id}")
async def delete_comment(
    event_id: str,
    comment_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete a comment (Only comment author or department head)"""
    
    comment = await prisma.eventcomment.find_unique(
        where={"id": comment_id}
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is author or department head
    if comment.id_utilisateur != current_user.id and current_user.role != "DEPARTMENT_HEAD":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    await prisma.eventcomment.delete(where={"id": comment_id})
    
    return {"message": "Comment deleted successfully"}


# ===========================
# REACTION ENDPOINTS
# ===========================

@router.post("/{event_id}/reactions")
async def add_reaction(
    event_id: str,
    reaction_data: ReactionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Add or update a reaction to an event
    
    Reaction types:
    - LIKE: General like
    - LOVE: Love it
    - INTERESTED: Interested in attending
    - GOING: Will attend
    - NOT_GOING: Won't attend
    """
    
    # Verify event exists
    event = await prisma.evenement.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user already reacted
    existing_reaction = await prisma.eventreaction.find_first(
        where={
            "id_evenement": event_id,
            "id_utilisateur": current_user.id
        }
    )
    
    if existing_reaction:
        # Update existing reaction
        reaction = await prisma.eventreaction.update(
            where={"id": existing_reaction.id},
            data={"type": reaction_data.type}
        )
    else:
        # Create new reaction
        reaction = await prisma.eventreaction.create(
            data={
                "id_evenement": event_id,
                "id_utilisateur": current_user.id,
                "type": reaction_data.type
            }
        )
    
    # Get updated reaction counts
    all_reactions = await prisma.eventreaction.find_many(
        where={"id_evenement": event_id}
    )
    
    reaction_counts = {}
    for r in all_reactions:
        reaction_counts[r.type] = reaction_counts.get(r.type, 0) + 1
    
    return {
        "message": "Reaction updated",
        "userReaction": reaction.type,
        "counts": reaction_counts,
        "total": len(all_reactions)
    }


@router.delete("/{event_id}/reactions")
async def remove_reaction(
    event_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Remove user's reaction from an event"""
    
    reaction = await prisma.eventreaction.find_first(
        where={
            "id_evenement": event_id,
            "id_utilisateur": current_user.id
        }
    )
    
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    await prisma.eventreaction.delete(where={"id": reaction.id})
    
    return {"message": "Reaction removed"}


# ===========================
# STATISTICS
# ===========================

@router.get("/stats/summary")
async def get_events_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_department_head)
):
    """Get events statistics (Department heads only)"""
    
    total_events = await prisma.evenement.count()
    
    upcoming_events = await prisma.evenement.count(
        where={"date": {"gte": datetime.now()}}
    )
    
    total_comments = await prisma.eventcomment.count()
    total_reactions = await prisma.eventreaction.count()
    
    # Get events by type
    events = await prisma.evenement.find_many()
    events_by_type = {}
    for event in events:
        events_by_type[event.type] = events_by_type.get(event.type, 0) + 1
    
    return {
        "totalEvents": total_events,
        "upcomingEvents": upcoming_events,
        "totalComments": total_comments,
        "totalReactions": total_reactions,
        "eventsByType": events_by_type
    }
