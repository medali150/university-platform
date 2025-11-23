"""
Admin API - Teachers Management (FIXED)
Correct French Prisma model names
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/admin/teachers", tags=["Admin - Teachers"])


class TeacherResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    departement: Optional[dict] = None
    
    class Config:
        from_attributes = True


class TeacherUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    id_departement: Optional[str] = None
    image_url: Optional[str] = None


@router.get("/", response_model=List[TeacherResponse])
async def get_all_teachers(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all teachers (Admin only) - FIXED"""
    try:
        print("👨‍🏫 Fetching teachers with French model names...")
        
        teachers = await prisma.enseignant.find_many(
            include={
                "departement": True
            }
        )
        
        print(f"✅ Found {len(teachers)} teachers")
        
        result = []
        for teacher in teachers:
            result.append({
                "id": teacher.id,
                "firstName": teacher.prenom,
                "lastName": teacher.nom,
                "email": teacher.email,
                "departement": {
                    "id": teacher.departement.id,
                    "nom": teacher.departement.nom
                } if teacher.departement else None
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


@router.get("/{teacher_id}")
async def get_teacher(
    teacher_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get teacher by ID"""
    try:
        teacher = await prisma.enseignant.find_unique(
            where={"id": teacher_id},
            include={
                "departement": True,
                "matieres": True
            }
        )
        
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        return {
            "id": teacher.id,
            "firstName": teacher.prenom,
            "lastName": teacher.nom,
            "email": teacher.email,
            "departement": {
                "id": teacher.departement.id,
                "nom": teacher.departement.nom
            } if teacher.departement else None,
            "matieres": [
                {
                    "id": m.id,
                    "nom": m.nom
                } for m in teacher.matieres
            ] if teacher.matieres else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: str,
    data: TeacherUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a teacher"""
    try:
        existing = await prisma.enseignant.find_unique(where={"id": teacher_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        
        teacher = await prisma.enseignant.update(
            where={"id": teacher_id},
            data=update_data,
            include={
                "departement": True,
                "utilisateur": True
            }
        )
        
        # Update user account if email/name changed
        if data.email or data.nom or data.prenom:
            user_update = {}
            if data.email: user_update["email"] = data.email
            if data.nom: user_update["nom"] = data.nom
            if data.prenom: user_update["prenom"] = data.prenom
            
            await prisma.utilisateur.update_many(
                where={"enseignant_id": teacher_id},
                data=user_update
            )
        
        return {
            "id": teacher.id,
            "firstName": teacher.prenom,
            "lastName": teacher.nom,
            "email": teacher.email,
            "departement": {
                "id": teacher.departement.id,
                "nom": teacher.departement.nom
            } if teacher.departement else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_teachers_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get teachers statistics"""
    try:
        total = await prisma.enseignant.count()
        
        return {
            "total": total,
            "message": f"{total} enseignants dans la base de données"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
