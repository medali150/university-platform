from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import require_admin

router = APIRouter(prefix="/admin/levels", tags=["Admin - Levels"])


@router.get("/")
async def get_levels(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in level name"),
    specialty_id: Optional[str] = Query(None, description="Filter by specialty ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all levels with pagination and filtering (Admin only)"""
    
    # Build where clause for filtering using direct relationship
    where_clause = {}
    if search:
        where_clause["nom"] = {"contains": search}
    if specialty_id:
        where_clause["id_specialite"] = specialty_id
    
    # Get total count
    total = await prisma.niveau.count(where=where_clause)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    # Get levels with relations
    levels = await prisma.niveau.find_many(
        where=where_clause,
        include={
            "specialite": {
                "include": {
                    "departement": True
                }
            }
        },
        skip=skip,
        take=page_size,
        order={"nom": "asc"}
    )
    
    return {
        "levels": [
            {
                "id": level.id,
                "name": level.nom,
                "specialty": {
                    "id": level.specialite.id,
                    "name": level.specialite.nom,
                    "department": {
                        "id": level.specialite.departement.id,
                        "name": level.specialite.departement.nom
                    } if level.specialite.departement else None
                } if level.specialite else None,
                "createdAt": level.createdAt.isoformat() if level.createdAt else None,
                "updatedAt": level.updatedAt.isoformat() if level.updatedAt else None
            }
            for level in levels
        ],
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages
    }


@router.get("/{level_id}/groups")
async def get_level_groups(
    level_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all groups for a specific level (Admin only)"""
    
    try:
        # Check if level exists
        level = await prisma.niveau.find_unique(where={"id": level_id})
        if not level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found"
            )
        
        # Get groups
        groups = await prisma.groupe.find_many(
            where={"id_niveau": level_id},
            include={
                "etudiants": True,
                "niveau": True
            },
            order={"nom": "asc"}
        )
        
        return {
            "success": True,
            "groups": [
                {
                    "id": group.id,
                    "nom": group.nom,
                    "id_niveau": group.id_niveau,
                    "niveau": {
                        "id": group.niveau.id,
                        "nom": group.niveau.nom
                    } if group.niveau else None,
                    "student_count": len(group.etudiants) if group.etudiants else 0
                }
                for group in groups
            ],
            "level": {
                "id": level.id,
                "nom": level.nom
            },
            "total": len(groups)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_level_groups: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch groups: {str(e)}"
        )
