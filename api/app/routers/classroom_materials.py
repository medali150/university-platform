"""
Smart Classroom - Course Materials API
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/api/classroom", tags=["Smart Classroom - Materials"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MaterialCreate(BaseModel):
    titre: str
    description: Optional[str] = None
    id_cours: str
    type: str  # document, video, lien, presentation
    contenu: Optional[str] = None  # URL or embedded content
    fichiers: Optional[dict] = None  # {name, url, size, type}
    estTelechargeableBoolean: bool = True
    ordre: int = 0


class MaterialUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    contenu: Optional[str] = None
    estTelechargeableBoolean: Optional[bool] = None
    ordre: Optional[int] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def check_teacher_permission(user, course_id: str, prisma: Prisma) -> bool:
    """Verify teacher owns the course"""
    if user.role != "TEACHER":
        return False
    
    course = await prisma.cours.find_unique(where={"id": course_id})
    return course and course.id_enseignant == user.enseignant_id


# ============================================================================
# MATERIALS CRUD
# ============================================================================

@router.post("/materials/upload", status_code=status.HTTP_201_CREATED)
async def upload_material_file(
    file: UploadFile = File(...),
    course_id: str = None,
    titre: str = None,
    description: str = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Upload a real file as course material (Teacher only)"""
    import os
    import shutil
    from pathlib import Path
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can upload materials")
    
    if not course_id:
        raise HTTPException(status_code=400, detail="course_id is required")
    
    try:
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, course_id, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission for this course")
        
        # Create uploads directory if not exists
        uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create material in database
        material = await prisma.materielcours.create(
            data={
                "titre": titre or file.filename,
                "description": description,
                "id_cours": course_id,
                "type": "document",
                "fichierUrl": f"/uploads/{unique_filename}",
                "fichierNom": file.filename,
                "fichierTaille": file_size,
                "fichierType": file.content_type,
                "estPublie": True,
                "estTelechargeable": True
            }
        )
        
        print(f"✅ File uploaded: {file.filename} ({file_size} bytes)")
        print(f"   Saved to: {file_path}")
        
        return material
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/materials", status_code=status.HTTP_201_CREATED)
async def create_material(
    material_data: MaterialCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Create course material (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can create materials")
    
    try:
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, material_data.id_cours, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission for this course")
        
        material = await prisma.materielcours.create(
            data=material_data.dict()
        )
        
        print(f"✅ Material created: {material.titre}")
        
        # TODO: If AI summarization is enabled, generate summary
        
        return material
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courses/{course_id}/materials")
async def get_course_materials(
    course_id: str,
    type: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get course materials"""
    
    try:
        where_clause = {"id_cours": course_id}
        if type:
            where_clause["type"] = type
        
        materials = await prisma.materielcours.find_many(
            where=where_clause,
            order={"ordre": "asc"}
        )
        
        return materials
        
    except Exception as e:
        print(f"❌ Error fetching materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials/{material_id}")
async def get_material(
    material_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get material details"""
    
    try:
        material = await prisma.materielcours.find_unique(
            where={"id": material_id},
            include={"cours": True}
        )
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Note: nbVues field doesn't exist in MaterielCours model
        # View count tracking removed
        
        return material
        
    except Exception as e:
        print(f"❌ Error fetching material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials/{material_id}/download")
async def download_material(
    material_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Download material file"""
    from fastapi.responses import FileResponse, RedirectResponse
    import os
    
    try:
        material = await prisma.materielcours.find_unique(
            where={"id": material_id}
        )
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # For external links, redirect
        if material.type == 'link' and material.lienExterne:
            return RedirectResponse(url=material.lienExterne)
        
        # For files
        if material.fichierUrl:
            # Check if file exists locally (for testing)
            # In production, this would download from S3/Azure Blob
            file_path = material.fichierUrl.replace('/uploads/', 'uploads/')
            
            if os.path.exists(file_path):
                return FileResponse(
                    path=file_path,
                    filename=material.fichierNom or material.titre,
                    media_type=material.fichierType or 'application/octet-stream'
                )
            else:
                # File stored remotely or doesn't exist
                raise HTTPException(
                    status_code=404, 
                    detail="File not found. In production, this would download from cloud storage."
                )
        
        raise HTTPException(status_code=400, detail="No downloadable content")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/materials/{material_id}")
async def update_material(
    material_id: str,
    material_data: MaterialUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Update material (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can update materials")
    
    try:
        material = await prisma.materielcours.find_unique(where={"id": material_id})
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, material.id_cours, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission")
        
        updated_material = await prisma.materielcours.update(
            where={"id": material_id},
            data=material_data.dict(exclude_unset=True)
        )
        
        print(f"✅ Material updated: {material_id}")
        return updated_material
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Delete material (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can delete materials")
    
    try:
        material = await prisma.materielcours.find_unique(where={"id": material_id})
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, material.id_cours, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission")
        
        # TODO: Delete associated files from S3/Azure Blob
        
        await prisma.materielcours.delete(where={"id": material_id})
        
        print(f"✅ Material deleted: {material_id}")
        return {"message": "Material deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FILE UPLOAD (Basic implementation - needs S3/Azure integration)
# ============================================================================

@router.post("/materials/upload")
async def upload_material_file(
    file: UploadFile = File(...),
    course_id: str = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """
    Upload file for material (Teacher only)
    
    TODO: Integrate with AWS S3 or Azure Blob Storage
    For now, returns placeholder URL
    """
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can upload files")
    
    try:
        # Validate file size (e.g., max 100MB)
        MAX_SIZE = 100 * 1024 * 1024  # 100MB
        contents = await file.read()
        
        if len(contents) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")
        
        # TODO: Upload to S3/Azure Blob
        # For now, return mock data
        file_info = {
            "name": file.filename,
            "size": len(contents),
            "type": file.content_type,
            "url": f"/uploads/materials/{course_id}/{file.filename}",  # Placeholder
            "uploadedAt": datetime.utcnow().isoformat()
        }
        
        print(f"✅ File uploaded: {file.filename} ({len(contents)} bytes)")
        
        return {
            "success": True,
            "file": file_info,
            "message": "File uploaded successfully (placeholder - integrate S3/Azure)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MATERIAL ANALYTICS
# ============================================================================

@router.get("/materials/{material_id}/stats")
async def get_material_stats(
    material_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get material analytics (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can view analytics")
    
    try:
        material = await prisma.materielcours.find_unique(
            where={"id": material_id},
            include={"cours": True}
        )
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, material.id_cours, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission")
        
        # Get enrolled students count
        enrollments = await prisma.inscriptioncours.count(
            where={
                "id_cours": material.id_cours,
                "statut": "active"
            }
        )
        
        stats = {
            "material_id": material_id,
            "title": material.titre,
            "type": material.type,
            "views": material.nbVues,
            "total_students": enrollments,
            "view_rate": round((material.nbVues / enrollments * 100) if enrollments > 0 else 0, 2),
            "created_at": material.createdAt,
            "last_viewed": material.updatedAt  # Simplified
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching material stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/courses/{course_id}/materials/reorder")
async def reorder_materials(
    course_id: str,
    material_orders: List[dict],  # [{"id": "...", "ordre": 1}, ...]
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Reorder course materials (Teacher only)"""
    
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Only teachers can reorder materials")
    
    try:
        # Verify course ownership
        has_permission = await check_teacher_permission(current_user, course_id, prisma)
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission")
        
        # Update orders
        for item in material_orders:
            await prisma.materielcours.update(
                where={"id": item["id"]},
                data={"ordre": item["ordre"]}
            )
        
        print(f"✅ Materials reordered for course {course_id}")
        return {"message": "Materials reordered successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error reordering materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))
