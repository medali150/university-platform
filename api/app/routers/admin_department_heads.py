"""
Admin API - Department Heads Management (FIXED)
Correct French Prisma model names
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin
from pydantic import BaseModel, EmailStr
import bcrypt

router = APIRouter(prefix="/admin/department-heads", tags=["Admin - Department Heads"])


class DepartmentHeadResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    role: str = "Chef de Département"
    departement: Optional[dict] = None
    
    class Config:
        from_attributes = True


class DepartmentHeadCreate(BaseModel):
    # Accept both English and French field names for compatibility
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: EmailStr
    password: str
    departmentId: Optional[str] = None
    id_departement: Optional[str] = None
    
    def get_nom(self) -> str:
        return self.nom or self.lastName or ""
    
    def get_prenom(self) -> str:
        return self.prenom or self.firstName or ""
    
    def get_id_departement(self) -> str:
        return self.id_departement or self.departmentId or ""


class DepartmentHeadUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    id_departement: Optional[str] = None


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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_department_head(
    data: DepartmentHeadCreate,
    department_id: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department head"""
    try:
        # Get field values with fallback
        nom = data.get_nom()
        prenom = data.get_prenom()
        # Use query parameter if provided, otherwise fallback to body fields
        id_departement = department_id or data.get_id_departement()
        
        if not nom or not prenom or not id_departement:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: nom/lastName, prenom/firstName, id_departement/departmentId"
            )
        
        # Check if department exists
        department = await prisma.departement.find_unique(where={"id": id_departement})
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Check if email already exists
        existing_user = await prisma.utilisateur.find_unique(where={"email": data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user first
        user = await prisma.utilisateur.create(
            data={
                "nom": nom,
                "prenom": prenom,
                "email": data.email,
                "mdp_hash": hashed_password,
                "role": "DEPARTMENT_HEAD"
            }
        )
        
        # Create department head
        dept_head = await prisma.chefdepartement.create(
            data={
                "id_utilisateur": user.id,
                "id_departement": id_departement
            },
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        
        return {
            "id": dept_head.id,
            "firstName": dept_head.utilisateur.prenom,
            "lastName": dept_head.utilisateur.nom,
            "email": dept_head.utilisateur.email,
            "role": "Chef de Département",
            "departement": {
                "id": dept_head.departement.id,
                "nom": dept_head.departement.nom
            } if dept_head.departement else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dept_head_id}")
async def update_department_head(
    dept_head_id: str,
    data: DepartmentHeadUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a department head"""
    try:
        existing = await prisma.chefdepartement.find_unique(
            where={"id": dept_head_id},
            include={"utilisateur": True}
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Department head not found")
        
        # Update department head
        update_data = {}
        if data.id_departement is not None:
            department = await prisma.departement.find_unique(where={"id": data.id_departement})
            if not department:
                raise HTTPException(status_code=404, detail="Department not found")
            update_data["id_departement"] = data.id_departement
        
        if update_data:
            await prisma.chefdepartement.update(
                where={"id": dept_head_id},
                data=update_data
            )
        
        # Update user if needed
        if data.email or data.nom or data.prenom:
            user_update = {}
            if data.email: user_update["email"] = data.email
            if data.nom: user_update["nom"] = data.nom
            if data.prenom: user_update["prenom"] = data.prenom
            
            await prisma.utilisateur.update(
                where={"id": existing.id_utilisateur},
                data=user_update
            )
        
        # Fetch updated record
        dept_head = await prisma.chefdepartement.find_unique(
            where={"id": dept_head_id},
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        
        return {
            "id": dept_head.id,
            "firstName": dept_head.utilisateur.prenom,
            "lastName": dept_head.utilisateur.nom,
            "email": dept_head.utilisateur.email,
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


@router.delete("/{dept_head_id}")
async def delete_department_head(
    dept_head_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a department head"""
    try:
        dept_head = await prisma.chefdepartement.find_unique(
            where={"id": dept_head_id},
            include={"utilisateur": True}
        )
        if not dept_head:
            raise HTTPException(status_code=404, detail="Department head not found")
        
        # Delete department head first
        await prisma.chefdepartement.delete(where={"id": dept_head_id})
        
        # Delete associated user
        if dept_head.id_utilisateur:
            await prisma.utilisateur.delete(where={"id": dept_head.id_utilisateur})
        
        return {"message": "Department head deleted successfully"}
        
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
