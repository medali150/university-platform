from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from prisma import Prisma
from datetime import datetime, timedelta

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user

router = APIRouter(prefix="/department-head", tags=["Department Head Dashboard"])


@router.get("/statistics")
async def get_department_head_statistics(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get statistics for department head dashboard"""
    try:
        # Verify user is department head
        if current_user.role != "DEPARTMENT_HEAD":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Department head access required"
            )
        
        # Find the department head record to get their department
        dept_head = await prisma.departmenthead.find_unique(
            where={"userId": current_user.id},
            include={"department": True}
        )
        
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head record not found"
            )
        
        department_id = dept_head.departmentId
        department_name = dept_head.department.name
        
        # Get students count in the department (through specialties)
        students_count = await prisma.student.count(
            where={
                "specialty": {
                    "departmentId": department_id
                }
            }
        )
        
        # Get teachers count in the department
        teachers_count = await prisma.teacher.count(
            where={
                "departmentId": department_id
            }
        )
        
        # Get pending absences count for the department
        pending_absences = await prisma.absence.count(
            where={
                "status": "PENDING",
                "schedule": {
                    "teacher": {
                        "departmentId": department_id
                    }
                }
            }
        )
        
        # Get make-up requests count (assuming there's a makeup table)
        # For now, we'll simulate this or use a related count
        makeup_requests = 8  # Placeholder - adjust based on your schema
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_students = await prisma.student.count(
            where={
                "createdAt": {"gte": seven_days_ago},
                "specialty": {
                    "departmentId": department_id
                }
            }
        )
        
        # Calculate attendance rate (placeholder - adjust based on actual attendance schema)
        attendance_rate = 94.2
        
        # Calculate room utilization (placeholder)
        room_utilization = 87.5
        
        # Get scheduled hours (placeholder - adjust based on schedule schema)
        scheduled_hours = 1247
        
        # Get recent activity items
        recent_absences = await prisma.absence.find_many(
            where={
                "schedule": {
                    "teacher": {
                        "departmentId": department_id
                    }
                }
            },
            include={
                "student": {
                    "include": {"user": True}
                },
                "schedule": {
                    "include": {
                        "subject": True,
                        "teacher": {
                            "include": {"user": True}
                        }
                    }
                }
            },
            orderBy={"createdAt": "desc"},
            take=5
        )
        
        # Format recent activity
        activity_items = []
        for absence in recent_absences:
            activity_items.append({
                "type": "absence_request",
                "message": f"New absence request",
                "details": f"{absence.student.user.firstName} {absence.student.user.lastName} - {absence.schedule.subject.name}",
                "time": absence.createdAt.isoformat() if absence.createdAt else None
            })
        
        return {
            "department": {
                "id": department_id,
                "name": department_name
            },
            "overview": {
                "totalStudents": students_count,
                "activeTeachers": teachers_count,
                "pendingAbsences": pending_absences,
                "makeupRequests": makeup_requests
            },
            "performance": {
                "attendanceRate": attendance_rate,
                "roomUtilization": room_utilization,
                "scheduledHours": scheduled_hours,
                "makeupSessions": 23
            },
            "recentActivity": activity_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_department_head_statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/students")
async def get_department_students(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all students in the department head's department"""
    try:
        # Verify user is department head
        if current_user.role != "DEPARTMENT_HEAD":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Department head access required"
            )
        
        # Find the department head record to get their department
        dept_head = await prisma.departmenthead.find_unique(
            where={"userId": current_user.id},
            include={"department": True}
        )
        
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head record not found"
            )
        
        # Get students in the department
        students = await prisma.student.find_many(
            where={
                "specialty": {
                    "departmentId": dept_head.departmentId
                }
            },
            include={
                "user": True,
                "specialty": True,
                "level": True,
                "group": True
            }
        )
        
        # Format the response
        formatted_students = []
        for student in students:
            formatted_students.append({
                "id": student.user.id,
                "firstName": student.user.firstName,
                "lastName": student.user.lastName,
                "email": student.user.email,
                "role": student.user.role,
                "studentInfo": {
                    "id": student.id,
                    "specialty": student.specialty.name if student.specialty else None,
                    "level": student.level.name if student.level else None,
                    "group": student.group.name if student.group else None
                }
            })
        
        return formatted_students
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_department_students: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/teachers")
async def get_department_teachers(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all teachers in the department head's department"""
    try:
        # Verify user is department head
        if current_user.role != "DEPARTMENT_HEAD":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Department head access required"
            )
        
        # Find the department head record to get their department
        dept_head = await prisma.departmenthead.find_unique(
            where={"userId": current_user.id},
            include={"department": True}
        )
        
        if not dept_head:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department head record not found"
            )
        
        # Get teachers in the department
        teachers = await prisma.teacher.find_many(
            where={
                "departmentId": dept_head.departmentId
            },
            include={
                "user": True,
                "department": True
            }
        )
        
        # Format the response
        formatted_teachers = []
        for teacher in teachers:
            formatted_teachers.append({
                "id": teacher.user.id,
                "firstName": teacher.user.firstName,
                "lastName": teacher.user.lastName,
                "email": teacher.user.email,
                "role": teacher.user.role,
                "teacherInfo": {
                    "id": teacher.id,
                    "department": teacher.department.name if teacher.department else None
                }
            })
        
        return formatted_teachers
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_department_teachers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")