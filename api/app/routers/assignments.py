"""
Smart Classroom - Assignments Management API
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/classroom/assignments", tags=["Smart Classroom - Assignments"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AssignmentCreate(BaseModel):
    titre: str
    description: str
    instructions: Optional[str] = None
    id_cours: str
    type: str = "assignment"  # assignment, quiz, project, exam
    points: int = 100
    dateLimite: datetime
    dateDisponible: Optional[datetime] = None
    autoriserSoumissionTardive: bool = False
    penaliteRetard: Optional[int] = None
    attemptsMax: int = 1
    afficherCorrection: bool = True
    detectionPlagiat: bool = True
    feedbackAI: bool = True


class SubmissionCreate(BaseModel):
    contenu: Optional[str] = None
    fichiers: Optional[dict] = None  # JSON with file info


class GradeSubmission(BaseModel):
    note: float
    feedback: Optional[str] = None


# ============================================================================
# ASSIGNMENTS CRUD
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create new assignment (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    
    try:
        # Verify course ownership
        course = await prisma.cours.find_unique(where={"id": assignment_data.id_cours})
        if not course or course.id_enseignant != current_user.enseignant_id:
            raise HTTPException(status_code=403, detail="You don't have permission for this course")
        
        assignment = await prisma.devoir.create(data=assignment_data.dict())
        
        print(f"✅ Assignment created: {assignment.titre}")
        return assignment
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/course/{course_id}")
async def get_course_assignments(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all assignments for a course"""
    
    try:
        assignments = await prisma.devoir.find_many(
            where={"id_cours": course_id},
            include={"soumissions": True},
            order={"dateLimite": "asc"}
        )
        
        # Add submission stats for each assignment
        result = []
        for assignment in assignments:
            stats = {
                "total_submissions": len(assignment.soumissions),
                "graded": len([s for s in assignment.soumissions if s.statut == "graded"]),
                "pending": len([s for s in assignment.soumissions if s.statut == "submitted"])
            }
            
            # Check if current user submitted
            user_submission = None
            if current_user.role == "STUDENT":
                user_submission = next(
                    (s for s in assignment.soumissions if s.id_etudiant == current_user.etudiant_id),
                    None
                )
            
            result.append({
                **assignment.dict(),
                "stats": stats,
                "user_submission": user_submission.dict() if user_submission else None
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get assignment details"""
    
    try:
        assignment = await prisma.devoir.find_unique(
            where={"id": assignment_id},
            include={
                "cours": True,
                "soumissions": {
                    "include": {
                        "etudiant": {"include": {"utilisateur": True}}
                    }
                },
                "rubriques": True
            }
        )
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        return assignment
        
    except Exception as e:
        print(f"❌ Error fetching assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUBMISSIONS
# ============================================================================

@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str,
    submission_data: SubmissionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Submit assignment (Students only)"""
    
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    try:
        # Get assignment
        assignment = await prisma.devoir.find_unique(where={"id": assignment_id})
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Check deadline
        is_late = datetime.now() > assignment.dateLimite
        if is_late and not assignment.autoriserSoumissionTardive:
            raise HTTPException(status_code=400, detail="Assignment deadline has passed")
        
        # Check attempts
        existing_submissions = await prisma.soumissiondevoir.find_many(
            where={
                "id_devoir": assignment_id,
                "id_etudiant": current_user.etudiant_id
            }
        )
        
        if len(existing_submissions) >= assignment.attemptsMax:
            raise HTTPException(status_code=400, detail="Maximum attempts reached")
        
        # Create submission
        submission = await prisma.soumissiondevoir.create(
            data={
                "id_devoir": assignment_id,
                "id_etudiant": current_user.etudiant_id,
                "contenu": submission_data.contenu,
                "fichiers": submission_data.fichiers,
                "statut": "submitted",
                "tentativeNumero": len(existing_submissions) + 1,
                "estEnRetard": is_late
            }
        )
        
        print(f"✅ Submission created for student {current_user.email}")
        
        # TODO: Trigger plagiarism detection if enabled
        # TODO: Trigger AI feedback generation if enabled
        
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error submitting assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assignment_id}/submissions")
async def get_assignment_submissions(
    assignment_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all submissions for an assignment (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")
    
    try:
        submissions = await prisma.soumissiondevoir.find_many(
            where={"id_devoir": assignment_id},
            include={
                "etudiant": {"include": {"utilisateur": True}},
                "commentaires": True
            },
            order={"dateSoumission": "desc"}
        )
        
        return submissions
        
    except Exception as e:
        print(f"❌ Error fetching submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: str,
    grade_data: GradeSubmission,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Grade a submission (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can grade submissions")
    
    try:
        submission = await prisma.soumissiondevoir.find_unique(
            where={"id": submission_id},
            include={"devoir": True}
        )
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Validate grade
        if grade_data.note < 0 or grade_data.note > submission.devoir.points:
            raise HTTPException(
                status_code=400,
                detail=f"Grade must be between 0 and {submission.devoir.points}"
            )
        
        # Update submission
        updated_submission = await prisma.soumissiondevoir.update(
            where={"id": submission_id},
            data={
                "note": grade_data.note,
                "noteMax": submission.devoir.points,
                "feedback": grade_data.feedback,
                "statut": "graded",
                "dateNotation": datetime.now()
            }
        )
        
        print(f"✅ Submission graded: {grade_data.note}/{submission.devoir.points}")
        
        # TODO: Send notification to student
        
        return updated_submission
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error grading submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}")
async def get_submission(
    submission_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get submission details"""
    
    try:
        submission = await prisma.soumissiondevoir.find_unique(
            where={"id": submission_id},
            include={
                "devoir": {"include": {"cours": True}},
                "etudiant": {"include": {"utilisateur": True}},
                "commentaires": {
                    "include": {"utilisateur": True},
                    "order": {"createdAt": "asc"}
                }
            }
        )
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Check permission
        if current_user.role == "STUDENT" and submission.id_etudiant != current_user.etudiant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))
