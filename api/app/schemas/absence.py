from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class AbsenceStatusEnum(str, Enum):
    PENDING = "PENDING"
    JUSTIFIED = "JUSTIFIED"
    REFUSED = "REFUSED"

class AbsenceCreate(BaseModel):
    studentId: str = Field(..., description="Student ID")
    scheduleId: str = Field(..., description="Schedule ID") 
    reason: Optional[str] = Field(None, description="Reason for absence")

class AbsenceUpdate(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for absence")
    status: Optional[AbsenceStatusEnum] = Field(None, description="Absence status")
    justificationUrl: Optional[str] = Field(None, description="URL to justification document")

class UserInfo(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    role: str

class StudentInfo(BaseModel):
    id: str
    userId: str
    enrollmentNumber: Optional[str]
    user: UserInfo

class SubjectInfo(BaseModel):
    id: str
    name: str

class GroupInfo(BaseModel):
    id: str
    name: str

class RoomInfo(BaseModel):
    id: str
    code: str
    type: Optional[str]
    capacity: Optional[int]

class ScheduleInfo(BaseModel):
    id: str
    date: datetime
    startTime: datetime
    endTime: datetime
    subject: SubjectInfo
    group: GroupInfo
    room: RoomInfo

class AbsenceResponse(BaseModel):
    id: str
    studentId: str
    scheduleId: str
    reason: Optional[str]
    status: str
    justificationUrl: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    student: StudentInfo
    schedule: ScheduleInfo

    class Config:
        from_attributes = True

class AbsenceNotification(BaseModel):
    id: str
    message: str
    type: str = "absence"
    studentId: str
    absenceId: str
    createdAt: datetime
    read: bool = False

class AbsenceSummary(BaseModel):
    totalAbsences: int
    pendingAbsences: int
    justifiedAbsences: int
    refusedAbsences: int
    studentId: str
    studentName: str

# New models for teacher absence management
class StudentAbsenceInfo(BaseModel):
    id: str
    nom: str
    prenom: str
    email: str
    is_absent: bool
    absence_id: Optional[str] = None

class TeacherGroupInfo(BaseModel):
    id: str
    nom: str
    niveau: dict
    specialite: dict
    student_count: int

class TeacherGroupDetails(BaseModel):
    id: str
    nom: str
    niveau: dict
    students: List[StudentAbsenceInfo]

class MarkAbsenceRequest(BaseModel):
    student_id: str
    schedule_id: str
    is_absent: bool
    motif: Optional[str] = None

class TeacherAbsenceResponse(BaseModel):
    success: bool
    message: str
    absence_id: Optional[str] = None