from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.schemas.subject import (
    SubjectCreate, 
    SubjectUpdate, 
    SubjectResponse, 
    SubjectListResponse,
    SubjectDetailResponse
)
from app.core.deps import require_admin

router = APIRouter(prefix="/admin/subjects", tags=["Admin - Subjects"])


@router.get("/", response_model=SubjectListResponse)
async def get_subjects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in subject name"),
    level_id: Optional[str] = Query(None, description="Filter by level ID"),
    teacher_id: Optional[str] = Query(None, description="Filter by teacher ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all subjects with pagination and filtering (Admin only)"""
    
    # Build where clause for filtering
    where_clause = {}
    if search:
        where_clause["name"] = {"contains": search}
    if level_id:
        where_clause["levelId"] = level_id
    if teacher_id:
        where_clause["teacherId"] = teacher_id
    
    # Get total count
    total = await prisma.subject.count(where=where_clause)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    # Get subjects with relations
    subjects = await prisma.subject.find_many(
        where=where_clause,
        include={
            "level": {
                "include": {
                    "specialty": {
                        "include": {"department": True}
                    }
                }
            },
            "teacher": {
                "include": {"user": True, "department": True}
            }
        },
        skip=skip,
        take=page_size,
        order={"name": "asc"}
    )
    
    return SubjectListResponse(
        subjects=subjects,
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=total_pages
    )


@router.get("/{subject_id}", response_model=SubjectDetailResponse)
async def get_subject(
    subject_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a specific subject by ID (Admin only)"""
    subject = await prisma.subject.find_unique(
        where={"id": subject_id},
        include={
            "level": {
                "include": {
                    "specialty": {
                        "include": {"department": True}
                    }
                }
            },
            "teacher": {
                "include": {"user": True, "department": True}
            },
            "schedules": {
                "include": {
                    "room": True,
                    "group": True
                },
                "take": 10,
                "order": {"date": "desc"}
            }
        }
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return subject


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new subject (Admin only)"""
    
    # Verify that level exists
    level = await prisma.level.find_unique(where={"id": subject_data.levelId})
    if not level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level not found"
        )
    
    # Verify that teacher exists
    teacher = await prisma.teacher.find_unique(where={"id": subject_data.teacherId})
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher not found"
        )
    
    # Check if subject with same name already exists for this level
    existing_subject = await prisma.subject.find_first(
        where={
            "name": subject_data.name,
            "levelId": subject_data.levelId
        }
    )
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A subject with this name already exists for this level"
        )
    
    # Create the subject
    subject = await prisma.subject.create(
        data={
            "name": subject_data.name,
            "levelId": subject_data.levelId,
            "teacherId": subject_data.teacherId
        },
        include={
            "level": {
                "include": {
                    "specialty": {
                        "include": {"department": True}
                    }
                }
            },
            "teacher": {
                "include": {"user": True, "department": True}
            }
        }
    )
    
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    subject_data: SubjectUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a subject (Admin only)"""
    
    # Check if subject exists
    existing_subject = await prisma.subject.find_unique(where={"id": subject_id})
    if not existing_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Prepare update data
    update_data = {}
    
    # Validate and add fields to update
    if subject_data.name is not None:
        # Check for duplicate name in the same level
        level_id = subject_data.levelId if subject_data.levelId is not None else existing_subject.levelId
        duplicate = await prisma.subject.find_first(
            where={
                "name": subject_data.name,
                "levelId": level_id,
                "id": {"not": subject_id}
            }
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A subject with this name already exists for this level"
            )
        update_data["name"] = subject_data.name
    
    if subject_data.levelId is not None:
        # Verify that level exists
        level = await prisma.level.find_unique(where={"id": subject_data.levelId})
        if not level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Level not found"
            )
        update_data["levelId"] = subject_data.levelId
    
    if subject_data.teacherId is not None:
        # Verify that teacher exists
        teacher = await prisma.teacher.find_unique(where={"id": subject_data.teacherId})
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher not found"
            )
        update_data["teacherId"] = subject_data.teacherId
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    # Update the subject
    subject = await prisma.subject.update(
        where={"id": subject_id},
        data=update_data,
        include={
            "level": {
                "include": {
                    "specialty": {
                        "include": {"department": True}
                    }
                }
            },
            "teacher": {
                "include": {"user": True, "department": True}
            }
        }
    )
    
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a subject (Admin only)"""
    
    # Check if subject exists
    subject = await prisma.subject.find_unique(where={"id": subject_id})
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Check if subject has associated schedules
    schedule_count = await prisma.schedule.count(where={"subjectId": subject_id})
    if schedule_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete subject. It has {schedule_count} associated schedules. Please remove or reassign these schedules first."
        )
    
    # Delete the subject
    await prisma.subject.delete(where={"id": subject_id})
    
    return None


@router.get("/{subject_id}/schedules")
async def get_subject_schedules(
    subject_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all schedules for a specific subject (Admin only)"""
    
    # Check if subject exists
    subject = await prisma.subject.find_unique(where={"id": subject_id})
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Get total count
    total = await prisma.schedule.count(where={"subjectId": subject_id})
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size
    
    # Get schedules
    schedules = await prisma.schedule.find_many(
        where={"subjectId": subject_id},
        include={
            "room": True,
            "group": True,
            "teacher": {"include": {"user": True}},
            "absences": {"include": {"student": {"include": {"user": True}}}}
        },
        skip=skip,
        take=page_size,
        order={"date": "desc"}
    )
    
    return {
        "schedules": schedules,
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages,
        "subject": subject
    }


# Helper endpoints for frontend
@router.get("/helpers/levels")
async def get_levels_for_subjects(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all levels for subject creation (Admin only)"""
    levels = await prisma.level.find_many(
        include={
            "specialty": {
                "include": {"department": True}
            }
        },
        order={"name": "asc"}
    )
    return {"levels": levels}


@router.get("/helpers/teachers")
async def get_teachers_for_subjects(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all teachers for subject creation (Admin only)"""
    teachers = await prisma.teacher.find_many(
        include={
            "user": True,
            "department": True
        },
        order={"user": {"firstName": "asc"}}
    )
    return {"teachers": teachers}