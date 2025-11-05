"""
Admin API - Department Heads Management (FIXED)
Correct French Prisma model names
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/admin/department-heads", tags=["Admin - Department Heads"])


class DepartmentHeadResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    login: Optional[str] = None
    role: str = "Chef de Département"
    departement: Optional[dict] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[DepartmentHeadResponse])
async def get_all_department_heads(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all department heads (Admin only) - FIXED"""
    try:
        print("👔 Fetching department heads with French model names...")
        
        dept_heads = await prisma.chefdepartement.find_many(
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        
        print(f"✅ Found {len(dept_heads)} department heads")
        
        result = []
        for dh in dept_heads:
            result.append({
                "id": dh.id,
                "firstName": dh.utilisateur.prenom if dh.utilisateur else "",
                "lastName": dh.utilisateur.nom if dh.utilisateur else "",
                "email": dh.utilisateur.email if dh.utilisateur else "",
                "login": dh.utilisateur.login if dh.utilisateur else "",
                "role": "Chef de Département",
                "departement": {
                    "id": dh.departement.id,
                    "nom": dh.departement.nom
                } if dh.departement else None
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


@router.get("/{dept_head_id}")
async def get_department_head(
    dept_head_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get department head by ID"""
    try:
        dept_head = await prisma.chefdepartement.find_unique(
            where={"id": dept_head_id},
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        
        if not dept_head:
            raise HTTPException(status_code=404, detail="Department head not found")
        
        return {
            "id": dept_head.id,
            "firstName": dept_head.utilisateur.prenom if dept_head.utilisateur else "",
            "lastName": dept_head.utilisateur.nom if dept_head.utilisateur else "",
            "email": dept_head.utilisateur.email if dept_head.utilisateur else "",
            "login": dept_head.utilisateur.login if dept_head.utilisateur else "",
            "role": "Chef de Département",
            "departement": {
                "id": dept_head.departement.id,
                "nom": dept_head.departement.nom
            } if dept_head.departement else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_dept_heads_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get department heads statistics"""
    try:
        total = await prisma.chefdepartement.count()
        
        return {
            "total": total,
            "message": f"{total} chefs de département dans la base de données"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
