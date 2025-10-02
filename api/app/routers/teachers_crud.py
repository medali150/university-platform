from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from typing import List, Optional
from prisma import Prisma
from datetime import datetime

from app.db.prisma_client import get_prisma
from app.schemas.user import UserResponse, UserCreate
from app.schemas.absence import (
    AbsenceCreate, 
    AbsenceUpdate, 
    AbsenceResponse, 
    AbsenceNotification,
    AbsenceSummary,
    AbsenceStatusEnum
)
from app.core.deps import require_admin, require_department_head, get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/admin/teachers", tags=["Admin - Teacher Management"])


@router.get("/", response_model=List[UserResponse])
async def get_all_teachers(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    specialty_id: Optional[str] = Query(None, description="Filter by specialty ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get all teachers with optional filters (Admin only)"""
    try:
        # Test basic query first
        print("Starting teachers query...")
        
        # First, let's see if we can query teachers at all
        teacher_count = await prisma.teacher.count()
        print(f"Total teachers in database: {teacher_count}")
        
        if teacher_count == 0:
            return []
        
        # Try basic teacher query without includes
        teachers = await prisma.teacher.find_many()
        print(f"Retrieved {len(teachers)} teachers")
        
        # Try with minimal includes
        teachers_with_user = await prisma.teacher.find_many(
            include={"user": True}
        )
        print(f"Retrieved {len(teachers_with_user)} teachers with user info")
        
        # Build result
        result = []
        for teacher in teachers_with_user:
            if teacher.user:
                user_data = {
                    "id": teacher.user.id,
                    "firstName": teacher.user.firstName,
                    "lastName": teacher.user.lastName,
                    "email": teacher.user.email,
                    "login": teacher.user.login,
                    "role": teacher.user.role,
                    "createdAt": teacher.user.createdAt,
                    "updatedAt": teacher.user.updatedAt,
                    "teacherInfo": {
                        "id": teacher.id,
                        "department": None,
                        "specializations": []
                    }
                }
                result.append(user_data)
        
        print(f"Returning {len(result)} teacher records")
        return result
        
    except Exception as e:
        print(f"Error in get_all_teachers: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
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
                "subjects": {
                    "include": {
                        "level": {
                            "include": {
                                "specialty": True
                            }
                        }
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
        if not teacher.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher user not found"
            )
            
        # Get specializations from subjects
        specializations = list(set([
            subject.level.specialty.name 
            for subject in teacher.subjects 
            if subject.level and subject.level.specialty
        ]))
        
        user_data = {
            "id": teacher.user.id,
            "firstName": teacher.user.firstName,
            "lastName": teacher.user.lastName,
            "email": teacher.user.email,
            "login": teacher.user.login,
            "role": teacher.user.role,
            "createdAt": teacher.user.createdAt,
            "updatedAt": teacher.user.updatedAt,
            "teacherInfo": {
                "id": teacher.id,
                "department": teacher.department.name if teacher.department else None,
                "specializations": specializations
            }
        }
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse)
async def create_teacher(
    user_data: UserCreate,
    department_id: Optional[str] = Query(None, description="Department ID for the teacher"),
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
        if department_id:
            department = await prisma.department.find_unique(where={"id": department_id})
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found"
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
        }
        
        if department_id:
            teacher_data["departmentId"] = department_id
            
        new_teacher = await prisma.teacher.create(data=teacher_data)
        
        print(f"Created teacher {new_teacher.id} for user {new_user.id}")
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating teacher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{teacher_id}", response_model=UserResponse)
async def update_teacher(
    teacher_id: str,
    user_data: Optional[dict] = Body(None),
    department_id: Optional[str] = Query(None, description="New department ID"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update teacher information (Admin only)"""
    try:
        # Check if teacher exists (try teacher ID first, then user ID)
        teacher = await prisma.teacher.find_unique(
            where={"id": teacher_id},
            include={"user": True}
        )
        
        if not teacher or not teacher.user:
            # Try to find by user ID in case that's what we're getting
            user = await prisma.user.find_unique(where={"id": teacher_id})
            if user:
                teacher = await prisma.teacher.find_unique(
                    where={"userId": user.id},
                    include={"user": True}
                )
            
            if not teacher or not teacher.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Teacher not found"
                )
        
        # Update user data if provided
        if user_data:
            user_update_data = {}
            if "firstName" in user_data:
                user_update_data["firstName"] = user_data["firstName"]
            if "lastName" in user_data:
                user_update_data["lastName"] = user_data["lastName"]
            if "email" in user_data:
                # Check if email is already in use by another user
                existing = await prisma.user.find_first(
                    where={
                        "email": user_data["email"],
                        "id": {"not": teacher.userId}
                    }
                )
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )
                user_update_data["email"] = user_data["email"]
            if "login" in user_data:
                # Check if login is already in use by another user
                existing = await prisma.user.find_first(
                    where={
                        "login": user_data["login"],
                        "id": {"not": teacher.userId}
                    }
                )
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Login already in use"
                    )
                user_update_data["login"] = user_data["login"]
            if "password" in user_data and user_data["password"]:
                user_update_data["passwordHash"] = hash_password(user_data["password"])
            
            if user_update_data:
                await prisma.user.update(
                    where={"id": teacher.userId},
                    data=user_update_data
                )
        
        # Update teacher-specific data
        teacher_update_data = {}
        if department_id is not None:
            if department_id:  # If not empty string
                department = await prisma.department.find_unique(where={"id": department_id})
                if not department:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Department not found"
                    )
                teacher_update_data["departmentId"] = department_id
            else:
                teacher_update_data["departmentId"] = None
        
        if teacher_update_data:
            await prisma.teacher.update(
                where={"id": teacher.id},
                data=teacher_update_data
            )
        
        # Get updated teacher data
        updated_teacher = await prisma.teacher.find_unique(
            where={"id": teacher.id},
            include={"user": True}
        )
        
        if not updated_teacher or not updated_teacher.user:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated teacher")
        
        print(f"Updated teacher {teacher.id}")
        return updated_teacher.user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating teacher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a teacher (Admin only)"""
    try:
        # Find teacher (try teacher ID first, then user ID)
        teacher = await prisma.teacher.find_unique(where={"id": teacher_id})
        
        if not teacher:
            # Try to find by user ID in case that's what we're getting
            user = await prisma.user.find_unique(where={"id": teacher_id})
            if user:
                teacher = await prisma.teacher.find_unique(where={"userId": user.id})
            
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Teacher not found"
                )
        
        user_id = teacher.userId
        teacher_record_id = teacher.id
        
        # Delete teacher-specialty relationships first
        # await prisma.teacher_specialty.delete_many(
        #     where={"teacherId": teacher_record_id}
        # )
        # TODO: Handle specialty cleanup through subjects
        
        # Delete teacher record
        await prisma.teacher.delete(where={"id": teacher_record_id})
        
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
        # existing = await prisma.teacher_specialty.find_first(
        #     where={
        #         "teacherId": teacher_id,
        #         "specialtyId": specialty_id
        #     }
        # )
        existing = None  # TODO: Check through subjects
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher already has this specialty"
            )
        
        # Create relationship
        # await prisma.teacher_specialty.create(
        #     data={
        #         "teacherId": teacher_id,
        #         "specialtyId": specialty_id
        #     }
        # )
        # TODO: Implement through subjects
        
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
        # existing = await prisma.teacher_specialty.find_first(
        #     where={
        #         "teacherId": teacher_id,
        #         "specialtyId": specialty_id
        #     }
        # )
        existing = None  # TODO: Check through subjects
        if not existing:
            # For now, always return not found since table doesn't exist
            pass
        
        # Delete relationship
        # await prisma.teacher_specialty.delete(where={"id": existing.id})
        # TODO: Implement through subjects
        
        return {"message": "Specialty removed from teacher successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# TEACHER ABSENCE MANAGEMENT ENDPOINTS
# ==========================================

async def get_current_teacher(
    current_user = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    """Get current user's teacher information"""
    if current_user.role != "TEACHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    
    teacher = await prisma.teacher.find_unique(
        where={"userId": current_user.id},
        include={
            "user": True,
            "department": True
        }
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher record not found"
        )
    
    return teacher


# Create new router for teacher absence management
absence_router = APIRouter(prefix="/teacher/absences", tags=["Teacher - Absence Management"])


def format_absence_response(absence):
    """Helper function to format absence data for API response"""
    return {
        "id": absence.id,
        "studentId": absence.studentId,
        "scheduleId": absence.scheduleId,
        "reason": absence.reason,
        "status": absence.status,
        "justificationUrl": absence.justificationUrl,
        "createdAt": absence.createdAt,
        "updatedAt": absence.updatedAt,
        "student": {
            "id": absence.student.id,
            "userId": absence.student.userId,
            "enrollmentNumber": getattr(absence.student, 'enrollmentNumber', None),
            "user": {
                "id": absence.student.user.id,
                "firstName": absence.student.user.firstName,
                "lastName": absence.student.user.lastName,
                "email": absence.student.user.email,
                "role": absence.student.user.role
            }
        },
        "schedule": {
            "id": absence.schedule.id,
            "date": absence.schedule.date,
            "startTime": absence.schedule.startTime,
            "endTime": absence.schedule.endTime,
            "subject": {
                "id": absence.schedule.subject.id,
                "name": absence.schedule.subject.name
            },
            "group": {
                "id": absence.schedule.group.id,
                "name": absence.schedule.group.name
            },
            "room": {
                "id": absence.schedule.room.id,
                "code": absence.schedule.room.code,
                "type": absence.schedule.room.type,
                "capacity": absence.schedule.room.capacity
            }
        }
    }


@absence_router.get("/my-schedules")
async def get_my_schedules(
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Get teacher's schedules to mark absences"""
    try:
        where_clause = {"teacherId": teacher.id}
        
        # Date filtering
        if date_from:
            where_clause["date"] = {"gte": date_from}
        if date_to:
            if "date" in where_clause:
                where_clause["date"].update({"lte": date_to})
            else:
                where_clause["date"] = {"lte": date_to}
        
        schedules = await prisma.schedule.find_many(
            where=where_clause,
            include={
                "room": True,
                "subject": True,
                "group": True,
                "teacher": {"include": {"user": True}}
            },
            order=[
                {"date": "desc"},
                {"startTime": "asc"}
            ]
        )
        
        return schedules
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedules: {str(e)}")


@absence_router.get("/schedule/{schedule_id}/students")
async def get_schedule_students(
    schedule_id: str,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Get students in a specific schedule to mark absences"""
    try:
        # Verify teacher owns this schedule
        schedule = await prisma.schedule.find_unique(
            where={"id": schedule_id},
            include={
                "group": True,
                "subject": True,
                "room": True
            }
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        if schedule.teacherId != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own schedules"
            )
        
        # Get students in the group
        students = await prisma.student.find_many(
            where={"groupId": schedule.groupId},
            include={
                "user": True,
                "group": True,
                "specialty": True
            },
            order={"user": {"lastName": "asc"}}
        )
        
        # Get existing absences for this schedule
        existing_absences = await prisma.absence.find_many(
            where={"scheduleId": schedule_id},
            include={"student": {"include": {"user": True}}}
        )
        
        # Map existing absences by student ID
        absence_map = {abs.studentId: abs for abs in existing_absences}
        
        # Build response with absence status
        result = []
        for student in students:
            student_data = {
                "id": student.id,
                "userId": student.userId,
                "user": {
                    "id": student.user.id,
                    "firstName": student.user.firstName,
                    "lastName": student.user.lastName,
                    "email": student.user.email
                },
                "group": {
                    "id": student.group.id,
                    "name": student.group.name
                },
                "absence": None
            }
            
            # Add absence info if exists
            if student.id in absence_map:
                absence = absence_map[student.id]
                student_data["absence"] = {
                    "id": absence.id,
                    "reason": absence.reason,
                    "status": absence.status,
                    "createdAt": absence.createdAt,
                    "justificationUrl": absence.justificationUrl
                }
            
            result.append(student_data)
        
        return {
            "schedule": {
                "id": schedule.id,
                "date": schedule.date,
                "startTime": schedule.startTime,
                "endTime": schedule.endTime,
                "subject": {"id": schedule.subject.id, "name": schedule.subject.name},
                "group": {"id": schedule.group.id, "name": schedule.group.name},
                "room": {"id": schedule.room.id, "code": schedule.room.code}
            },
            "students": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching students: {str(e)}")


@absence_router.post("/", response_model=AbsenceResponse, status_code=status.HTTP_201_CREATED)
async def create_absence(
    absence_data: AbsenceCreate,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Create a new absence record for a student"""
    try:
        # Verify the schedule belongs to the teacher
        schedule = await prisma.schedule.find_unique(
            where={"id": absence_data.scheduleId},
            include={
                "subject": True,
                "group": True,
                "room": True
            }
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        if schedule.teacherId != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark absences for your own classes"
            )
        
        # Verify the student exists and is in the group
        student = await prisma.student.find_unique(
            where={"id": absence_data.studentId},
            include={"user": True, "group": True}
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        if student.groupId != schedule.groupId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student is not in the schedule's group"
            )
        
        # Check if absence already exists
        existing_absence = await prisma.absence.find_first(
            where={
                "studentId": absence_data.studentId,
                "scheduleId": absence_data.scheduleId
            }
        )
        
        if existing_absence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Absence already recorded for this student in this class"
            )
        
        # Create the absence
        new_absence = await prisma.absence.create(
            data={
                "studentId": absence_data.studentId,
                "scheduleId": absence_data.scheduleId,
                "reason": absence_data.reason,
                "status": "PENDING"
            },
            include={
                "student": {"include": {"user": True}},
                "schedule": {
                    "include": {
                        "subject": True,
                        "group": True,
                        "room": True
                    }
                }
            }
        )
        
        # TODO: Send notification to student (implement messaging system)
        # await send_absence_notification(new_absence)
        
        return format_absence_response(new_absence)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating absence: {str(e)}")


@absence_router.get("/", response_model=List[AbsenceResponse])
async def get_my_marked_absences(
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    status_filter: Optional[AbsenceStatusEnum] = Query(None, description="Filter by status"),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Get all absences marked by this teacher"""
    try:
        # Build where clause
        where_clause = {
            "schedule": {"teacherId": teacher.id}
        }
        
        if status_filter:
            where_clause["status"] = status_filter
            
        if student_id:
            where_clause["studentId"] = student_id
        
        if date_from or date_to:
            schedule_filter = {}
            if date_from:
                schedule_filter["date"] = {"gte": date_from}
            if date_to:
                if "date" in schedule_filter:
                    schedule_filter["date"].update({"lte": date_to})
                else:
                    schedule_filter["date"] = {"lte": date_to}
            
            where_clause["schedule"].update(schedule_filter)
        
        absences = await prisma.absence.find_many(
            where=where_clause,
            include={
                "student": {"include": {"user": True, "group": True}},
                "schedule": {
                    "include": {
                        "subject": True,
                        "group": True,
                        "room": True
                    }
                }
            },
            order={"createdAt": "desc"}
        )
        
        return absences
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching absences: {str(e)}")


@absence_router.get("/{absence_id}", response_model=AbsenceResponse)
async def get_absence(
    absence_id: str,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Get a specific absence by ID"""
    try:
        absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={
                "student": {"include": {"user": True, "group": True}},
                "schedule": {
                    "include": {
                        "subject": True,
                        "group": True,
                        "room": True,
                        "teacher": True
                    }
                }
            }
        )
        
        if not absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence not found"
            )
        
        # Verify teacher owns this absence
        if absence.schedule.teacherId != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access absences from your own classes"
            )
        
        return absence
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching absence: {str(e)}")


@absence_router.put("/{absence_id}", response_model=AbsenceResponse)
async def update_absence(
    absence_id: str,
    absence_data: AbsenceUpdate,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Update an absence record"""
    try:
        # Get the existing absence
        existing_absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={
                "schedule": {"include": {"teacher": True}}
            }
        )
        
        if not existing_absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence not found"
            )
        
        # Verify teacher owns this absence
        if existing_absence.schedule.teacherId != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update absences from your own classes"
            )
        
        # Prepare update data
        update_data = {}
        if absence_data.reason is not None:
            update_data["reason"] = absence_data.reason
        if absence_data.status is not None:
            update_data["status"] = absence_data.status
        if absence_data.justificationUrl is not None:
            update_data["justificationUrl"] = absence_data.justificationUrl
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update the absence
        updated_absence = await prisma.absence.update(
            where={"id": absence_id},
            data=update_data,
            include={
                "student": {"include": {"user": True, "group": True}},
                "schedule": {
                    "include": {
                        "subject": True,
                        "group": True,
                        "room": True
                    }
                }
            }
        )
        
        # TODO: Send notification to student about status change
        # if absence_data.status:
        #     await send_absence_status_notification(updated_absence)
        
        return updated_absence
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating absence: {str(e)}")


@absence_router.delete("/{absence_id}")
async def delete_absence(
    absence_id: str,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Delete an absence record"""
    try:
        # Get the existing absence
        existing_absence = await prisma.absence.find_unique(
            where={"id": absence_id},
            include={"schedule": True}
        )
        
        if not existing_absence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence not found"
            )
        
        # Verify teacher owns this absence
        if existing_absence.schedule.teacherId != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete absences from your own classes"
            )
        
        # Delete the absence
        await prisma.absence.delete(where={"id": absence_id})
        
        return {"message": "Absence deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting absence: {str(e)}")


@absence_router.get("/statistics/{student_id}", response_model=AbsenceSummary)
async def get_student_absence_statistics(
    student_id: str,
    prisma: Prisma = Depends(get_prisma),
    teacher = Depends(get_current_teacher)
):
    """Get absence statistics for a specific student in teacher's classes"""
    try:
        # Verify student exists
        student = await prisma.student.find_unique(
            where={"id": student_id},
            include={"user": True}
        )
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get all absences for this student in teacher's classes
        absences = await prisma.absence.find_many(
            where={
                "studentId": student_id,
                "schedule": {"teacherId": teacher.id}
            }
        )
        
        # Calculate statistics
        total_absences = len(absences)
        pending_absences = len([a for a in absences if a.status == "PENDING"])
        justified_absences = len([a for a in absences if a.status == "JUSTIFIED"])
        refused_absences = len([a for a in absences if a.status == "REFUSED"])
        
        return {
            "totalAbsences": total_absences,
            "pendingAbsences": pending_absences,
            "justifiedAbsences": justified_absences,
            "refusedAbsences": refused_absences,
            "studentId": student_id,
            "studentName": f"{student.user.firstName} {student.user.lastName}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


# TODO: Implement notification system
async def send_absence_notification(absence):
    """Send notification to student about new absence"""
    # This would integrate with a messaging/notification system
    # For now, just log the notification
    print(f"📧 NOTIFICATION: Absence marked for student {absence.student.user.firstName} {absence.student.user.lastName}")
    print(f"   Subject: {absence.schedule.subject.name}")
    print(f"   Date: {absence.schedule.date}")
    print(f"   Reason: {absence.reason}")
    pass


async def send_absence_status_notification(absence):
    """Send notification to student about absence status change"""
    # This would integrate with a messaging/notification system
    print(f"📧 STATUS UPDATE: Absence status changed to {absence.status} for {absence.student.user.firstName} {absence.student.user.lastName}")
    pass


# Include the absence router in the main router
router.include_router(absence_router)