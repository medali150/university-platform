"""
AI Teaching Assistant Chat API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime
from app.services.ai.openai_service import openai_service

router = APIRouter(prefix="/api/classroom/ai", tags=["Smart Classroom - AI Assistant"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatMessage(BaseModel):
    message: str
    course_id: Optional[str] = None
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    context_used: bool = False


# ============================================================================
# AI CHAT ASSISTANT
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    chat_data: ChatMessage,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Chat with AI teaching assistant
    
    Provides help with:
    - Course content questions
    - Assignment guidance
    - Study tips
    - General academic support
    """
    
    try:
        # Build context from course if provided
        context = ""
        
        if chat_data.course_id:
            # Get course info
            course = await prisma.cours.find_unique(
                where={"id": chat_data.course_id},
                include={
                    "materiaux": {"take": 5},
                    "devoirs": {"take": 3}
                }
            )
            
            if course:
                context = f"""
Context: User is in course "{course.nom}" (Code: {course.code})
Description: {course.description or "N/A"}

Recent materials: {', '.join([m.titre for m in course.materiaux]) if course.materiaux else "None"}
Recent assignments: {', '.join([d.titre for d in course.devoirs]) if course.devoirs else "None"}
"""
        
        # Build prompt
        prompt = _build_chat_prompt(
            message=chat_data.message,
            context=context,
            user_role=current_user.role
        )
        
        # Get AI response using Groq (ultra-fast!)
        ai_response = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=500,
            temperature=0.7
        )
        
        if not ai_response:
            raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
        
        # Save chat history
        try:
            await prisma.chatai.create(
                data={
                    "id_utilisateur": current_user.id,
                    "id_cours": chat_data.course_id if chat_data.course_id else None,
                    "question": chat_data.message,
                    "reponse": ai_response,
                    "contexte": {"has_course_context": bool(chat_data.course_id)} if chat_data.course_id else None,
                    "modeleAI": "llama-3.3-70b-versatile"
                }
            )
        except Exception as e:
            # Don't fail the request if chat history save fails
            print(f"⚠️ Failed to save chat history: {e}")
        
        print(f"✅ AI chat response generated for user {current_user.email}")
        
        return ChatResponse(
            response=ai_response,
            timestamp=datetime.utcnow(),
            context_used=bool(context)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_chat_prompt(message: str, context: str, user_role: str) -> str:
    """Build prompt for AI assistant"""
    
    role_context = {
        "STUDENT": "You are helping a student with their coursework.",
        "TEACHER": "You are assisting a teacher with course management and pedagogy.",
        "ADMIN": "You are helping an administrator with platform management."
    }
    
    prompt = f"""You are a helpful, knowledgeable AI teaching assistant for a university learning platform.

{role_context.get(user_role, "You are helping a user.")}

{context}

User Question: {message}

Provide a clear, helpful response that:
1. Directly addresses the question
2. Is educational and encouraging
3. Suggests next steps or resources when appropriate
4. Is concise (2-3 paragraphs maximum)

If you don't know something or the question is unclear, politely ask for clarification.
Do not make up information.
"""
    
    return prompt


@router.get("/chat/history")
async def get_chat_history(
    course_id: Optional[str] = None,
    limit: int = 20,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get user's chat history"""
    
    try:
        where_clause = {"id_utilisateur": current_user.id}
        
        if course_id:
            where_clause["id_cours"] = course_id
        
        chats = await prisma.chatai.find_many(
            where=where_clause,
            order={"createdAt": "desc"},
            take=limit
        )
        
        return chats
        
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{chat_id}")
async def delete_chat(
    chat_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete chat message"""
    
    try:
        chat = await prisma.chatai.find_unique(where={"id": chat_id})
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        if chat.id_utilisateur != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own chats")
        
        await prisma.chatai.delete(where={"id": chat_id})
        
        return {"message": "Chat deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLAGIARISM CHECK
# ============================================================================

@router.post("/plagiarism/check")
async def check_plagiarism(
    assignment_id: str,
    submission_text: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Check submission for plagiarism
    
    Compares against:
    - Other submissions in the same assignment
    - Online sources (simplified check)
    """
    
    try:
        from app.services.ai.plagiarism import plagiarism_detector
        
        # Get assignment
        assignment = await prisma.devoir.find_unique(where={"id": assignment_id})
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Get other submissions
        other_submissions = await prisma.soumissiondevoir.find_many(
            where={
                "id_devoir": assignment_id,
                "id_etudiant": {"not": current_user.etudiant_id}
            },
            include={"etudiant": {"include": {"utilisateur": True}}}
        )
        
        # Format for comparison
        comparison_data = [
            {
                "id": sub.id,
                "contenu": sub.contenu or "",
                "etudiant_nom": sub.etudiant.utilisateur.nom if sub.etudiant and sub.etudiant.utilisateur else "Unknown"
            }
            for sub in other_submissions
        ]
        
        # Run plagiarism check
        result = await plagiarism_detector.check_submission_against_class(
            submission_text,
            comparison_data
        )
        
        print(f"✅ Plagiarism check completed: {'FLAGGED' if result['is_plagiarized'] else 'CLEAN'}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error checking plagiarism: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI FEEDBACK GENERATION
# ============================================================================

@router.post("/feedback/generate")
async def generate_ai_feedback(
    submission_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Generate AI feedback for a submission (Teacher only)
    """
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can generate AI feedback")
    
    try:
        from app.services.ai.feedback import feedback_generator
        
        # Get submission with assignment details
        submission = await prisma.soumissiondevoir.find_unique(
            where={"id": submission_id},
            include={
                "devoir": True,
                "etudiant": {"include": {"utilisateur": True}}
            }
        )
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Generate feedback
        feedback = await feedback_generator.generate_feedback(
            assignment_title=submission.devoir.titre,
            assignment_instructions=submission.devoir.instructions or "",
            submission_content=submission.contenu or "",
            grade=float(submission.note) if submission.note else None,
            max_points=float(submission.devoir.points) if submission.devoir.points else None
        )
        
        if not feedback:
            raise HTTPException(status_code=503, detail="AI feedback generation failed")
        
        print(f"✅ AI feedback generated for submission {submission_id}")
        
        return {
            "submission_id": submission_id,
            "feedback": feedback,
            "student_name": submission.etudiant.utilisateur.nom if submission.etudiant.utilisateur else "Unknown",
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONTENT SUMMARIZATION
# ============================================================================

@router.post("/summarize")
async def summarize_content(
    material_id: str,
    style: str = "concise",  # concise, detailed, bullet_points
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Summarize course material using AI
    """
    
    try:
        from app.services.ai.summarization import content_summarizer
        
        # Get material
        material = await prisma.materielcours.find_unique(where={"id": material_id})
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        if not material.contenu:
            raise HTTPException(status_code=400, detail="Material has no content to summarize")
        
        # Generate summary
        summary = await content_summarizer.summarize_text(
            content=material.contenu,
            max_length=200,
            style=style
        )
        
        if not summary:
            raise HTTPException(status_code=503, detail="Summarization failed")
        
        print(f"✅ Content summarized: {material.titre}")
        
        return {
            "material_id": material_id,
            "title": material.titre,
            "summary": summary,
            "style": style,
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error summarizing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
