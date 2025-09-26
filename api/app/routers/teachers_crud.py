from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.user import UserResponse, UserCreate
from app.core.deps import require_admin, require_department_head
from app.core.security import hash_password

router = APIRouter(prefix="/admin/teachers", tags=["Admin - Teacher Management"])


@router.get("/", response_model=List[UserResponse])
async def get_all_teachers(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    specialty_id: Optional[str] = Query(None, description="Filter by specialty ID"),
    academic_title: Optional[str] = Query(None, description="Filter by academic title"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all teachers with optional filters (Admin only)"""
    try:
        # Build filter conditions
        where_conditions = {"role": "TEACHER"}
        
        teachers = await prisma.teacher.find_many(
            where={},  # We'll filter through joins
            include={
                "user": {
                    "select": {
                        "id": True,
                        "firstName": True,
                        "lastName": True,
                        "email": True,
                        "login": True,
                        "role": True,
                        "createdAt": True,
                        "updatedAt": True
                    }
                },
                "department": True,
                "specialties": {
                    "include": {
                        "specialty": True
                    }
                }
            }
        )
        
        # Filter results based on query parameters
        filtered_teachers = []
        for teacher in teachers:
            include_teacher = True
            
            # Filter by department
            if department_id and teacher.departmentId != department_id:
                include_teacher = False
                
            # Filter by specialty
            if specialty_id and include_teacher:
                has_specialty = any(
                    ts.specialtyId == specialty_id 
                    for ts in teacher.specialties
                )
                if not has_specialty:
                    include_teacher = False
                    
            # Filter by academic title
            if academic_title and teacher.academicTitle != academic_title:
                include_teacher = False
                
            if include_teacher:
                filtered_teachers.append(teacher)
        
        # Transform the data to match UserResponse format
        result = []
        for teacher in filtered_teachers:
            user_data = teacher.user
            user_data.update({
                "teacherInfo": {
                    "id": teacher.id,
                    "department": teacher.department.name if teacher.department else None,
                    "academicTitle": teacher.academicTitle,
                    "specializations": [ts.specialty.name for ts in teacher.specialties],
                    "yearsOfExperience": teacher.yearsOfExperience
                }
            })
            result.append(user_data)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{teacher_id}", response_model=UserResponse)
async def get_teacher_by_id(
    teacher_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get teacher by ID (Admin only)"""
    try:
        teacher = await prisma.teacher.find_unique(
            where={"id": teacher_id},
            include={
                "user": True,
                "department": True,
                "specialties": {
                    "include": {
                        "specialty": True
                    }
                }
            }
        )
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Transform the data
        user_data = teacher.user
        user_data.update({
            "teacherInfo": {
                "id": teacher.id,
                "department": teacher.department.name if teacher.department else None,
                "academicTitle": teacher.academicTitle,
                "specializations": [ts.specialty.name for ts in teacher.specialties],
                "yearsOfExperience": teacher.yearsOfExperience
            }
        })
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_teacher(
    user_data: UserCreate,
    department_id: Optional[str] = Query(None, description="Department ID for the teacher"),
    academic_title: Optional[str] = Query(None, description="Academic title"),
    years_of_experience: Optional[int] = Query(0, description="Years of experience"),
    specialty_ids: Optional[List[str]] = Query([], description="Specialty IDs the teacher can teach"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new teacher (Admin only)"""
    try:
        # Validate role
        if user_data.role != "TEACHER":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role must be TEACHER"
            )
        
        # Check if user already exists
        existing_user = await prisma.user.find_first(
            where={
                "OR": [
                    {"email": user_data.email},
                    {"login": user_data.login}
                ]
            }
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or login already exists"
            )
        
        # Validate department if provided
        department = None
        if department_id:
            department = await prisma.department.find_unique(where={"id": department_id})
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found"
                )
        
        # Validate specialties if provided
        if specialty_ids:
            for specialty_id in specialty_ids:
                specialty = await prisma.specialty.find_unique(where={"id": specialty_id})
                if not specialty:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Specialty with ID {specialty_id} not found"
                    )
        
        # Create user first
        hashed_password = hash_password(user_data.password)
        new_user = await prisma.user.create(
            data={
                "firstName": user_data.firstName,
                "lastName": user_data.lastName,
                "email": user_data.email,
                "login": user_data.login,
                "passwordHash": hashed_password,
                "role": user_data.role
            }
        )
        
        # Create teacher record
        teacher_data = {
            "userId": new_user.id,
            "yearsOfExperience": years_of_experience or 0
        }
        
        if department_id:
            teacher_data["departmentId"] = department_id
        if academic_title:
            teacher_data["academicTitle"] = academic_title
            
        new_teacher = await prisma.teacher.create(data=teacher_data)
        
        # Create teacher-specialty relationships
        if specialty_ids:
            for specialty_id in specialty_ids:
                await prisma.teacherSpecialty.create(
                    data={
                        "teacherId": new_teacher.id,
                        "specialtyId": specialty_id
                    }
                )
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: str,
    department_id: Optional[str] = Query(None, description="New department ID"),
    academic_title: Optional[str] = Query(None, description="New academic title"),
    years_of_experience: Optional[int] = Query(None, description="New years of experience"),
    specialty_ids: Optional[List[str]] = Query(None, description="New specialty IDs"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update teacher information (Admin only)"""
    try:
        # Check if teacher exists
        teacher = await prisma.teacher.find_unique(where={"id": teacher_id})
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Build update data
        update_data = {}
        
        if department_id is not None:
            if department_id:  # If not empty string
                department = await prisma.department.find_unique(where={"id": department_id})
                if not department:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Department not found"
                    )
            update_data["departmentId"] = department_id if department_id else None
            
        if academic_title is not None:
            update_data["academicTitle"] = academic_title
            
        if years_of_experience is not None:
            update_data["yearsOfExperience"] = years_of_experience
        
        # Update teacher record
        if update_data:
            await prisma.teacher.update(
                where={"id": teacher_id},
                data=update_data
            )
        
        # Update specialties if provided
        if specialty_ids is not None:
            # Validate all specialties first
            for specialty_id in specialty_ids:
                specialty = await prisma.specialty.find_unique(where={"id": specialty_id})
                if not specialty:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Specialty with ID {specialty_id} not found"
                    )
            
            # Remove existing specialties
            await prisma.teacherSpecialty.delete_many(
                where={"teacherId": teacher_id}
            )
            
            # Add new specialties
            for specialty_id in specialty_ids:
                await prisma.teacherSpecialty.create(
                    data={
                        "teacherId": teacher_id,
                        "specialtyId": specialty_id
                    }
                )
        
        return {"message": "Teacher updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a teacher (Admin only)"""
    try:
        # Find teacher and get user ID
        teacher = await prisma.teacher.find_unique(where={"id": teacher_id})
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        user_id = teacher.userId
        
        # Delete teacher-specialty relationships first
        await prisma.teacherSpecialty.delete_many(
            where={"teacherId": teacher_id}
        )
        
        # Delete teacher record
        await prisma.teacher.delete(where={"id": teacher_id})
        
        # Delete associated user
        await prisma.user.delete(where={"id": user_id})
        
        return {"message": "Teacher deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{teacher_id}/specialties/{specialty_id}")
async def add_teacher_specialty(
    teacher_id: str,
    specialty_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Add a specialty to a teacher (Admin only)"""
    try:
        # Check if teacher exists
        teacher = await prisma.teacher.find_unique(where={"id": teacher_id})
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Check if specialty exists
        specialty = await prisma.specialty.find_unique(where={"id": specialty_id})
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        # Check if relationship already exists
        existing = await prisma.teacherSpecialty.find_first(
            where={
                "teacherId": teacher_id,
                "specialtyId": specialty_id
            }
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher already has this specialty"
            )
        
        # Create relationship
        await prisma.teacherSpecialty.create(
            data={
                "teacherId": teacher_id,
                "specialtyId": specialty_id
            }
        )
        
        return {"message": "Specialty added to teacher successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{teacher_id}/specialties/{specialty_id}")
async def remove_teacher_specialty(
    teacher_id: str,
    specialty_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Remove a specialty from a teacher (Admin only)"""
    try:
        # Check if relationship exists
        existing = await prisma.teacherSpecialty.find_first(
            where={
                "teacherId": teacher_id,
                "specialtyId": specialty_id
            }
        )
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher does not have this specialty"
            )
        
        # Delete relationship
        await prisma.teacherSpecialty.delete(where={"id": existing.id})
        
        return {"message": "Specialty removed from teacher successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))