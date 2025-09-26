from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma

from app.db.prisma_client import get_prisma
from app.schemas.user import UserResponse, UserCreate
from app.schemas.university import DepartmentHeadCreate, DepartmentHeadResponse
from app.core.deps import require_admin, require_department_head
from app.core.security import hash_password

router = APIRouter(prefix="/admin/students", tags=["Admin - Student Management"])


@router.get("/", response_model=List[UserResponse])
async def get_all_students(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    specialty_id: Optional[str] = Query(None, description="Filter by specialty ID"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all students with optional filters (Admin only)"""
    try:
        # Build filter conditions
        where_conditions = {"role": "STUDENT"}
        
        # Add filters if provided
        if department_id:
            # Find students through their specialty's department
            where_conditions["specialty"] = {
                "departmentId": department_id
            }
        
        if specialty_id:
            where_conditions["specialtyId"] = specialty_id
            
        students = await prisma.student.find_many(
            where=where_conditions,
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
                "specialty": {
                    "include": {
                        "department": True
                    }
                },
                "level": True,
                "group": True
            }
        )
        
        # Transform the data to match UserResponse format
        result = []
        for student in students:
            user_data = student.user
            user_data.update({
                "studentInfo": {
                    "id": student.id,
                    "specialty": student.specialty.name if student.specialty else None,
                    "department": student.specialty.department.name if student.specialty and student.specialty.department else None,
                    "level": student.level.name if student.level else None,
                    "group": student.group.name if student.group else None
                }
            })
            result.append(user_data)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}", response_model=UserResponse)
async def get_student_by_id(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get student by ID (Admin only)"""
    try:
        student = await prisma.student.find_unique(
            where={"id": student_id},
            include={
                "user": True,
                "specialty": {
                    "include": {
                        "department": True
                    }
                },
                "level": True,
                "group": True
            }
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Transform the data
        user_data = student.user
        user_data.update({
            "studentInfo": {
                "id": student.id,
                "specialty": student.specialty.name if student.specialty else None,
                "department": student.specialty.department.name if student.specialty and student.specialty.department else None,
                "level": student.level.name if student.level else None,
                "group": student.group.name if student.group else None
            }
        })
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_student(
    user_data: UserCreate,
    specialty_id: Optional[str] = Query(None, description="Specialty ID for the student"),
    level_id: Optional[str] = Query(None, description="Level ID for the student"),
    group_id: Optional[str] = Query(None, description="Group ID for the student"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new student (Admin only)"""
    try:
        # Validate role
        if user_data.role != "STUDENT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role must be STUDENT"
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
        
        # Validate specialty if provided
        specialty = None
        if specialty_id:
            specialty = await prisma.specialty.find_unique(where={"id": specialty_id})
            if not specialty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Specialty not found"
                )
        
        # Validate level if provided
        level = None
        if level_id:
            level = await prisma.level.find_unique(where={"id": level_id})
            if not level:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Level not found"
                )
        
        # Validate group if provided
        group = None
        if group_id:
            group = await prisma.group.find_unique(where={"id": group_id})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found"
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
        
        # Create student record
        student_data = {
            "userId": new_user.id
        }
        
        if specialty_id:
            student_data["specialtyId"] = specialty_id
        if level_id:
            student_data["levelId"] = level_id
        if group_id:
            student_data["groupId"] = group_id
            
        await prisma.student.create(data=student_data)
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{student_id}")
async def update_student(
    student_id: str,
    specialty_id: Optional[str] = Query(None, description="New specialty ID"),
    level_id: Optional[str] = Query(None, description="New level ID"),
    group_id: Optional[str] = Query(None, description="New group ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update student information (Admin only)"""
    try:
        # Check if student exists
        student = await prisma.student.find_unique(where={"id": student_id})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Build update data
        update_data = {}
        
        if specialty_id:
            specialty = await prisma.specialty.find_unique(where={"id": specialty_id})
            if not specialty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Specialty not found"
                )
            update_data["specialtyId"] = specialty_id
            
        if level_id:
            level = await prisma.level.find_unique(where={"id": level_id})
            if not level:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Level not found"
                )
            update_data["levelId"] = level_id
            
        if group_id:
            group = await prisma.group.find_unique(where={"id": group_id})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found"
                )
            update_data["groupId"] = group_id
        
        if update_data:
            updated_student = await prisma.student.update(
                where={"id": student_id},
                data=update_data
            )
            return {"message": "Student updated successfully", "student": updated_student}
        else:
            return {"message": "No updates provided"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a student (Admin only)"""
    try:
        # Find student and get user ID
        student = await prisma.student.find_unique(where={"id": student_id})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        user_id = student.userId
        
        # Delete student record first (due to foreign key constraint)
        await prisma.student.delete(where={"id": student_id})
        
        # Delete associated user
        await prisma.user.delete(where={"id": user_id})
        
        return {"message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))