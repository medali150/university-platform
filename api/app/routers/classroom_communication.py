"""
Smart Classroom - Announcements & Discussions API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/classroom", tags=["Smart Classroom - Communication"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AnnouncementCreate(BaseModel):
    titre: Optional[str] = None
    contenu: str
    id_cours: str
    estEpingle: bool = False
    autoriserCommentaires: bool = True
    fichiers: Optional[dict] = None


class DiscussionCreate(BaseModel):
    titre: str
    contenu: str
    id_cours: str


class ReplyCreate(BaseModel):
    contenu: str


class CommentCreate(BaseModel):
    contenu: str


# ============================================================================
# ANNOUNCEMENTS
# ============================================================================

@router.post("/announcements", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create course announcement (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can create announcements")
    
    try:
        # Verify course ownership
        course = await prisma.cours.find_unique(where={"id": announcement_data.id_cours})
        if not course or course.id_enseignant != current_user.enseignant_id:
            raise HTTPException(status_code=403, detail="You don't have permission for this course")
        
        announcement = await prisma.annoncecours.create(
            data={
                **announcement_data.dict(),
                "id_auteur": current_user.id
            }
        )
        
        print(f"✅ Announcement created in course {announcement_data.id_cours}")
        
        # TODO: Send notifications to all enrolled students
        
        return announcement
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}/announcements")
async def get_course_announcements(
    course_id: str,
    limit: int = 20,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course announcements"""
    
    try:
        announcements = await prisma.annoncecours.find_many(
            where={"id_cours": course_id},
            include={
                "auteur": True,
                "commentaires": {
                    "include": {"utilisateur": True}
                }
            },
            order=[
                {"estEpingle": "desc"},
                {"createdAt": "desc"}
            ],
            take=limit
        )
        
        return announcements
        
    except Exception as e:
        print(f"❌ Error fetching announcements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/announcements/{announcement_id}/comments")
async def add_announcement_comment(
    announcement_id: str,
    comment_data: CommentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Add comment to announcement"""
    
    try:
        announcement = await prisma.annoncecours.find_unique(where={"id": announcement_id})
        
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        if not announcement.autoriserCommentaires:
            raise HTTPException(status_code=403, detail="Comments are disabled for this announcement")
        
        comment = await prisma.commentaireannonce.create(
            data={
                "id_annonce": announcement_id,
                "id_utilisateur": current_user.id,
                "contenu": comment_data.contenu
            },
            include={"utilisateur": True}
        )
        
        print(f"✅ Comment added to announcement {announcement_id}")
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete announcement (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can delete announcements")
    
    try:
        announcement = await prisma.annoncecours.find_unique(where={"id": announcement_id})
        
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        if announcement.id_auteur != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own announcements")
        
        await prisma.annoncecours.delete(where={"id": announcement_id})
        
        print(f"✅ Announcement deleted: {announcement_id}")
        return {"message": "Announcement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DISCUSSIONS / FORUM
# ============================================================================

@router.post("/discussions", status_code=status.HTTP_201_CREATED)
async def create_discussion(
    discussion_data: DiscussionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create discussion thread"""
    
    try:
        # Verify user is enrolled in course
        if current_user.role == "STUDENT":
            enrollment = await prisma.inscriptioncours.find_first(
                where={
                    "id_cours": discussion_data.id_cours,
                    "id_etudiant": current_user.etudiant_id,
                    "statut": "active"
                }
            )
            if not enrollment:
                raise HTTPException(status_code=403, detail="You must be enrolled to post discussions")
        
        discussion = await prisma.discussion.create(
            data={
                **discussion_data.dict(),
                "id_auteur": current_user.id
            },
            include={"auteur": True}
        )
        
        print(f"✅ Discussion created: {discussion.titre}")
        return discussion
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}/discussions")
async def get_course_discussions(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course discussions"""
    
    try:
        discussions = await prisma.discussion.find_many(
            where={"id_cours": course_id},
            include={
                "auteur": True,
                "reponses": {
                    "include": {"auteur": True},
                    "order": {"createdAt": "asc"}
                }
            },
            order=[
                {"estEpingle": "desc"},
                {"createdAt": "desc"}
            ]
        )
        
        return discussions
        
    except Exception as e:
        print(f"❌ Error fetching discussions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discussions/{discussion_id}")
async def get_discussion(
    discussion_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get discussion details"""
    
    try:
        discussion = await prisma.discussion.find_unique(
            where={"id": discussion_id},
            include={
                "auteur": True,
                "cours": True,
                "reponses": {
                    "include": {"auteur": True},
                    "order": {"createdAt": "asc"}
                }
            }
        )
        
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")
        
        # Increment view count
        await prisma.discussion.update(
            where={"id": discussion_id},
            data={"nbVues": discussion.nbVues + 1}
        )
        
        return discussion
        
    except Exception as e:
        print(f"❌ Error fetching discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discussions/{discussion_id}/replies")
async def add_discussion_reply(
    discussion_id: str,
    reply_data: ReplyCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Add reply to discussion"""
    
    try:
        discussion = await prisma.discussion.find_unique(where={"id": discussion_id})
        
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")
        
        if discussion.estVerrouille:
            raise HTTPException(status_code=403, detail="Discussion is locked")
        
        reply = await prisma.reponsediscussion.create(
            data={
                "id_discussion": discussion_id,
                "id_auteur": current_user.id,
                "contenu": reply_data.contenu
            },
            include={"auteur": True}
        )
        
        # Update reply count
        await prisma.discussion.update(
            where={"id": discussion_id},
            data={"nbReponses": discussion.nbReponses + 1}
        )
        
        print(f"✅ Reply added to discussion {discussion_id}")
        return reply
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error adding reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/discussions/{discussion_id}/resolve")
async def resolve_discussion(
    discussion_id: str,
    reply_id: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Mark discussion as resolved"""
    
    try:
        discussion = await prisma.discussion.find_unique(where={"id": discussion_id})
        
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")
        
        # Only author or teacher can resolve
        if discussion.id_auteur != current_user.id and current_user.role != "TEACHER":
            raise HTTPException(status_code=403, detail="Only the author or teacher can resolve")
        
        # Update discussion
        await prisma.discussion.update(
            where={"id": discussion_id},
            data={"estResolu": True}
        )
        
        # Mark best answer if provided
        if reply_id:
            await prisma.reponsediscussion.update(
                where={"id": reply_id},
                data={"estMeilleure": True}
            )
        
        print(f"✅ Discussion resolved: {discussion_id}")
        return {"message": "Discussion marked as resolved"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error resolving discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/discussions/{discussion_id}")
async def delete_discussion(
    discussion_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete discussion"""
    
    try:
        discussion = await prisma.discussion.find_unique(where={"id": discussion_id})
        
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")
        
        # Only author or teacher can delete
        if discussion.id_auteur != current_user.id and current_user.role != "TEACHER":
            raise HTTPException(status_code=403, detail="You don't have permission to delete")
        
        await prisma.discussion.delete(where={"id": discussion_id})
        
        print(f"✅ Discussion deleted: {discussion_id}")
        return {"message": "Discussion deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
