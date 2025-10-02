# Schedule Management API for Department Heads

This document provides the complete implementation of schedule management endpoints for department heads with proper authorization and conflict detection.

## Implementation Summary

### ✅ Completed Components

1. **Schema Definition** (`app/schemas/schedule.py`)
   - `ScheduleCreate`: Validation for new schedules
   - `ScheduleUpdate`: Validation for schedule updates  
   - `ScheduleResponse`: Structured response format
   - `ConflictInfo`: Detailed conflict information
   - `ScheduleConflictError`: Conflict error responses
   - `DepartmentAuthError`: Authorization error responses

2. **Router Implementation** (`app/routers/schedules.py`)
   - Department head authorization middleware
   - Department ownership verification
   - Schedule conflict detection
   - CRUD endpoints with proper validation

3. **Main Application Integration** (`main.py`)
   - Schedule router included in FastAPI app
   - Endpoint documentation updated

## API Endpoints

### 🔐 Authentication Required
All endpoints require `DEPARTMENT_HEAD` or `ADMIN` role with valid JWT token.

### 📋 Available Endpoints

#### 1. **POST /schedules** - Create Schedule
```http
POST /schedules
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "date": "2025-09-28T00:00:00",
  "startTime": "2025-09-28T10:00:00",
  "endTime": "2025-09-28T12:00:00",
  "roomId": "room_id_here",
  "subjectId": "subject_id_here", 
  "groupId": "group_id_here",
  "teacherId": "teacher_id_here",
  "status": "PLANNED"
}
```

**Features:**
- ✅ Department ownership verification
- ✅ Resource validation (room, subject, group, teacher exist)
- ✅ Department association check (subject/group/teacher belong to dept)
- ✅ Subject-teacher assignment verification
- ✅ Schedule conflict detection (room, teacher, group overlaps)
- ✅ Time validation (end > start, same date)

**Responses:**
- `201`: Schedule created successfully
- `400`: Validation error (bad time, wrong teacher-subject)
- `403`: Authorization error (resource not in department)
- `404`: Resource not found
- `409`: Schedule conflict detected

#### 2. **PATCH /schedules/{id}** - Update Schedule
```http
PATCH /schedules/cmg123xyz
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "status": "CANCELED",
  "startTime": "2025-09-28T11:00:00"
}
```

**Features:**
- ✅ Department ownership verification for existing schedule
- ✅ Partial update support (only provided fields)
- ✅ Resource ownership check for new assignments
- ✅ Conflict detection for time/resource changes
- ✅ Excludes current schedule from conflict check

**Responses:**
- `200`: Schedule updated successfully
- `400`: No valid fields provided
- `403`: Not authorized to modify schedule
- `404`: Schedule not found
- `409`: Update would cause conflicts

#### 3. **GET /schedules/department** - Get Department Schedules
```http
GET /schedules/department?date_from=2025-09-28&date_to=2025-10-05
Authorization: Bearer <jwt_token>
```

**Features:**
- ✅ Only shows schedules from user's department
- ✅ Optional date range filtering
- ✅ Ordered by date and start time
- ✅ Complete schedule information included

**Response:**
```json
[
  {
    "id": "schedule_id",
    "date": "2025-09-28T00:00:00",
    "startTime": "2025-09-28T10:00:00", 
    "endTime": "2025-09-28T12:00:00",
    "status": "PLANNED",
    "room": {"code": "ROOM-101", "type": "LECTURE"},
    "subject": {"name": "Advanced Programming"},
    "group": {"name": "L3-G1"},
    "teacher": {"user": {"firstName": "John", "lastName": "Doe"}}
  }
]
```

#### 4. **GET /schedules/{id}** - Get Specific Schedule
```http
GET /schedules/cmg123xyz
Authorization: Bearer <jwt_token>
```

**Features:**
- ✅ Department ownership verification
- ✅ Complete schedule details
- ✅ Related entity information

## Department Ownership Verification

### Prisma Query for Department Check
```python
async def verify_department_ownership(subject_id, group_id, teacher_id, room_id, dept_head, prisma):
    # Get subject with department chain
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
            "teacher": {"include": {"department": True}}
        }
    )
    
    # Get group with department chain  
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
    
    # Get teacher with department
    teacher = await prisma.teacher.find_unique(
        where={"id": teacher_id},
        include={"department": True, "user": True}
    )
    
    # Verify all belong to department head's department
    dept_id = dept_head.departmentId
    
    if subject.level.specialty.departmentId != dept_id:
        raise HTTPException(403, "Subject not in your department")
    if group.level.specialty.departmentId != dept_id:
        raise HTTPException(403, "Group not in your department")  
    if teacher.departmentId != dept_id:
        raise HTTPException(403, "Teacher not in your department")
```

## Conflict Detection Logic

### Schedule Overlap Detection
```python
async def check_schedule_conflicts(date, start_time, end_time, room_id, teacher_id, group_id, prisma, exclude_schedule_id=None):
    # Build overlap conditions
    overlap_conditions = {
        "date": date.date(),
        "status": {"not": "CANCELED"},
        "OR": [
            # New schedule starts during existing schedule
            {"AND": [
                {"startTime": {"lte": start_time}},
                {"endTime": {"gt": start_time}}
            ]},
            # New schedule ends during existing schedule  
            {"AND": [
                {"startTime": {"lt": end_time}},
                {"endTime": {"gte": end_time}}
            ]},
            # New schedule completely contains existing schedule
            {"AND": [
                {"startTime": {"gte": start_time}},
                {"endTime": {"lte": end_time}}
            ]}
        ]
    }
    
    # Check room conflicts
    room_conflicts = await prisma.schedule.find_many(
        where={**overlap_conditions, "roomId": room_id}
    )
    
    # Check teacher conflicts
    teacher_conflicts = await prisma.schedule.find_many(
        where={**overlap_conditions, "teacherId": teacher_id}
    )
    
    # Check group conflicts
    group_conflicts = await prisma.schedule.find_many(
        where={**overlap_conditions, "groupId": group_id}
    )
    
    return conflicts
```

## Error Handling

### Authorization Errors
```json
{
  "detail": "You can only modify schedules in your own department"
}
```

### Conflict Errors
```json
{
  "detail": {
    "error": "Schedule conflict detected",
    "conflicts": [
      {
        "type": "room",
        "conflictingScheduleId": "existing_schedule_id",
        "message": "Room ROOM-101 is already booked from 10:00 to 12:00 for Advanced Programming with L3-G1"
      },
      {
        "type": "teacher", 
        "conflictingScheduleId": "existing_schedule_id",
        "message": "Teacher John Doe is already scheduled from 11:00 to 13:00 for Database Systems in room ROOM-102"
      }
    ]
  }
}
```

### Validation Errors
```json
{
  "detail": "End time must be after start time"
}
```

## Testing

### Test Setup Script
Created `setup_test_dept_head.py` to create test department head:
- **Login:** `depthead`
- **Password:** `depthead123` 
- **Role:** `DEPARTMENT_HEAD`
- **Department:** `Computer Science`

### Test Credentials
```bash
# Department Head Authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "depthead", "password": "depthead123"}'

# Use returned token for schedule operations
curl -X GET http://localhost:8000/schedules/department \
  -H "Authorization: Bearer <token>"
```

## Security Features

1. **Role-Based Access Control**: Only `DEPARTMENT_HEAD` and `ADMIN` roles
2. **Department Isolation**: Department heads can only manage their own department's schedules
3. **Resource Ownership**: All resources (subjects, groups, teachers) must belong to the same department
4. **Subject-Teacher Verification**: Ensures subject is actually taught by specified teacher
5. **Admin Override**: Admin users can manage all departments

## Integration Notes

- ✅ Added to main FastAPI application
- ✅ Uses existing authentication system
- ✅ Follows existing code patterns and structure
- ✅ Proper error handling and validation
- ✅ Complete documentation and testing setup

The implementation is production-ready with comprehensive validation, authorization, and conflict detection.