from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from prisma import Prisma
from datetime import datetime, timedelta

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_department_head, require_student, require_student
from app.schemas.schedule import (
    ScheduleCreate, 
    ScheduleUpdate, 
    ScheduleResponse, 
    ScheduleConflictError,
    DepartmentAuthError,
    ConflictInfo
)

router = APIRouter(prefix="/schedules", tags=["Schedules"])


async def get_current_department_head(
    current_user = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    """Get current user's department head information"""
    if current_user.role not in ["DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Department Head or Admin access required"
        )
    
    if current_user.role == "ADMIN":
        # Admin can manage all departments, return None to indicate no restriction
        return None
    
    dept_head = await prisma.departmenthead.find_unique(
        where={"userId": current_user.id},
        include={"department": True}
    )
    
    if not dept_head:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department Head record not found"
        )
    
    return dept_head


async def verify_department_ownership(
    subject_id: str,
    group_id: str,
    teacher_id: str,
    room_id: str,
    dept_head,
    prisma: Prisma
) -> dict:
    """
    Verify that subject, group, and teacher belong to the department head's department.
    Returns the entities if valid, raises HTTPException if not.
    """
    # Get all entities with department information
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
                "include": {"department": True}
            }
        }
    )
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    
    group = await prisma.group.find_unique(
        where={"id": group_id},
        include={
            "level": {
                "include": {
                    "specialty": {
                        "include": {"department": True}
                    }
                }
            }
        }
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    
    teacher = await prisma.teacher.find_unique(
        where={"id": teacher_id},
        include={"department": True, "user": True}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found"
        )
    
    room = await prisma.room.find_unique(where={"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # If admin, skip department checks
    if dept_head is None:
        return {
            "subject": subject,
            "group": group,
            "teacher": teacher,
            "room": room
        }
    
    # Verify department ownership
    dept_id = dept_head.departmentId
    
    # Check if subject belongs to department (through specialty)
    if subject.level.specialty.departmentId != dept_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Subject '{subject.name}' does not belong to your department"
        )
    
    # Check if group belongs to department (through specialty)
    if group.level.specialty.departmentId != dept_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Group '{group.name}' does not belong to your department"
        )
    
    # Check if teacher belongs to department
    if teacher.departmentId != dept_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Teacher '{teacher.user.firstName} {teacher.user.lastName}' does not belong to your department"
        )
    
    # Verify subject is taught by the specified teacher
    if subject.teacherId != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject '{subject.name}' is not taught by the specified teacher"
        )
    
    return {
        "subject": subject,
        "group": group,
        "teacher": teacher,
        "room": room
    }


async def check_schedule_conflicts(
    date: datetime,
    start_time: datetime,
    end_time: datetime,
    room_id: str,
    teacher_id: str,
    group_id: str,
    prisma: Prisma,
    exclude_schedule_id: Optional[str] = None
) -> List[ConflictInfo]:
    """
    Check for schedule conflicts with room, teacher, or group.
    Returns list of conflicts found.
    """
    conflicts = []
    
    # Build where clause for overlapping schedules
    # Convert datetime to date for comparison, but keep it as datetime for Prisma
    schedule_date = datetime.combine(date.date(), datetime.min.time())
    next_day = schedule_date + timedelta(days=1)
    
    overlap_conditions = {
        "date": {
            "gte": schedule_date,
            "lt": next_day
        },
        "status": {"not": "CANCELED"},  # Don't consider canceled schedules
        "OR": [
            # New schedule starts during existing schedule
            {
                "AND": [
                    {"startTime": {"lte": start_time}},
                    {"endTime": {"gt": start_time}}
                ]
            },
            # New schedule ends during existing schedule
            {
                "AND": [
                    {"startTime": {"lt": end_time}},
                    {"endTime": {"gte": end_time}}
                ]
            },
            # New schedule completely contains existing schedule
            {
                "AND": [
                    {"startTime": {"gte": start_time}},
                    {"endTime": {"lte": end_time}}
                ]
            }
        ]
    }
    
    # If updating, exclude the current schedule from conflict check
    if exclude_schedule_id:
        overlap_conditions["NOT"] = {"id": exclude_schedule_id}
    
    # Check room conflicts
    room_conflicts = await prisma.schedule.find_many(
        where={
            **overlap_conditions,
            "roomId": room_id
        },
        include={
            "subject": True,
            "teacher": {"include": {"user": True}},
            "group": True,
            "room": True
        }
    )
    
    for conflict in room_conflicts:
        conflicts.append(ConflictInfo(
            type="room",
            conflictingScheduleId=conflict.id,
            message=f"Room {conflict.room.code} is already booked from {conflict.startTime.strftime('%H:%M')} to {conflict.endTime.strftime('%H:%M')} for {conflict.subject.name} with {conflict.group.name}"
        ))
    
    # Check teacher conflicts
    teacher_conflicts = await prisma.schedule.find_many(
        where={
            **overlap_conditions,
            "teacherId": teacher_id
        },
        include={
            "subject": True,
            "teacher": {"include": {"user": True}},
            "group": True,
            "room": True
        }
    )
    
    for conflict in teacher_conflicts:
        conflicts.append(ConflictInfo(
            type="teacher",
            conflictingScheduleId=conflict.id,
            message=f"Teacher {conflict.teacher.user.firstName} {conflict.teacher.user.lastName} is already scheduled from {conflict.startTime.strftime('%H:%M')} to {conflict.endTime.strftime('%H:%M')} for {conflict.subject.name} in room {conflict.room.code}"
        ))
    
    # Check group conflicts
    group_conflicts = await prisma.schedule.find_many(
        where={
            **overlap_conditions,
            "groupId": group_id
        },
        include={
            "subject": True,
            "teacher": {"include": {"user": True}},
            "group": True,
            "room": True
        }
    )
    
    for conflict in group_conflicts:
        conflicts.append(ConflictInfo(
            type="group",
            conflictingScheduleId=conflict.id,
            message=f"Group {conflict.group.name} is already scheduled from {conflict.startTime.strftime('%H:%M')} to {conflict.endTime.strftime('%H:%M')} for {conflict.subject.name} in room {conflict.room.code}"
        ))
    
    return conflicts


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """
    Create a new schedule. 
    DEPARTMENT_HEAD can only create schedules for their own department.
    ADMIN can create schedules for any department.
    """
    # Verify department ownership and get entities
    entities = await verify_department_ownership(
        schedule_data.subjectId,
        schedule_data.groupId,
        schedule_data.teacherId,
        schedule_data.roomId,
        dept_head,
        prisma
    )
    
    # Check for schedule conflicts
    conflicts = await check_schedule_conflicts(
        schedule_data.date,
        schedule_data.startTime,
        schedule_data.endTime,
        schedule_data.roomId,
        schedule_data.teacherId,
        schedule_data.groupId,
        prisma
    )
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Schedule conflict detected",
                "conflicts": [conflict.dict() for conflict in conflicts]
            }
        )
    
    # Create the schedule
    new_schedule = await prisma.schedule.create(
        data={
            "date": schedule_data.date,
            "startTime": schedule_data.startTime,
            "endTime": schedule_data.endTime,
            "roomId": schedule_data.roomId,
            "subjectId": schedule_data.subjectId,
            "groupId": schedule_data.groupId,
            "teacherId": schedule_data.teacherId,
            "status": schedule_data.status
        },
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        }
    )
    
    return new_schedule


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """
    Update an existing schedule.
    DEPARTMENT_HEAD can only update schedules that belong to their department.
    ADMIN can update any schedule.
    """
    # Get existing schedule with department information
    existing_schedule = await prisma.schedule.find_unique(
        where={"id": schedule_id},
        include={
            "room": True,
            "subject": {
                "include": {
                    "level": {
                        "include": {
                            "specialty": {
                                "include": {"department": True}
                            }
                        }
                    },
                    "teacher": {"include": {"department": True}}
                }
            },
            "group": {
                "include": {
                    "level": {
                        "include": {
                            "specialty": {
                                "include": {"department": True}
                            }
                        }
                    }
                }
            },
            "teacher": {"include": {"department": True, "user": True}}
        }
    )
    
    if not existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    
    # Check department ownership for non-admin users
    if dept_head is not None:
        dept_id = dept_head.departmentId
        schedule_dept_id = existing_schedule.subject.level.specialty.departmentId
        
        if schedule_dept_id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify schedules in your own department"
            )
    
    # Prepare update data with only provided fields
    update_data = {}
    
    # If any resource IDs are being updated, verify ownership
    if any([schedule_data.subjectId, schedule_data.groupId, schedule_data.teacherId, schedule_data.roomId]):
        # Use existing values for unspecified fields
        subject_id = schedule_data.subjectId or existing_schedule.subjectId
        group_id = schedule_data.groupId or existing_schedule.groupId
        teacher_id = schedule_data.teacherId or existing_schedule.teacherId
        room_id = schedule_data.roomId or existing_schedule.roomId
        
        # Verify department ownership for new resources
        entities = await verify_department_ownership(
            subject_id, group_id, teacher_id, room_id, dept_head, prisma
        )
        
        if schedule_data.subjectId:
            update_data["subjectId"] = schedule_data.subjectId
        if schedule_data.groupId:
            update_data["groupId"] = schedule_data.groupId
        if schedule_data.teacherId:
            update_data["teacherId"] = schedule_data.teacherId
        if schedule_data.roomId:
            update_data["roomId"] = schedule_data.roomId
    
    # Update time and date fields
    if schedule_data.date is not None:
        update_data["date"] = schedule_data.date
    if schedule_data.startTime is not None:
        update_data["startTime"] = schedule_data.startTime
    if schedule_data.endTime is not None:
        update_data["endTime"] = schedule_data.endTime
    if schedule_data.status is not None:
        update_data["status"] = schedule_data.status
    
    # Check for conflicts if time, date, or resources are being updated
    if any(field in update_data for field in ["date", "startTime", "endTime", "roomId", "teacherId", "groupId"]):
        # Use updated values or existing ones
        check_date = update_data.get("date", existing_schedule.date)
        check_start = update_data.get("startTime", existing_schedule.startTime)
        check_end = update_data.get("endTime", existing_schedule.endTime)
        check_room = update_data.get("roomId", existing_schedule.roomId)
        check_teacher = update_data.get("teacherId", existing_schedule.teacherId)
        check_group = update_data.get("groupId", existing_schedule.groupId)
        
        conflicts = await check_schedule_conflicts(
            check_date,
            check_start,
            check_end,
            check_room,
            check_teacher,
            check_group,
            prisma,
            exclude_schedule_id=schedule_id
        )
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Schedule conflict detected",
                    "conflicts": [conflict.dict() for conflict in conflicts]
                }
            )
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update the schedule
    updated_schedule = await prisma.schedule.update(
        where={"id": schedule_id},
        data=update_data,
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        }
    )
    
    return updated_schedule


@router.get("/department", response_model=List[ScheduleResponse])
async def get_department_schedules(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """
    Get all schedules for the department head's department.
    ADMIN can see all schedules.
    """
    where_clause = {}
    
    # Date filtering
    if date_from:
        where_clause["date"] = {"gte": date_from}
    if date_to:
        if "date" in where_clause:
            where_clause["date"].update({"lte": date_to})
        else:
            where_clause["date"] = {"lte": date_to}
    
    # Department filtering for non-admin users
    if dept_head is not None:
        where_clause["subject"] = {
            "level": {
                "specialty": {
                    "departmentId": dept_head.departmentId
                }
            }
        }
    
    schedules = await prisma.schedule.find_many(
        where=where_clause,
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        },
        order_by=[
            {"date": "asc"},
            {"startTime": "asc"}
        ]
    )
    
    return schedules


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get a specific schedule by ID"""
    schedule = await prisma.schedule.find_unique(
        where={"id": schedule_id},
        include={
            "room": True,
            "subject": {
                "include": {
                    "level": {
                        "include": {
                            "specialty": {
                                "include": {"department": True}
                            }
                        }
                    }
                }
            },
            "group": True,
            "teacher": {"include": {"user": True}}
        }
    )
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    
    # Check department ownership for non-admin users
    if dept_head is not None:
        dept_id = dept_head.departmentId
        schedule_dept_id = schedule.subject.level.specialty.departmentId
        
        if schedule_dept_id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view schedules in your own department"
            )
    
    return schedule


# ====================
# STUDENT SCHEDULE ENDPOINTS  
# ====================

async def get_current_student(
    current_user = Depends(get_current_user),
    prisma: Prisma = Depends(get_prisma)
):
    """Get current user's student information"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    
    student = await prisma.student.find_unique(
        where={"userId": current_user.id},
        include={
            "user": True,
            "group": {
                "include": {
                    "level": {
                        "include": {
                            "specialty": {
                                "include": {"department": True}
                            }
                        }
                    }
                }
            },
            "specialty": {
                "include": {"department": True}
            }
        }
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student record not found"
        )
    
    return student


@router.get("/student/my-schedule", response_model=List[ScheduleResponse])
async def get_my_schedule(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    prisma: Prisma = Depends(get_prisma),
    student = Depends(get_current_student)
):
    """Get current student's schedule"""
    where_clause = {
        "groupId": student.groupId,
        "status": {"not": "CANCELED"}  # Don't show canceled classes
    }
    
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
        order_by=[
            {"date": "asc"},
            {"startTime": "asc"}
        ]
    )
    
    return schedules


from datetime import date as date_type

@router.get("/student/weekly-timetable")
async def get_weekly_timetable(
    week_start: Optional[date_type] = None,
    prisma: Prisma = Depends(get_prisma),
    student = Depends(get_current_student)
):
    """Get student's weekly timetable in grid format like the image"""
    
    # If no week specified, use current week
    if not week_start:
        today = date_type.today()
        # Get Monday of current week (0=Monday, 6=Sunday)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
    
    week_end = week_start + timedelta(days=6)  # Sunday
    
    # Get all schedules for the week
    schedules = await prisma.schedule.find_many(
        where={
            "groupId": student.groupId,
            "date": {
                "gte": datetime.combine(week_start, datetime.min.time()),
                "lte": datetime.combine(week_end, datetime.max.time())
            },
            "status": {"not": "CANCELED"}
        },
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        },
        order_by=[
            {"date": "asc"},
            {"startTime": "asc"}
        ]
    )
    
    # Create timetable grid
    timetable = {
        "weekStart": week_start.isoformat(),
        "weekEnd": week_end.isoformat(),
        "studentInfo": {
            "name": f"{student.user.firstName} {student.user.lastName}" if student.user else "Student",
            "group": student.group.name if student.group else None,
            "level": student.group.level.name if student.group and student.group.level else None,
            "specialty": student.specialty.name if student.specialty else None,
            "department": student.specialty.department.name if student.specialty and student.specialty.department else None
        },
        "days": {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": []
        }
    }
    
    # Map day names
    day_mapping = {
        0: "monday",
        1: "tuesday", 
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday"
    }
    
    # Organize schedules by day
    for schedule in schedules:
        day_of_week = schedule.date.weekday()
        if day_of_week in day_mapping:
            day_name = day_mapping[day_of_week]
            
            schedule_info = {
                "id": schedule.id,
                "subject": schedule.subject.name,
                "teacher": f"{schedule.teacher.user.firstName} {schedule.teacher.user.lastName}",
                "room": schedule.room.code,
                "startTime": schedule.startTime.strftime("%H:%M"),
                "endTime": schedule.endTime.strftime("%H:%M"),
                "timeSlot": f"{schedule.startTime.strftime('%H:%M')} - {schedule.endTime.strftime('%H:%M')}",
                "status": schedule.status,
                "date": schedule.date.isoformat()
            }
            
            timetable["days"][day_name].append(schedule_info)
    
    # Sort each day by start time
    for day in timetable["days"]:
        timetable["days"][day].sort(key=lambda x: x["startTime"])
    
    return timetable


@router.get("/student/today-schedule", response_model=List[ScheduleResponse])
async def get_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    student = Depends(get_current_student)
):
    """Get student's schedule for today"""
    today = datetime.now().date()
    
    schedules = await prisma.schedule.find_many(
        where={
            "groupId": student.groupId,
            "date": {
                "gte": datetime.combine(today, datetime.min.time()),
                "lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
            },
            "status": {"not": "CANCELED"}
        },
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        },
        order_by=[{"startTime": "asc"}]
    )
    
    return schedules


# ====================
# RESOURCE ENDPOINTS FOR SCHEDULE MANAGEMENT
# ====================

@router.get("/resources/subjects")
async def get_subjects_for_department(
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get subjects available for schedule creation in the department"""
    where_clause = {}
    
    # Filter by department for non-admin users
    if dept_head is not None:
        where_clause["level"] = {
            "specialty": {
                "departmentId": dept_head.departmentId
            }
        }
    
    subjects = await prisma.subject.find_many(
        where=where_clause,
        include={
            "teacher": {"include": {"user": True}},
            "level": {
                "include": {
                    "specialty": {"include": {"department": True}}
                }
            }
        },
        order_by={"name": "asc"}
    )
    
    return [{
        "id": subject.id,
        "name": subject.name,
        "teacher": {
            "id": subject.teacher.id,
            "name": f"{subject.teacher.user.firstName} {subject.teacher.user.lastName}"
        },
        "level": subject.level.name,
        "specialty": subject.level.specialty.name,
        "department": subject.level.specialty.department.name
    } for subject in subjects]


@router.get("/resources/teachers")
async def get_teachers_for_department(
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get teachers available for schedule creation in the department"""
    where_clause = {}
    
    # Filter by department for non-admin users
    if dept_head is not None:
        where_clause["departmentId"] = dept_head.departmentId
    
    teachers = await prisma.teacher.find_many(
        where=where_clause,
        include={
            "user": True,
            "department": True,
            "subjects": True
        },
        order_by={"user": {"lastName": "asc"}}
    )
    
    return [{
        "id": teacher.id,
        "name": f"{teacher.user.firstName} {teacher.user.lastName}",
        "email": teacher.user.email,
        "department": teacher.department.name,
        "subjects": [subject.name for subject in teacher.subjects]
    } for teacher in teachers]


@router.get("/resources/groups")
async def get_groups_for_department(
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get groups available for schedule creation in the department"""
    where_clause = {}
    
    # Filter by department for non-admin users
    if dept_head is not None:
        where_clause["level"] = {
            "specialty": {
                "departmentId": dept_head.departmentId
            }
        }
    
    groups = await prisma.group.find_many(
        where=where_clause,
        include={
            "level": {
                "include": {
                    "specialty": {"include": {"department": True}}
                }
            }
        },
        order_by={"name": "asc"}
    )
    
    return [{
        "id": group.id,
        "name": group.name,
        "level": group.level.name,
        "specialty": group.level.specialty.name,
        "department": group.level.specialty.department.name
    } for group in groups]


@router.get("/resources/rooms")
async def get_available_rooms(
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get all available rooms for schedule creation"""
    rooms = await prisma.room.find_many(
        order_by={"code": "asc"}
    )
    
    return [{
        "id": room.id,
        "code": room.code,
        "type": room.type,
        "capacity": room.capacity
    } for room in rooms]


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Delete a schedule"""
    # Get existing schedule with department information
    existing_schedule = await prisma.schedule.find_unique(
        where={"id": schedule_id},
        include={
            "subject": {
                "include": {
                    "level": {
                        "include": {
                            "specialty": {"include": {"department": True}}
                        }
                    }
                }
            }
        }
    )
    
    if not existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )
    
    # Check department ownership for non-admin users
    if dept_head is not None:
        dept_id = dept_head.departmentId
        schedule_dept_id = existing_schedule.subject.level.specialty.departmentId
        
        if schedule_dept_id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete schedules in your own department"
            )
    
    # Delete the schedule
    await prisma.schedule.delete(where={"id": schedule_id})
    
    return {"message": "Schedule deleted successfully"}


@router.get("/timetable/weekly")
async def get_weekly_timetable(
    week_start: Optional[date_type] = None,
    prisma: Prisma = Depends(get_prisma),
    dept_head = Depends(get_current_department_head)
):
    """Get department's weekly timetable in table format"""
    
    # If no week specified, use current week
    if not week_start:
        today = date_type.today()
        # Get Monday of current week
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
    
    week_end = week_start + timedelta(days=4)  # Friday
    
    where_clause = {
        "date": {
            "gte": datetime.combine(week_start, datetime.min.time()),
            "lte": datetime.combine(week_end, datetime.max.time())
        },
        "status": {"not": "CANCELED"}
    }
    
    # Filter by department for non-admin users
    if dept_head is not None:
        where_clause["subject"] = {
            "level": {
                "specialty": {
                    "departmentId": dept_head.departmentId
                }
            }
        }
    
    # Get all schedules for the week
    schedules = await prisma.schedule.find_many(
        where=where_clause,
        include={
            "room": True,
            "subject": True,
            "group": True,
            "teacher": {"include": {"user": True}}
        },
        order_by=[
            {"date": "asc"},
            {"startTime": "asc"}
        ]
    )
    
    # Create timetable structure
    timetable = {
        "weekStart": week_start.isoformat(),
        "weekEnd": week_end.isoformat(),
        "schedules": [],
        "summary": {
            "totalSchedules": len(schedules),
            "totalHours": 0
        }
    }
    
    total_minutes = 0
    
    for schedule in schedules:
        # Calculate duration in minutes
        duration = (schedule.endTime - schedule.startTime).total_seconds() / 60
        total_minutes += duration
        
        schedule_info = {
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "dayOfWeek": schedule.date.strftime("%A"),
            "startTime": schedule.startTime.strftime("%H:%M"),
            "endTime": schedule.endTime.strftime("%H:%M"),
            "duration": f"{int(duration // 60)}h{int(duration % 60):02d}",
            "subject": {
                "id": schedule.subject.id,
                "name": schedule.subject.name
            },
            "teacher": {
                "id": schedule.teacher.id,
                "name": f"{schedule.teacher.user.firstName} {schedule.teacher.user.lastName}"
            },
            "group": {
                "id": schedule.group.id,
                "name": schedule.group.name
            },
            "room": {
                "id": schedule.room.id,
                "code": schedule.room.code,
                "type": schedule.room.type
            },
            "status": schedule.status
        }
        
        timetable["schedules"].append(schedule_info)
    
    # Convert total minutes to hours
    timetable["summary"]["totalHours"] = f"{int(total_minutes // 60)}h{int(total_minutes % 60):02d}"
    
    return timetable