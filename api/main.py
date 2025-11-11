from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.prisma_client import lifespan
from app.routers import auth, admin, departments, specialties
from app.routers import students_crud, teachers_crud, department_heads_crud
from app.routers import admin_students, admin_teachers, admin_department_heads  # NEW: Fixed admin routes
from app.routers import levels_crud, subjects_crud, rooms_crud, admin_dashboard
from app.routers import department_head_dashboard, department_head_timetable
from app.routers import semester_timetable  # ✅ ACTIVE: Semester-based timetable system
from app.routers import levels_public, absence_management, teacher_profile, simple_absences, absence_notifications, student_profile, debug_absences, room_occupancy, notifications
# Note: department_head_timetable provides helper endpoints (groups, teachers, rooms, subjects)
from app.routers import messages  # Messaging system for teacher-student communication
from app.routers import student_averages  # Student averages management for department heads
from app.routers import teacher_grades  # Teacher grade submission and management
from app.routers import student_grades  # Student grades viewing
from app.routers import department_head_analytics  # Department head analytics and statistics
from app.routers import events  # Events and news system
# Smart Classroom System - Google Classroom-like features
from app.routers import courses  # Course management
from app.routers import assignments  # Assignment creation, submission, grading
from app.routers import classroom_communication  # Announcements & discussions
from app.routers import classroom_materials  # Course materials & file uploads
from app.routers import classroom_ai  # AI assistant, plagiarism, feedback, summarization

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving files
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(specialties.router)
app.include_router(admin.router)
# app.include_router(students_crud.router)  # OLD - Has bugs
# app.include_router(teachers_crud.router)  # OLD - Has bugs
# app.include_router(department_heads_crud.router)  # OLD - Has bugs
app.include_router(admin_students.router)  # NEW: Fixed with French models
app.include_router(admin_teachers.router)  # NEW: Fixed with French models
app.include_router(admin_department_heads.router)  # NEW: Fixed with French models
app.include_router(levels_crud.router)
app.include_router(subjects_crud.router)
app.include_router(rooms_crud.router)  # NEW: Rooms CRUD
app.include_router(levels_public.router)
app.include_router(admin_dashboard.router)
app.include_router(department_head_dashboard.router)
app.include_router(department_head_timetable.router)  # Helper endpoints: groups, teachers, rooms, subjects
app.include_router(semester_timetable.router)  # ✅ MAIN: Semester timetable creation and management
app.include_router(absence_management.router)
app.include_router(teacher_profile.router)
app.include_router(simple_absences.router)
# app.include_router(timetable_management.router)  # OLD: Weekly management - DISABLED
app.include_router(absence_notifications.router)
app.include_router(student_profile.router)
app.include_router(debug_absences.router)
app.include_router(room_occupancy.router)
app.include_router(notifications.router)
# app.include_router(timetables_optimized.router)  # OLD: Conflicts with semester system - DISABLED
app.include_router(messages.router)  # NEW: Messaging system
app.include_router(student_averages.router)  # NEW: Student averages management
app.include_router(teacher_grades.router)  # NEW: Teacher grade submission
app.include_router(student_grades.router)  # NEW: Student grades viewing
app.include_router(department_head_analytics.router)  # NEW: Department head analytics
app.include_router(events.router)  # NEW: Events and news system
# Smart Classroom System
app.include_router(courses.router)  # NEW: Course management (create, enroll, analytics)
app.include_router(assignments.router)  # NEW: Assignments & submissions
app.include_router(classroom_communication.router)  # NEW: Announcements & discussions
app.include_router(classroom_materials.router)  # NEW: Course materials
app.include_router(classroom_ai.router)  # NEW: AI features


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": f"🎓 {settings.app_name}",
        "status": "running",
        "database": "PostgreSQL + Prisma",
        "version": settings.app_version,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth",
            "departments": "/departments",
            "specialties": "/specialties",
            "admin": "/admin",
            "student_management": "/admin/students",
            "teacher_management": "/admin/teachers", 
            "department_head_management": "/admin/department-heads",
            "level_management": "/admin/levels",
            "subject_management": "/admin/subjects",
            "schedule_management": "/schedules",
            "admin_dashboard": "/admin/dashboard",
            "department_head_timetable": "/department-head/timetable",
            "department_head_schedule": "/department-head/schedule",
            "department_head_dashboard": "/department-head",
            "absence_management": "/absences",
            "debug_absences": "/debug-absences",
            "room_occupancy": "/room-occupancy",
            "smart_classroom": {
                "courses": "/api/classroom/courses",
                "assignments": "/api/classroom/assignments",
                "announcements": "/api/classroom/announcements",
                "discussions": "/api/classroom/discussions",
                "materials": "/api/classroom/materials",
                "ai_chat": "/api/classroom/ai/chat",
                "plagiarism": "/api/classroom/ai/plagiarism/check",
                "ai_feedback": "/api/classroom/ai/feedback/generate",
                "summarize": "/api/classroom/ai/summarize"
            }
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    from app.db.prisma_client import get_prisma
    try:
        prisma = await get_prisma()
        # Test database connectivity - use French table name
        count = await prisma.utilisateur.count()
        return {
            "status": "healthy",
            "database": "connected",
            "users_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }


@app.post("/quick-login")
async def quick_login(email: str, password: str):
    """Quick login endpoint for testing"""
    from app.db.prisma_client import get_prisma
    from app.core.security import verify_password
    from app.core.jwt import create_access_token, create_refresh_token
    
    try:
        prisma = await get_prisma()
        
        # Find user
        user = await prisma.utilisateur.find_unique(where={"email": email})
        if not user:
            return {"error": "User not found"}
        
        # Verify password
        if not verify_password(password, user.mdp_hash):
            return {"error": "Invalid password"}
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "prenom": user.prenom,
                "nom": user.nom,
                "role": user.role,
                "firstName": user.prenom,
                "lastName": user.nom,
                "login": user.email
            }
        }
    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}