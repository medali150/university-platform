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
        # Build filter conditions for Student model
        where_conditions = {}
        
        # Add filters if provided
        if department_id:
            # Find students through their specialty's department
            where_conditions["specialty"] = {
                "departmentId": department_id
            }
        
        if specialty_id:
            where_conditions["specialtyId"] = specialty_id
            
        students = await prisma.etudiant.find_many(
            where=where_conditions,
            include={
                "user": True,
                "specialty": {
                    "include": {
                        "department": True
                    }
                },
                "group": {
                    "include": {
                        "level": True
                    }
                }
            }
        )
        
        # Transform the data to match UserResponse format
        result = []
        for student in students:
            if student.user:
                user_data = {
                    "id": student.user.id,  # User ID
                    "studentRecordId": student.id,  # Student record ID (THIS is what we need for delete)
                    "firstName": student.user.firstName,
                    "lastName": student.user.lastName,
                    "email": student.user.email,
                    "login": student.user.login,
                    "role": student.user.role,
                    "createdAt": student.user.createdAt,
                    "updatedAt": student.user.updatedAt,
                    "studentInfo": {
                        "id": student.id,  # Also in nested object for compatibility
                        "specialty": student.specialty.name if student.specialty else None,
                        "specialtyId": student.specialtyId if student.specialtyId else None,
                        "department": student.specialty.department.name if student.specialty and student.specialty.department else None,
                        "level": student.group.level.name if student.group and student.group.level else None,
                        "levelId": student.group.levelId if student.group and student.group.levelId else None,
                        "group": student.group.name if student.group else None,
                        "groupId": student.groupId if student.groupId else None
                    }
                }
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
        student = await prisma.etudiant.find_unique(
            where={"id": student_id},
            include={
                "user": True,
                "specialty": {
                    "include": {
                        "department": True
                    }
                },
                "group": {
                    "include": {
                        "level": True
                    }
                }
            }
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Transform the data
        if not student.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student user data not found"
            )
            
        user_data = {
            "id": student.user.id,
            "firstName": student.user.firstName,
            "lastName": student.user.lastName,
            "email": student.user.email,
            "login": student.user.login,
            "role": student.user.role,
            "createdAt": student.user.createdAt,
            "updatedAt": student.user.updatedAt,
            "studentInfo": {
                "id": student.id,
                "specialty": student.specialty.name if student.specialty else None,
                "department": student.specialty.department.name if student.specialty and student.specialty.department else None,
                "level": student.group.level.name if student.group and student.group.level else None,
                "group": student.group.name if student.group else None
            }
        }
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_student(
    user_data: UserCreate,
    specialty_id: Optional[str] = Query(None, description="Specialty ID for the student"),
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
        existing_user = await prisma.utilisateur.find_first(
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
            specialty = await prisma.specialite.find_unique(where={"id": specialty_id})
            if not specialty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Specialty not found"
                )
        
        # Validate group if provided
        group = None
        if group_id:
            group = await prisma.groupe.find_unique(where={"id": group_id})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found"
                )
        
        # Create user first
        hashed_password = hash_password(user_data.password)
        new_user = await prisma.utilisateur.create(
            data={
                "firstName": user_data.firstName,
                "lastName": user_data.lastName,
                "email": user_data.email,
                "login": user_data.login,
                "passwordHash": hashed_password,
                "role": user_data.role
            }
        )
        
        # Create student record - both groupId and specialtyId are required according to schema
        if not specialty_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty ID is required for student creation"
            )
        
        if not group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group ID is required for student creation"
            )
            
        student_data = {
            "userId": new_user.id,
            "specialtyId": specialty_id,
            "groupId": group_id
        }
            
        await prisma.etudiant.create(data=student_data)
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{student_id}")
async def update_student(
    student_id: str,
    specialty_id: Optional[str] = Query(None, description="New specialty ID"),
    group_id: Optional[str] = Query(None, description="New group ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update student information (Admin only)"""
    try:
        print(f"=== UPDATE STUDENT DEBUG ===")
        print(f"Received student_id: {student_id}")
        
        # Find student record by student.id (not user.id)
        student = await prisma.etudiant.find_unique(where={"id": student_id})
        
        if not student:
            print(f"No student found with student.id: {student_id}")
            
            # Maybe they sent user.id instead of student.id - try to find by userId
            print("Trying to find student by userId...")
            student = await prisma.etudiant.find_first(where={"userId": student_id})
            
            if student:
                print(f"Found student by userId: {student.id}")
                student_id = student.id  # Use correct student.id for update
            else:
                print("No student found by userId either")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found with ID: {student_id}"
                )
        
        # Build update data
        update_data = {}
        
        if specialty_id:
            specialty = await prisma.specialite.find_unique(where={"id": specialty_id})
            if not specialty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Specialty not found"
                )
            update_data["specialtyId"] = specialty_id
            
        if group_id:
            group = await prisma.groupe.find_unique(where={"id": group_id})
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Group not found"
                )
            update_data["groupId"] = group_id
        
        if update_data:
            updated_student = await prisma.etudiant.update(
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
        print(f"=== DELETE STUDENT DEBUG ===")
        print(f"Received student_id: {student_id}")
        
        # Find student record by student.id (not user.id)
        student = await prisma.etudiant.find_unique(
            where={"id": student_id},
            include={"user": True}
        )
        
        if not student:
            print(f"No student found with student.id: {student_id}")
            
            # Maybe they sent user.id instead of student.id - try to find by userId
            print("Trying to find student by userId...")
            student = await prisma.etudiant.find_first(
                where={"userId": student_id},
                include={"user": True}
            )
            
            if student:
                print(f"Found student by userId: {student.id}")
                student_id = student.id  # Use correct student.id for deletion
            else:
                print("No student found by userId either")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found with ID: {student_id}"
                )
        
        user_id = student.userId
        print(f"Will delete student.id: {student.id} and user.id: {user_id}")
        
        # Delete student record first (due to foreign key constraint)
        await prisma.etudiant.delete(where={"id": student.id})
        print(f"Deleted student record: {student.id}")
        
        # Delete associated user
        await prisma.utilisateur.delete(where={"id": user_id})
        print(f"Deleted user record: {user_id}")
        
        return {"message": "Student deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting student: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))