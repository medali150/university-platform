"""
Pydantic models for absence management system
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AbsenceStatus(str, Enum):
    UNJUSTIFIED = "unjustified"
    JUSTIFIED = "justified"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class AbsenceCreate(BaseModel):
    studentId: str = Field(..., description="ID de l'étudiant")
    scheduleId: Optional[str] = Field(None, description="ID de l'emploi du temps (optionnel)")
    subjectId: Optional[str] = Field(None, description="ID de la matière (pour absence générale)")
    absenceDate: Optional[datetime] = Field(None, description="Date de l'absence (pour absence générale)")
    reason: str = Field(default="", description="Motif de l'absence")
    status: AbsenceStatus = Field(default=AbsenceStatus.UNJUSTIFIED, description="Statut de l'absence")

class AbsenceUpdate(BaseModel):
    reason: Optional[str] = None
    status: Optional[AbsenceStatus] = None

class AbsenceJustification(BaseModel):
    absenceId: str = Field(..., description="ID de l'absence")
    justificationText: str = Field(..., description="Texte de justification")
    supportingDocuments: Optional[List[str]] = Field(default=[], description="Documents justificatifs")

class AbsenceReview(BaseModel):
    absenceId: str = Field(..., description="ID de l'absence")
    reviewStatus: AbsenceStatus = Field(..., description="Statut de révision")
    reviewNotes: Optional[str] = Field(None, description="Notes de révision")

class AbsenceQuery(BaseModel):
    studentId: Optional[str] = None
    teacherId: Optional[str] = None
    classId: Optional[str] = None
    status: Optional[AbsenceStatus] = None
    dateFrom: Optional[datetime] = None
    dateTo: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)

class AbsenceResponse(BaseModel):
    id: str
    studentId: str
    studentName: str
    scheduleId: Optional[str] = None
    className: Optional[str] = None
    teacherName: Optional[str] = None
    subjectName: Optional[str] = None
    date: Optional[datetime] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    reason: str
    status: AbsenceStatus
    justificationText: Optional[str] = None
    supportingDocuments: Optional[List[str]] = []
    reviewNotes: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class AbsenceStatistics(BaseModel):
    totalAbsences: int
    justifiedAbsences: int
    unjustifiedAbsences: int
    pendingReview: int
    approvedJustifications: int
    rejectedJustifications: int
    absenceRate: float
    studentsWithHighAbsences: List[dict]

class NotificationHistory(BaseModel):
    id: str
    absenceId: str
    recipientEmail: str
    notificationType: str
    channels: List[str]
    status: str
    sentAt: datetime
    errorMessage: Optional[str] = None