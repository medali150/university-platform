from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.schemas.level import (
    LevelCreate, 
    LevelUpdate, 
    LevelResponse, 
    LevelListResponse,
    LevelDetailResponse
)
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
    
    # Build where clause for filtering
    where_clause = {}
    if search:
        where_clause["name"] = {"contains": search}
    if specialty_id:
        where_clause["specialtyId"] = specialty_id
    
    # Get total count
    total = await prisma.level.count(where=where_clause)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    # Get levels with relations
    levels = await prisma.level.find_many(
        where=where_clause,
        include={
            "specialty": {
                "include": {"department": True}
            }
        },
        skip=skip,
        take=page_size,
        order={"name": "asc"}
    )
    
    return {
        "levels": [
            {
                "id": level.id,
                "name": level.name,
                "specialtyId": level.specialtyId,
                "specialty": {
                    "id": level.specialty.id if level.specialty else None,
                    "name": level.specialty.name if level.specialty else None,
                    "department": {
                        "id": level.specialty.department.id if level.specialty and level.specialty.department else None,
                        "name": level.specialty.department.name if level.specialty and level.specialty.department else None
                    } if level.specialty and level.specialty.department else None
                } if level.specialty else None,
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


@router.get("/{level_id}", response_model=LevelDetailResponse)
async def get_level(
    level_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a specific level by ID (Admin only)"""
    level = await prisma.level.find_unique(
        where={"id": level_id},
        include={
            "specialty": {
                "include": {"department": True}
            },
            "groups": True,
            "subjects": {
                "include": {
                    "teacher": {
                        "include": {"user": True}
                    }
                }
            }
        }
    )
    
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )
    
    return level


@router.post("/", response_model=LevelResponse, status_code=status.HTTP_201_CREATED)
async def create_level(
    level_data: LevelCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new level (Admin only)"""
    
    # Verify that specialty exists
    specialty = await prisma.specialty.find_unique(where={"id": level_data.specialtyId})
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty not found"
        )
    
    # Check if level with same name already exists for this specialty
    existing_level = await prisma.level.find_first(
        where={
            "name": level_data.name,
            "specialtyId": level_data.specialtyId
        }
    )
    if existing_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A level with this name already exists for this specialty"
        )
    
    # Create the level
    level = await prisma.level.create(
        data={
            "name": level_data.name,
            "specialtyId": level_data.specialtyId
        },
        include={
            "specialty": {
                "include": {"department": True}
            }
        }
    )
    
    return level


@router.put("/{level_id}", response_model=LevelResponse)
async def update_level(
    level_id: str,
    level_data: LevelUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a level (Admin only)"""
    
    # Check if level exists
    existing_level = await prisma.level.find_unique(where={"id": level_id})
    if not existing_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )
    
    # Prepare update data
    update_data = {}
    
    # Validate and add fields to update
    if level_data.name is not None:
        # Check for duplicate name in the same specialty
        specialty_id = level_data.specialtyId if level_data.specialtyId is not None else existing_level.specialtyId
        duplicate = await prisma.level.find_first(
            where={
                "name": level_data.name,
                "specialtyId": specialty_id,
                "id": {"not": level_id}
            }
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A level with this name already exists for this specialty"
            )
        update_data["name"] = level_data.name
    
    if level_data.specialtyId is not None:
        # Verify that specialty exists
        specialty = await prisma.specialty.find_unique(where={"id": level_data.specialtyId})
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty not found"
            )
        update_data["specialtyId"] = level_data.specialtyId
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    # Update the level
    level = await prisma.level.update(
        where={"id": level_id},
        data=update_data,
        include={
            "specialty": {
                "include": {"department": True}
            }
        }
    )
    
    return level


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_level(
    level_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a level (Admin only)"""
    
    # Check if level exists
    level = await prisma.level.find_unique(where={"id": level_id})
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )
    
    # Check if level has associated groups
    group_count = await prisma.group.count(where={"levelId": level_id})
    if group_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete level. It has {group_count} associated groups. Please remove these groups first."
        )
    
    # Check if level has associated subjects
    subject_count = await prisma.subject.count(where={"levelId": level_id})
    if subject_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete level. It has {subject_count} associated subjects. Please remove these subjects first."
        )
    
    # Check if level has associated students
    student_count = await prisma.student.count(where={
        "group": {
            "levelId": level_id
        }
    })
    if student_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete level. It has {student_count} students in associated groups. Please move these students first."
        )
    
    # Delete the level
    await prisma.level.delete(where={"id": level_id})
    
    return None


@router.get("/{level_id}/subjects")
async def get_level_subjects(
    level_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all subjects for a specific level (Admin only)"""
    
    # Check if level exists
    level = await prisma.level.find_unique(where={"id": level_id})
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )
    
    # Get subjects
    subjects = await prisma.subject.find_many(
        where={"levelId": level_id},
        include={
            "teacher": {
                "include": {"user": True, "department": True}
            }
        },
        order={"name": "asc"}
    )
    
    return {
        "subjects": subjects,
        "level": level,
        "total": len(subjects)
    }


@router.get("/{level_id}/groups")
async def get_level_groups(
    level_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all groups for a specific level (Admin only)"""
    
    # Check if level exists
    level = await prisma.level.find_unique(where={"id": level_id})
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )
    
    # Get groups
    groups = await prisma.group.find_many(
        where={"levelId": level_id},
        include={
            "students": {
                "include": {"user": True}
            }
        },
        order={"name": "asc"}
    )
    
    return {
        "groups": groups,
        "level": level,
        "total": len(groups)
    }