from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.prisma_client import lifespan
from app.routers import auth, admin, departments, specialties
from app.routers import students_crud, teachers_crud, department_heads_crud
from app.routers import levels_crud, subjects_crud, schedules, admin_dashboard
from app.routers import department_head_dashboard, department_head_timetable
from app.routers import levels_public

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

# Include routers
app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(specialties.router)
app.include_router(admin.router)
app.include_router(students_crud.router)
app.include_router(teachers_crud.router)
app.include_router(department_heads_crud.router)
app.include_router(levels_crud.router)
app.include_router(subjects_crud.router)
app.include_router(levels_public.router)
app.include_router(schedules.router)
app.include_router(admin_dashboard.router)
app.include_router(department_head_dashboard.router)
app.include_router(department_head_timetable.router)


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
            "department_head_dashboard": "/department-head"
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