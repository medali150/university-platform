from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from prisma import Prisma
from datetime import datetime

from app.db.prisma_client import get_prisma
from app.schemas.user import UserResponse, UserCreate
from app.schemas.university import DepartmentResponse, DepartmentCreate
from app.core.deps import require_admin
from app.core.security import hash_password

router = APIRouter(prefix="/admin/department-heads", tags=["Admin - Department Head Management"])


@router.get("/", response_model=List[dict])
async def get_all_department_heads(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all department heads (Admin only)"""
    try:
        where_conditions = {}
        if department_id:
            where_conditions["departmentId"] = department_id
            
        department_heads = await prisma.departmentHead.find_many(
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
                "department": {
                    "select": {
                        "id": True,
                        "name": True,
                        "facultyId": True,
                        "faculty": {
                            "select": {
                                "name": True
                            }
                        }
                    }
                }
            }
        )
        
        # Transform the data
        result = []
        for dept_head in department_heads:
            user_data = dict(dept_head.user)
            user_data.update({
                "departmentHeadInfo": {
                    "id": dept_head.id,
                    "department": {
                        "id": dept_head.department.id,
                        "name": dept_head.department.name,
                        "faculty": dept_head.department.faculty.name if dept_head.department.faculty else None
                    },
                    "appointmentDate": dept_head.appointmentDate.isoformat() if dept_head.appointmentDate else None
                }
            })
            result.append(user_data)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dept_head_id}")
async def get_department_head_by_id(
    dept_head_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get department head by ID (Admin only)"""
    try:
        dept_head = await prisma.departmentHead.find_unique(
            where={"id": dept_head_id},
            include={
                "user": True,
                "department": {
                    "include": {
                        "faculty": True
                    }
                }
            }
        )
        
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head not found"
            )
        
        # Transform the data
        user_data = dict(dept_head.user)
        user_data.update({
            "departmentHeadInfo": {
                "id": dept_head.id,
                "department": {
                    "id": dept_head.department.id,
                    "name": dept_head.department.name,
                    "faculty": dept_head.department.faculty.name if dept_head.department.faculty else None
                },
                "appointmentDate": dept_head.appointmentDate.isoformat() if dept_head.appointmentDate else None
            }
        })
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_department_head(
    user_data: UserCreate,
    department_id: str = Query(..., description="Department ID to assign as head"),
    appointment_date: Optional[str] = Query(None, description="Appointment date (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create a new department head (Admin only)"""
    try:
        # Validate role
        if user_data.role != "DEPARTMENT_HEAD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role must be DEPARTMENT_HEAD"
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
        
        # Validate department
        department = await prisma.department.find_unique(where={"id": department_id})
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department already has a head
        existing_head = await prisma.departmentHead.find_first(
            where={"departmentId": department_id}
        )
        if existing_head:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department already has a head. Remove the current head first."
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
        
        # Create department head record
        dept_head_data = {
            "userId": new_user.id,
            "departmentId": department_id
        }
        
        if appointment_date:
            dept_head_data["appointmentDate"] = datetime.fromisoformat(appointment_date).date()
            
        await prisma.departmentHead.create(data=dept_head_data)
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dept_head_id}")
async def update_department_head(
    dept_head_id: str,
    department_id: Optional[str] = Query(None, description="New department ID"),
    appointment_date: Optional[str] = Query(None, description="New appointment date (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update department head information (Admin only)"""
    try:
        # Check if department head exists
        dept_head = await prisma.departmentHead.find_unique(where={"id": dept_head_id})
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head not found"
            )
        
        # Build update data
        update_data = {}
        
        if department_id:
            # Validate new department
            department = await prisma.department.find_unique(where={"id": department_id})
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found"
                )
            
            # Check if the new department already has a head (and it's not the current one)
            existing_head = await prisma.departmentHead.find_first(
                where={
                    "departmentId": department_id,
                    "id": {"not": dept_head_id}
                }
            )
            if existing_head:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department already has a different head"
                )
                
            update_data["departmentId"] = department_id
            
        if appointment_date:
            update_data["appointmentDate"] = datetime.fromisoformat(appointment_date).date()
        
        if update_data:
            updated_dept_head = await prisma.departmentHead.update(
                where={"id": dept_head_id},
                data=update_data
            )
            return {"message": "Department head updated successfully", "departmentHead": updated_dept_head}
        else:
            return {"message": "No updates provided"}
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
    """Delete a department head (Admin only)"""
    try:
        # Find department head and get user ID
        dept_head = await prisma.departmentHead.find_unique(where={"id": dept_head_id})
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head not found"
            )
        
        user_id = dept_head.userId
        
        # Delete department head record first
        await prisma.departmentHead.delete(where={"id": dept_head_id})
        
        # Delete associated user
        await prisma.user.delete(where={"id": user_id})
        
        return {"message": "Department head deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional endpoint to assign existing teacher as department head
@router.post("/assign-from-teacher/{teacher_id}")
async def assign_teacher_as_department_head(
    teacher_id: str,
    department_id: str = Query(..., description="Department ID to assign as head"),
    appointment_date: Optional[str] = Query(None, description="Appointment date (YYYY-MM-DD)"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Assign an existing teacher as department head (Admin only)"""
    try:
        # Find teacher
        teacher = await prisma.teacher.find_unique(
            where={"id": teacher_id},
            include={"user": True}
        )
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Validate department
        department = await prisma.department.find_unique(where={"id": department_id})
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department already has a head
        existing_head = await prisma.departmentHead.find_first(
            where={"departmentId": department_id}
        )
        if existing_head:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department already has a head"
            )
        
        # Check if teacher is already a department head
        existing_teacher_head = await prisma.departmentHead.find_first(
            where={"userId": teacher.userId}
        )
        if existing_teacher_head:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher is already a department head"
            )
        
        # Update user role to DEPARTMENT_HEAD
        await prisma.user.update(
            where={"id": teacher.userId},
            data={"role": "DEPARTMENT_HEAD"}
        )
        
        # Create department head record
        dept_head_data = {
            "userId": teacher.userId,
            "departmentId": department_id
        }
        
        if appointment_date:
            dept_head_data["appointmentDate"] = datetime.fromisoformat(appointment_date).date()
            
        new_dept_head = await prisma.departmentHead.create(data=dept_head_data)
        
        return {
            "message": "Teacher assigned as department head successfully",
            "departmentHead": new_dept_head
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to remove department head role (convert back to teacher)
@router.post("/{dept_head_id}/demote-to-teacher")
async def demote_department_head_to_teacher(
    dept_head_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Demote department head back to teacher role (Admin only)"""
    try:
        # Find department head
        dept_head = await prisma.departmentHead.find_unique(
            where={"id": dept_head_id},
            include={"user": True}
        )
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head not found"
            )
        
        user_id = dept_head.userId
        
        # Check if user still has teacher record
        teacher = await prisma.teacher.find_first(where={"userId": user_id})
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote: User does not have teacher record"
            )
        
        # Delete department head record
        await prisma.departmentHead.delete(where={"id": dept_head_id})
        
        # Update user role back to TEACHER
        await prisma.user.update(
            where={"id": user_id},
            data={"role": "TEACHER"}
        )
        
        return {"message": "Department head demoted to teacher successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))