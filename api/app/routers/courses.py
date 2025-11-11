"""
Smart Classroom - Courses Management API
Similar to Google Classroom
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime
import secrets
import string

router = APIRouter(prefix="/api/classroom/courses", tags=["Smart Classroom - Courses"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CourseCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    couleur: str = "#3B82F6"
    id_departement: Optional[str] = None
    id_specialite: Optional[str] = None
    id_niveau: Optional[str] = None
    anneeAcademique: str  # "2024-2025"
    semestre: str  # "S1" or "S2"
    capaciteMax: Optional[int] = None
    estPublic: bool = False
    dateDebut: Optional[datetime] = None
    dateFin: Optional[datetime] = None


class CourseUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    couleur: Optional[str] = None
    capaciteMax: Optional[str] = None
    estActif: Optional[bool] = None
    estPublic: Optional[bool] = None
    dateDebut: Optional[datetime] = None
    dateFin: Optional[datetime] = None


class CourseResponse(BaseModel):
    id: str
    code: str
    nom: str
    description: Optional[str]
    imageUrl: Optional[str]
    couleur: str
    id_enseignant: str
    anneeAcademique: str
    semestre: str
    estActif: bool
    estPublic: bool
    codeInvitation: Optional[str]
    dateDebut: Optional[datetime]
    dateFin: Optional[datetime]
    createdAt: datetime
    
    # Stats
    nbEtudiants: int = 0
    nbDevoirs: int = 0
    nbMaterialux: int = 0
    
    class Config:
        from_attributes = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_course_code(nom: str, annee: str, semestre: str) -> str:
    """Generate unique course code like CS101-2025-S1"""
    # Take first 5 chars of course name (uppercase, no spaces)
    prefix = ''.join(nom.split())[:5].upper()
    # Add random number
    random_num = ''.join(secrets.choice(string.digits) for _ in range(3))
    return f"{prefix}{random_num}-{annee.replace('-', '')}-{semestre}"


def generate_join_code() -> str:
    """Generate 6-character join code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


async def check_teacher_permission(user, course_id: str, prisma: Prisma):
    """Check if user is the teacher of this course"""
    if user.role not in ["TEACHER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Only teachers can perform this action")
    
    if user.role == "TEACHER":
        # Verify teacher owns this course
        course = await prisma.cours.find_unique(where={"id": course_id})
        if not course or course.id_enseignant != user.enseignant_id:
            raise HTTPException(status_code=403, detail="You don't have permission for this course")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create a new course (Teachers only)"""
    
    # Check if user is teacher
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can create courses")
    
    if not current_user.enseignant_id:
        raise HTTPException(status_code=400, detail="Teacher profile not found")
    
    try:
        # Generate unique course code
        code = generate_course_code(
            course_data.nom,
            course_data.anneeAcademique,
            course_data.semestre
        )
        
        # Generate join code
        join_code = generate_join_code()
        
        # Create course
        course = await prisma.cours.create(
            data={
                "code": code,
                "nom": course_data.nom,
                "description": course_data.description,
                "imageUrl": course_data.imageUrl,
                "couleur": course_data.couleur,
                "id_enseignant": current_user.enseignant_id,
                "id_departement": course_data.id_departement,
                "id_specialite": course_data.id_specialite,
                "id_niveau": course_data.id_niveau,
                "anneeAcademique": course_data.anneeAcademique,
                "semestre": course_data.semestre,
                "capaciteMax": course_data.capaciteMax,
                "estPublic": course_data.estPublic,
                "codeInvitation": join_code,
                "dateDebut": course_data.dateDebut,
                "dateFin": course_data.dateFin
            }
        )
        
        print(f"✅ Course created: {course.nom} ({course.code}) - Invite code: {course.codeInvitation}")
        
        return {
            **course.dict(),
            "nbEtudiants": 0,
            "nbDevoirs": 0,
            "nbMateriaux": 0
        }
        
    except Exception as e:
        print(f"❌ Error creating course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CourseResponse])
async def get_my_courses(
    annee: Optional[str] = None,
    semestre: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get courses for current user (teacher or student)"""
    
    try:
        courses = []
        
        if current_user.role == "TEACHER":
            # Get courses taught by this teacher
            where_clause = {"id_enseignant": current_user.enseignant_id}
            if annee:
                where_clause["anneeAcademique"] = annee
            if semestre:
                where_clause["semestre"] = semestre
            
            courses = await prisma.cours.find_many(
                where=where_clause,
                include={
                    "inscriptions": True,
                    "devoirs": True,
                    "materiaux": True
                },
                order={"createdAt": "desc"}
            )
            
        elif current_user.role == "STUDENT":
            # Get courses student is enrolled in
            enrollments = await prisma.inscriptioncours.find_many(
                where={
                    "id_etudiant": current_user.etudiant_id,
                    "statut": "active"
                },
                include={
                    "cours": {
                        "include": {
                            "inscriptions": True,
                            "devoirs": True,
                            "materiaux": True
                        }
                    }
                }
            )
            
            courses = [e.cours for e in enrollments]
            
            # Filter by year/semester if provided
            if annee:
                courses = [c for c in courses if c.anneeAcademique == annee]
            if semestre:
                courses = [c for c in courses if c.semestre == semestre]
        
        # Format response with stats
        result = []
        for course in courses:
            result.append({
                **course.dict(),
                "nbEtudiants": len(course.inscriptions) if hasattr(course, 'inscriptions') else 0,
                "nbDevoirs": len(course.devoirs) if hasattr(course, 'devoirs') else 0,
                "nbMateriaux": len(course.materiaux) if hasattr(course, 'materiaux') else 0
            })
        
        print(f"✅ Found {len(result)} courses for user {current_user.email}")
        return result
        
    except Exception as e:
        print(f"❌ Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}")
async def get_course(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course details"""
    
    try:
        course = await prisma.cours.find_unique(
            where={"id": course_id},
            include={
                "enseignant": {"include": {"utilisateur": True}},
                "departement": True,
                "specialite": True,
                "niveau": True,
                "inscriptions": {
                    "include": {
                        "etudiant": {"include": {"utilisateur": True}}
                    }
                },
                "devoirs": True,
                "annonces": True
            }
        )
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check access permission
        has_access = False
        
        if current_user.role == "TEACHER" and course.id_enseignant == current_user.enseignant_id:
            has_access = True
        elif current_user.role == "STUDENT":
            enrollment = await prisma.inscriptioncours.find_first(
                where={
                    "id_cours": course_id,
                    "id_etudiant": current_user.etudiant_id,
                    "statut": "active"
                }
            )
            has_access = enrollment is not None
        elif current_user.role in ["ADMIN", "DEPARTMENT_HEAD"]:
            has_access = True
        
        if not has_access:
            raise HTTPException(status_code=403, detail="You don't have access to this course")
        
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{course_id}")
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Update course (Teacher only)"""
    
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        # Prepare update data (only include fields that are set)
        update_data = {k: v for k, v in course_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        course = await prisma.cours.update(
            where={"id": course_id},
            data=update_data
        )
        
        print(f"✅ Course updated: {course.nom}")
        return course
        
    except Exception as e:
        print(f"❌ Error updating course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete course (Teacher only)"""
    
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        await prisma.cours.delete(where={"id": course_id})
        print(f"✅ Course deleted: {course_id}")
        return {"message": "Course deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{course_id}/join")
async def join_course(
    course_id: str,
    code: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Join a course with invitation code (Students only)"""
    
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students can join courses")
    
    if not current_user.etudiant_id:
        raise HTTPException(status_code=400, detail="Student profile not found")
    
    try:
        # Get course
        course = await prisma.cours.find_unique(where={"id": course_id})
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if not course.estActif:
            raise HTTPException(status_code=400, detail="Course is not active")
        
        # Verify join code if course is not public
        if not course.estPublic:
            if not code or code != course.codeInvitation:
                raise HTTPException(status_code=403, detail="Invalid invitation code")
        
        # Check if already enrolled
        existing = await prisma.inscriptioncours.find_first(
            where={
                "id_cours": course_id,
                "id_etudiant": current_user.etudiant_id
            }
        )
        
        if existing:
            if existing.statut == "active":
                return {"message": "Already enrolled in this course"}
            else:
                # Re-activate enrollment
                await prisma.inscriptioncours.update(
                    where={"id": existing.id},
                    data={"statut": "active", "dateInscription": datetime.now()}
                )
                return {"message": "Re-enrolled in course"}
        
        # Check capacity
        if course.capaciteMax:
            enrolled_count = await prisma.inscriptioncours.count(
                where={"id_cours": course_id, "statut": "active"}
            )
            if enrolled_count >= course.capaciteMax:
                raise HTTPException(status_code=400, detail="Course is full")
        
        # Create enrollment
        enrollment = await prisma.inscriptioncours.create(
            data={
                "id_cours": course_id,
                "id_etudiant": current_user.etudiant_id,
                "statut": "active",
                "role": "student"
            }
        )
        
        print(f"✅ Student {current_user.email} joined course {course.nom}")
        return {"message": "Successfully joined course", "enrollment": enrollment}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error joining course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{course_id}/leave")
async def leave_course(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Leave a course (Students only)"""
    
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students can leave courses")
    
    try:
        enrollment = await prisma.inscriptioncours.find_first(
            where={
                "id_cours": course_id,
                "id_etudiant": current_user.etudiant_id,
                "statut": "active"
            }
        )
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Not enrolled in this course")
        
        # Update status to dropped
        await prisma.inscriptioncours.update(
            where={"id": enrollment.id},
            data={
                "statut": "dropped",
                "dateRetrait": datetime.now()
            }
        )
        
        print(f"✅ Student {current_user.email} left course {course_id}")
        return {"message": "Successfully left course"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error leaving course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/students")
async def get_course_students(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get list of students enrolled in course"""
    
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        enrollments = await prisma.inscriptioncours.find_many(
            where={
                "id_cours": course_id,
                "statut": "active"
            },
            include={
                "etudiant": {
                    "include": {
                        "utilisateur": True,
                        "groupe": True,
                        "specialite": True
                    }
                }
            },
            order={"dateInscription": "asc"}
        )
        
        students = []
        for enrollment in enrollments:
            student = enrollment.etudiant
            students.append({
                "id": student.id,
                "nom": student.nom,
                "prenom": student.prenom,
                "email": student.email,
                "groupe": student.groupe.nom if student.groupe else None,
                "specialite": student.specialite.nom if student.specialite else None,
                "dateInscription": enrollment.dateInscription,
                "role": enrollment.role
            })
        
        print(f"✅ Found {len(students)} students in course {course_id}")
        return students
        
    except Exception as e:
        print(f"❌ Error fetching students: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/analytics")
async def get_course_analytics(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course analytics (Teacher only)"""
    
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        # Get various stats
        nb_students = await prisma.inscriptioncours.count(
            where={"id_cours": course_id, "statut": "active"}
        )
        
        nb_assignments = await prisma.devoir.count(
            where={"id_cours": course_id}
        )
        
        nb_materials = await prisma.materielcours.count(
            where={"id_cours": course_id}
        )
        
        nb_discussions = await prisma.discussion.count(
            where={"id_cours": course_id}
        )
        
        nb_announcements = await prisma.annoncecours.count(
            where={"id_cours": course_id}
        )
        
        # Get assignment submissions stats
        assignments = await prisma.devoir.find_many(
            where={"id_cours": course_id},
            include={"soumissions": True}
        )
        
        total_submissions = sum(len(a.soumissions) for a in assignments)
        graded_submissions = sum(
            len([s for s in a.soumissions if s.statut == "graded"])
            for a in assignments
        )
        
        analytics = {
            "nb_students": nb_students,
            "nb_assignments": nb_assignments,
            "nb_materials": nb_materials,
            "nb_discussions": nb_discussions,
            "nb_announcements": nb_announcements,
            "submissions": {
                "total": total_submissions,
                "graded": graded_submissions,
                "pending": total_submissions - graded_submissions
            }
        }
        
        print(f"✅ Analytics fetched for course {course_id}")
        return analytics
        
    except Exception as e:
        print(f"❌ Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NESTED ROUTES - Assignments & Announcements
# ============================================================================

@router.get("/{course_id}/assignments")
async def get_course_assignments_route(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all assignments for a course"""
    
    try:
        assignments = await prisma.devoir.find_many(
            where={"id_cours": course_id}
        )
        
        return assignments
        
    except Exception as e:
        print(f"❌ Error fetching assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/announcements")
async def get_course_announcements_route(
    course_id: str,
    limit: int = 20,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course announcements"""
    
    try:
        announcements = await prisma.annoncecours.find_many(
            where={"id_cours": course_id},
            include={"auteur": True},
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


@router.get("/search/by-code/{invite_code}")
async def find_course_by_invite_code(
    invite_code: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Find a course by its invitation code"""
    
    try:
        course = await prisma.cours.find_first(
            where={
                "codeInvitation": invite_code.upper(),
                "estActif": True
            }
        )
        
        if not course:
            raise HTTPException(status_code=404, detail="Code d'invitation invalide")
        
        return {
            "id": course.id,
            "code": course.code,
            "nom": course.nom,
            "description": course.description,
            "anneeAcademique": course.anneeAcademique,
            "semestre": course.semestre,
            "couleur": course.couleur,
            "codeInvitation": course.codeInvitation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error searching course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/materials")
async def get_course_materials_route(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all materials for a course"""
    
    try:
        materials = await prisma.materielcours.find_many(
            where={"id_cours": course_id},
            order={"createdAt": "desc"}
        )
        
        return materials
        
    except Exception as e:
        print(f"❌ Error fetching materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/discussions")
async def get_course_discussions_route(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all discussions for a course"""
    
    try:
        discussions = await prisma.discussion.find_many(
            where={"id_cours": course_id},
            include={"auteur": True},
            order=[
                {"estEpingle": "desc"},
                {"createdAt": "desc"}
            ]
        )
        
        return discussions
        
    except Exception as e:
        print(f"❌ Error fetching discussions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/people")
async def get_course_people(
    course_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all people in a course (teacher and students)"""
    
    try:
        # Get course with teacher
        course = await prisma.cours.find_unique(
            where={"id": course_id},
            include={
                "enseignant": {
                    "include": {"utilisateur": True}
                }
            }
        )
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get enrolled students
        enrollments = await prisma.inscriptioncours.find_many(
            where={
                "id_cours": course_id,
                "statut": "active"
            },
            include={
                "etudiant": {
                    "include": {"utilisateur": True}
                }
            },
            order={"dateInscription": "desc"}
        )
        
        # Format teacher
        teacher = {
            "id": course.enseignant.utilisateur.id,
            "nom": course.enseignant.utilisateur.nom,
            "prenom": course.enseignant.utilisateur.prenom,
            "email": course.enseignant.utilisateur.email,
            "role": "TEACHER",
            "imageUrl": None
        }
        
        # Format students
        students = []
        for enrollment in enrollments:
            students.append({
                "id": enrollment.etudiant.utilisateur.id,
                "nom": enrollment.etudiant.utilisateur.nom,
                "prenom": enrollment.etudiant.utilisateur.prenom,
                "email": enrollment.etudiant.utilisateur.email,
                "role": "STUDENT",
                "enrolledAt": enrollment.dateInscription.isoformat(),
                "imageUrl": None
            })
        
        return {
            "teacher": teacher,
            "students": students,
            "totalCount": len(students) + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching course people: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CREATE CONTENT ROUTES (POST)
# ============================================================================

class AnnouncementCreate(BaseModel):
    content: str
    isPinned: bool = False
    allowComments: bool = True


@router.post("/{course_id}/announcements", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    course_id: str,
    announcement: AnnouncementCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create a new announcement for a course"""
    
    # Check teacher permission
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        # Create announcement (use user id directly as auteur)
        new_announcement = await prisma.annoncecours.create(
            data={
                "id_cours": course_id,
                "id_auteur": current_user.id,
                "contenu": announcement.content,
                "estEpingle": announcement.isPinned,
                "autoriserCommentaires": announcement.allowComments
            }
        )
        
        return new_announcement
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    points: int = 100
    dueDate: Optional[datetime] = None
    availableFrom: Optional[datetime] = None
    allowLateSubmissions: bool = True
    enablePlagiarismCheck: bool = True
    enableAIFeedback: bool = True


@router.post("/{course_id}/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    course_id: str,
    assignment: AssignmentCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create a new assignment for a course"""
    
    # Check teacher permission
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        # Set default deadline if not provided
        due_date = assignment.dueDate if assignment.dueDate else datetime.now()
        
        # Create assignment
        new_assignment = await prisma.devoir.create(
            data={
                "id_cours": course_id,
                "titre": assignment.title,
                "description": assignment.description or "",
                "instructions": assignment.instructions,
                "points": assignment.points,
                "dateLimite": due_date,
                "dateDisponible": assignment.availableFrom,
                "autoriserSoumissionTardive": assignment.allowLateSubmissions,
                "detectionPlagiat": assignment.enablePlagiarismCheck,
                "feedbackAI": assignment.enableAIFeedback
            }
        )
        
        return new_assignment
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class MaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None
    fileUrl: Optional[str] = None
    fileName: Optional[str] = None
    fileType: Optional[str] = None
    fileSize: Optional[int] = None
    folder: str = "General"


@router.post("/{course_id}/materials", status_code=status.HTTP_201_CREATED)
async def create_material(
    course_id: str,
    material: MaterialCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Upload/Add a new material to a course"""
    
    # Check teacher permission
    await check_teacher_permission(current_user, course_id, prisma)
    
    try:
        # Determine material type
        if material.fileUrl:
            mat_type = "link" if material.fileUrl.startswith("http") else "document"
        else:
            mat_type = "document"
        
        # Create material
        new_material = await prisma.materielcours.create(
            data={
                "id_cours": course_id,
                "titre": material.title,
                "description": material.description,
                "type": mat_type,
                "fichierUrl": material.fileUrl,
                "fichierNom": material.fileName,
                "fichierType": material.fileType,
                "fichierTaille": material.fileSize,
                "lienExterne": material.fileUrl if mat_type == "link" else None
            }
        )
        
        return new_material
        
    except Exception as e:
        print(f"❌ Error creating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DiscussionCreate(BaseModel):
    title: str
    content: str
    isPinned: bool = False


@router.post("/{course_id}/discussions", status_code=status.HTTP_201_CREATED)
async def create_discussion(
    course_id: str,
    discussion: DiscussionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create a new discussion for a course"""
    
    try:
        # Create discussion
        new_discussion = await prisma.discussion.create(
            data={
                "id_cours": course_id,
                "id_auteur": current_user.id,
                "titre": discussion.title,
                "contenu": discussion.content,
                "estEpingle": discussion.isPinned
            }
        )
        
        return new_discussion
        
    except Exception as e:
        print(f"❌ Error creating discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
