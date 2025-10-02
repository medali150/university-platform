from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ScheduleStatusEnum(str, Enum):
    PLANNED = "PLANNED"
    CANCELED = "CANCELED"
    MAKEUP = "MAKEUP"

class ScheduleCreate(BaseModel):
    date: datetime = Field(..., description="Schedule date")
    startTime: datetime = Field(..., description="Start time")
    endTime: datetime = Field(..., description="End time")
    roomId: str = Field(..., description="Room ID")
    subjectId: str = Field(..., description="Subject ID")
    groupId: str = Field(..., description="Group ID")
    teacherId: str = Field(..., description="Teacher ID")
    status: ScheduleStatusEnum = Field(default=ScheduleStatusEnum.PLANNED, description="Schedule status")

    @validator('endTime')
    def validate_end_time(cls, v, values):
        if 'startTime' in values and v <= values['startTime']:
            raise ValueError('End time must be after start time')
        return v

    @validator('startTime', 'endTime')
    def validate_same_date(cls, v, values):
        if 'date' in values:
            # Ensure time is on the same date
            date = values['date'].date()
            if v.date() != date:
                raise ValueError('Start and end time must be on the same date as the schedule date')
        return v

class ScheduleUpdate(BaseModel):
    date: Optional[datetime] = Field(None, description="Schedule date")
    startTime: Optional[datetime] = Field(None, description="Start time")
    endTime: Optional[datetime] = Field(None, description="End time")
    roomId: Optional[str] = Field(None, description="Room ID")
    subjectId: Optional[str] = Field(None, description="Subject ID")
    groupId: Optional[str] = Field(None, description="Group ID")
    teacherId: Optional[str] = Field(None, description="Teacher ID")
    status: Optional[ScheduleStatusEnum] = Field(None, description="Schedule status")

    @validator('endTime')
    def validate_end_time(cls, v, values):
        if v and 'startTime' in values and values['startTime'] and v <= values['startTime']:
            raise ValueError('End time must be after start time')
        return v

class UserInfo(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str

class RoomInfo(BaseModel):
    id: str
    code: str
    type: str
    capacity: int

class SubjectInfo(BaseModel):
    id: str
    name: str
    levelId: str

class GroupInfo(BaseModel):
    id: str
    name: str
    levelId: str

class TeacherInfo(BaseModel):
    id: str
    userId: str
    departmentId: str
    user: UserInfo

class ScheduleResponse(BaseModel):
    id: str
    date: datetime
    startTime: datetime
    endTime: datetime
    status: str
    createdAt: datetime
    updatedAt: datetime
    room: RoomInfo
    subject: SubjectInfo
    group: GroupInfo
    teacher: TeacherInfo

    class Config:
        from_attributes = True

class ConflictInfo(BaseModel):
    type: str = Field(..., description="Type of conflict: room, teacher, or group")
    conflictingScheduleId: str = Field(..., description="ID of conflicting schedule")
    message: str = Field(..., description="Human-readable conflict description")

class ScheduleConflictError(BaseModel):
    error: str = Field(default="Schedule conflict detected")
    conflicts: List[ConflictInfo]
    
class DepartmentAuthError(BaseModel):
    error: str = Field(default="Unauthorized: Resource not in your department")
    message: str = Field(..., description="Detailed authorization error message")