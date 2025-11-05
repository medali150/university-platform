"""
Admin API - Students Management (FIXED)
Correct French Prisma model names
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/admin/students", tags=["Admin - Students"])


class StudentResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    groupe: Optional[dict] = None
    specialite: Optional[dict] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[StudentResponse])
async def get_all_students(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all students (Admin only) - FIXED"""
    try:
        print("📚 Fetching students with French model names...")
        
        students = await prisma.etudiant.find_many(
            include={
                "groupe": True,
                "specialite": True
            }
        )
        
        print(f"✅ Found {len(students)} students")
        
        result = []
        for student in students:
            result.append({
                "id": student.id,
                "firstName": student.prenom,
                "lastName": student.nom,
                "email": student.email,
                "groupe": {
                    "id": student.groupe.id,
                    "nom": student.groupe.nom
                } if student.groupe else None,
                "specialite": {
                    "id": student.specialite.id,
                    "nom": student.specialite.nom
                } if student.specialite else None
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{student_id}")
async def get_student(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get student by ID"""
    try:
        student = await prisma.etudiant.find_unique(
            where={"id": student_id},
            include={
                "groupe": True,
                "specialite": True,
                "niveau": True
            }
        )
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "id": student.id,
            "firstName": student.prenom,
            "lastName": student.nom,
            "email": student.email,
            "groupe": {
                "id": student.groupe.id,
                "nom": student.groupe.nom
            } if student.groupe else None,
            "specialite": {
                "id": student.specialite.id,
                "nom": student.specialite.nom
            } if student.specialite else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_students_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get students statistics"""
    try:
        total = await prisma.etudiant.count()
        
        return {
            "total": total,
            "message": f"{total} étudiants dans la base de données"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
