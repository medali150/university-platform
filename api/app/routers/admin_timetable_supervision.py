"""
Admin Timetable Supervision Module
===================================
Complete timetable management with intelligent conflict detection.
Supports viewing by: Department, Teacher, Classroom, Group/Section
Includes: Automatic conflict detection, Alternative suggestions, Bulk operations
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from typing import List, Optional, Dict, Any
from prisma import Prisma
from datetime import datetime, timedelta, time as dt_time
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.db.prisma_client import get_prisma
from app.core.deps import require_admin

router = APIRouter(prefix="/admin/timetable", tags=["Admin - Timetable Supervision"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ConflictType(str, Enum):
    ROOM = "room_conflict"
    TEACHER = "teacher_conflict"
    STUDENT_GROUP = "student_group_conflict"
    TIME = "time_conflict"
    LOGIC = "logic_conflict"
    CAPACITY = "capacity_conflict"

class SessionCreate(BaseModel):
    date: str = Field(..., description="Format: YYYY-MM-DD")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Format: HH:MM")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Format: HH:MM")
    subject_id: str
    group_id: str
    teacher_id: str
    room_id: str
    semester: Optional[str] = None  # e.g., "2024-2025-S1"
    is_recurring: bool = False
    recurrence_weeks: int = Field(default=1, ge=1, le=20)
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            start = datetime.strptime(values['start_time'], "%H:%M").time()
            end = datetime.strptime(v, "%H:%M").time()
            if end <= start:
                raise ValueError("end_time must be after start_time")
        return v

class SessionUpdate(BaseModel):
    date: Optional[str] = None
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    subject_id: Optional[str] = None
    group_id: Optional[str] = None
    teacher_id: Optional[str] = None
    room_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(PLANNED|CANCELED|MAKEUP)$")

class BulkSessionCreate(BaseModel):
    sessions: List[SessionCreate]
    check_conflicts: bool = True

class ConflictResolution(BaseModel):
    conflict_type: str
    severity: str  # "critical", "warning"
    message: str
    affected_sessions: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]

class TimetableFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    department_id: Optional[str] = None
    teacher_id: Optional[str] = None
    room_id: Optional[str] = None
    group_id: Optional[str] = None
    specialty_id: Optional[str] = None
    status: Optional[str] = None


# ============================================================================
# CONFLICT DETECTION ENGINE
# ============================================================================

class ConflictDetector:
    """Intelligent conflict detection engine"""
    
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.conflicts: List[Dict[str, Any]] = []
    
    async def detect_all_conflicts(
        self,
        session_data: SessionCreate,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Run all conflict checks and return structured conflict information
        """
        self.conflicts = []
        
        # Parse datetime
        session_date = datetime.strptime(session_data.date, "%Y-%m-%d")
        start_time = datetime.strptime(session_data.start_time, "%H:%M").time()
        end_time = datetime.strptime(session_data.end_time, "%H:%M").time()
        
        start_datetime = datetime.combine(session_date, start_time)
        end_datetime = datetime.combine(session_date, end_time)
        
        # Run all conflict checks
        await self._check_room_conflict(session_data, start_datetime, end_datetime, session_id)
        await self._check_teacher_conflict(session_data, start_datetime, end_datetime, session_id)
        await self._check_group_conflict(session_data, start_datetime, end_datetime, session_id)
        await self._check_time_validity(start_datetime, end_datetime)
        await self._check_logic_conflict(session_data)
        await self._check_capacity_conflict(session_data)
        
        return self.conflicts
    
    async def _check_room_conflict(
        self,
        session_data: SessionCreate,
        start_dt: datetime,
        end_dt: datetime,
        exclude_session_id: Optional[str] = None
    ):
        """Detect if room is already occupied at this time"""
        where_clause = {
            "id_salle": session_data.room_id,
            "date": start_dt.replace(hour=0, minute=0, second=0),
            "status": {"not": "CANCELED"},
            "AND": [
                {"heure_debut": {"lt": end_dt}},
                {"heure_fin": {"gt": start_dt}}
            ]
        }
        
        if exclude_session_id:
            where_clause["id"] = {"not": exclude_session_id}
        
        conflicting_sessions = await self.prisma.emploitemps.find_many(
            where=where_clause,
            include={
                "matiere": True,
                "groupe": True,
                "enseignant": True,
                "salle": True
            }
        )
        
        if conflicting_sessions:
            # Find alternative rooms
            suggestions = await self._suggest_alternative_rooms(
                start_dt, end_dt, session_data
            )
            
            self.conflicts.append({
                "type": ConflictType.ROOM,
                "severity": "critical",
                "message": f"Room already occupied during this time slot",
                "details": {
                    "room_id": session_data.room_id,
                    "conflicting_sessions": [
                        {
                            "id": s.id,
                            "subject": s.matiere.nom if s.matiere else "Unknown",
                            "group": s.groupe.nom if s.groupe else "Unknown",
                            "teacher": f"{s.enseignant.prenom} {s.enseignant.nom}" if s.enseignant else "Unknown",
                            "time": f"{s.heure_debut.strftime('%H:%M')} - {s.heure_fin.strftime('%H:%M')}"
                        }
                        for s in conflicting_sessions
                    ]
                },
                "suggestions": suggestions
            })
    
    async def _check_teacher_conflict(
        self,
        session_data: SessionCreate,
        start_dt: datetime,
        end_dt: datetime,
        exclude_session_id: Optional[str] = None
    ):
        """Detect if teacher is already assigned elsewhere"""
        where_clause = {
            "id_enseignant": session_data.teacher_id,
            "date": start_dt.replace(hour=0, minute=0, second=0),
            "status": {"not": "CANCELED"},
            "AND": [
                {"heure_debut": {"lt": end_dt}},
                {"heure_fin": {"gt": start_dt}}
            ]
        }
        
        if exclude_session_id:
            where_clause["id"] = {"not": exclude_session_id}
        
        conflicting_sessions = await self.prisma.emploitemps.find_many(
            where=where_clause,
            include={
                "matiere": True,
                "groupe": True,
                "salle": True
            }
        )
        
        if conflicting_sessions:
            # Suggest alternative teachers
            suggestions = await self._suggest_alternative_teachers(
                start_dt, end_dt, session_data
            )
            
            self.conflicts.append({
                "type": ConflictType.TEACHER,
                "severity": "critical",
                "message": f"Teacher already assigned to another session",
                "details": {
                    "teacher_id": session_data.teacher_id,
                    "conflicting_sessions": [
                        {
                            "id": s.id,
                            "subject": s.matiere.nom if s.matiere else "Unknown",
                            "group": s.groupe.nom if s.groupe else "Unknown",
                            "room": s.salle.code if s.salle else "Unknown",
                            "time": f"{s.heure_debut.strftime('%H:%M')} - {s.heure_fin.strftime('%H:%M')}"
                        }
                        for s in conflicting_sessions
                    ]
                },
                "suggestions": suggestions
            })
    
    async def _check_group_conflict(
        self,
        session_data: SessionCreate,
        start_dt: datetime,
        end_dt: datetime,
        exclude_session_id: Optional[str] = None
    ):
        """Detect if group already has another session"""
        where_clause = {
            "id_groupe": session_data.group_id,
            "date": start_dt.replace(hour=0, minute=0, second=0),
            "status": {"not": "CANCELED"},
            "AND": [
                {"heure_debut": {"lt": end_dt}},
                {"heure_fin": {"gt": start_dt}}
            ]
        }
        
        if exclude_session_id:
            where_clause["id"] = {"not": exclude_session_id}
        
        conflicting_sessions = await self.prisma.emploitemps.find_many(
            where=where_clause,
            include={
                "matiere": True,
                "enseignant": True,
                "salle": True
            }
        )
        
        if conflicting_sessions:
            # Suggest alternative time slots
            suggestions = await self._suggest_alternative_times(
                start_dt.date(), session_data
            )
            
            self.conflicts.append({
                "type": ConflictType.STUDENT_GROUP,
                "severity": "critical",
                "message": f"Group already has another session at this time",
                "details": {
                    "group_id": session_data.group_id,
                    "conflicting_sessions": [
                        {
                            "id": s.id,
                            "subject": s.matiere.nom if s.matiere else "Unknown",
                            "teacher": f"{s.enseignant.prenom} {s.enseignant.nom}" if s.enseignant else "Unknown",
                            "room": s.salle.code if s.salle else "Unknown",
                            "time": f"{s.heure_debut.strftime('%H:%M')} - {s.heure_fin.strftime('%H:%M')}"
                        }
                        for s in conflicting_sessions
                    ]
                },
                "suggestions": suggestions
            })
    
    async def _check_time_validity(self, start_dt: datetime, end_dt: datetime):
        """Check if time range is valid"""
        # Check if times are within university hours (e.g., 8:00 - 18:00)
        if start_dt.hour < 8 or end_dt.hour > 18:
            self.conflicts.append({
                "type": ConflictType.TIME,
                "severity": "warning",
                "message": "Session time outside university operating hours (8:00 - 18:00)",
                "details": {
                    "start_time": start_dt.strftime("%H:%M"),
                    "end_time": end_dt.strftime("%H:%M")
                },
                "suggestions": [
                    {
                        "type": "adjust_time",
                        "message": "Consider scheduling within 8:00 - 18:00"
                    }
                ]
            })
        
        # Check session duration (min 30 min, max 3 hours)
        duration = (end_dt - start_dt).total_seconds() / 3600
        if duration < 0.5:
            self.conflicts.append({
                "type": ConflictType.TIME,
                "severity": "warning",
                "message": "Session duration too short (minimum 30 minutes recommended)",
                "details": {"duration_hours": duration},
                "suggestions": []
            })
        elif duration > 3:
            self.conflicts.append({
                "type": ConflictType.TIME,
                "severity": "warning",
                "message": "Session duration too long (maximum 3 hours recommended)",
                "details": {"duration_hours": duration},
                "suggestions": []
            })
    
    async def _check_logic_conflict(self, session_data: SessionCreate):
        """Check if teacher is authorized to teach this subject"""
        # Get subject with teacher info
        subject = await self.prisma.matiere.find_unique(
            where={"id": session_data.subject_id},
            include={"enseignant": True}
        )
        
        if not subject:
            self.conflicts.append({
                "type": ConflictType.LOGIC,
                "severity": "critical",
                "message": "Subject not found",
                "details": {"subject_id": session_data.subject_id},
                "suggestions": []
            })
            return
        
        # Check if teacher is assigned to this subject
        if subject.id_enseignant and subject.id_enseignant != session_data.teacher_id:
            assigned_teacher = subject.enseignant
            self.conflicts.append({
                "type": ConflictType.LOGIC,
                "severity": "warning",
                "message": "Teacher not assigned to this subject",
                "details": {
                    "subject": subject.nom,
                    "assigned_teacher": f"{assigned_teacher.prenom} {assigned_teacher.nom}" if assigned_teacher else None,
                    "assigned_teacher_id": subject.id_enseignant
                },
                "suggestions": [
                    {
                        "type": "use_assigned_teacher",
                        "teacher_id": subject.id_enseignant,
                        "teacher_name": f"{assigned_teacher.prenom} {assigned_teacher.nom}" if assigned_teacher else None
                    }
                ]
            })
    
    async def _check_capacity_conflict(self, session_data: SessionCreate):
        """Check if room capacity is sufficient for group size"""
        # Get room capacity
        room = await self.prisma.salle.find_unique(
            where={"id": session_data.room_id}
        )
        
        if not room:
            return
        
        # Get group size
        group = await self.prisma.groupe.find_unique(
            where={"id": session_data.group_id}
        )
        
        if not group:
            return
        
        group_size = await self.prisma.etudiant.count(
            where={"id_groupe": session_data.group_id}
        )
        
        if group_size > room.capacite:
            # Suggest larger rooms
            larger_rooms = await self.prisma.salle.find_many(
                where={
                    "capacite": {"gte": group_size},
                    "type": room.type  # Same room type
                },
                take=5,
                order={"capacite": "asc"}
            )
            
            self.conflicts.append({
                "type": ConflictType.CAPACITY,
                "severity": "critical",
                "message": f"Room capacity ({room.capacite}) insufficient for group size ({group_size})",
                "details": {
                    "room_capacity": room.capacite,
                    "group_size": group_size,
                    "deficit": group_size - room.capacite
                },
                "suggestions": [
                    {
                        "type": "larger_room",
                        "room_id": r.id,
                        "room_code": r.code,
                        "capacity": r.capacite,
                        "type": r.type
                    }
                    for r in larger_rooms
                ]
            })
    
    async def _suggest_alternative_rooms(
        self,
        start_dt: datetime,
        end_dt: datetime,
        session_data: SessionCreate
    ) -> List[Dict[str, Any]]:
        """Find available rooms at this time"""
        # Get current room type
        current_room = await self.prisma.salle.find_unique(
            where={"id": session_data.room_id}
        )
        
        if not current_room:
            return []
        
        # Find all rooms of same type
        all_rooms = await self.prisma.salle.find_many(
            where={"type": current_room.type}
        )
        
        suggestions = []
        for room in all_rooms:
            if room.id == session_data.room_id:
                continue
            
            # Check if room is free
            conflicts = await self.prisma.emploitemps.find_first(
                where={
                    "id_salle": room.id,
                    "date": start_dt.replace(hour=0, minute=0, second=0),
                    "status": {"not": "CANCELED"},
                    "AND": [
                        {"heure_debut": {"lt": end_dt}},
                        {"heure_fin": {"gt": start_dt}}
                    ]
                }
            )
            
            if not conflicts:
                suggestions.append({
                    "type": "alternative_room",
                    "room_id": room.id,
                    "room_code": room.code,
                    "capacity": room.capacite,
                    "room_type": room.type,
                    "availability": "free"
                })
        
        return suggestions[:5]  # Top 5 suggestions
    
    async def _suggest_alternative_teachers(
        self,
        start_dt: datetime,
        end_dt: datetime,
        session_data: SessionCreate
    ) -> List[Dict[str, Any]]:
        """Find available teachers for this subject"""
        # Get subject to find qualified teachers
        subject = await self.prisma.matiere.find_unique(
            where={"id": session_data.subject_id},
            include={
                "specialite": {
                    "include": {
                        "departement": {
                            "include": {"enseignants": True}
                        }
                    }
                }
            }
        )
        
        if not subject:
            return []
        
        suggestions = []
        # Check teachers from same department
        for teacher in subject.specialite.departement.enseignants:
            if teacher.id == session_data.teacher_id:
                continue
            
            # Check if teacher is free
            conflicts = await self.prisma.emploitemps.find_first(
                where={
                    "id_enseignant": teacher.id,
                    "date": start_dt.replace(hour=0, minute=0, second=0),
                    "status": {"not": "CANCELED"},
                    "AND": [
                        {"heure_debut": {"lt": end_dt}},
                        {"heure_fin": {"gt": start_dt}}
                    ]
                }
            )
            
            if not conflicts:
                suggestions.append({
                    "type": "alternative_teacher",
                    "teacher_id": teacher.id,
                    "teacher_name": f"{teacher.prenom} {teacher.nom}",
                    "availability": "free"
                })
        
        return suggestions[:5]
    
    async def _suggest_alternative_times(
        self,
        date: datetime.date,
        session_data: SessionCreate
    ) -> List[Dict[str, Any]]:
        """Suggest alternative time slots on the same day"""
        # Standard time slots
        time_slots = [
            ("08:00", "09:30"),
            ("09:40", "11:10"),
            ("11:20", "12:50"),
            ("14:00", "15:30"),
            ("15:40", "17:10")
        ]
        
        suggestions = []
        for start_time_str, end_time_str in time_slots:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            start_dt = datetime.combine(date, start_time)
            end_dt = datetime.combine(date, end_time)
            
            # Check if slot is free for teacher, room, and group
            conflicts = await self.prisma.emploitemps.find_first(
                where={
                    "date": datetime.combine(date, dt_time(0, 0)),
                    "status": {"not": "CANCELED"},
                    "AND": [
                        {"heure_debut": {"lt": end_dt}},
                        {"heure_fin": {"gt": start_dt}}
                    ],
                    "OR": [
                        {"id_enseignant": session_data.teacher_id},
                        {"id_salle": session_data.room_id},
                        {"id_groupe": session_data.group_id}
                    ]
                }
            )
            
            if not conflicts:
                suggestions.append({
                    "type": "alternative_time",
                    "start_time": start_time_str,
                    "end_time": end_time_str,
                    "availability": "all_free"
                })
        
        return suggestions


# ============================================================================
# TIMETABLE SUPERVISION ENDPOINTS
# ============================================================================

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    check_conflicts: bool = Query(True, description="Check for conflicts before creating"),
    force: bool = Query(False, description="Force create even with conflicts"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Create a new timetable session with intelligent conflict detection.
    Returns conflicts if found and force=false.
    """
    # Run conflict detection
    detector = ConflictDetector(prisma)
    conflicts = await detector.detect_all_conflicts(session_data)
    
    # Check for critical conflicts
    critical_conflicts = [c for c in conflicts if c["severity"] == "critical"]
    
    if critical_conflicts and not force and check_conflicts:
        return {
            "status": "conflict_detected",
            "message": "Critical conflicts found. Set force=true to override.",
            "conflicts": conflicts,
            "session_data": session_data.dict()
        }
    
    # Parse datetime
    session_date = datetime.strptime(session_data.date, "%Y-%m-%d")
    start_time = datetime.strptime(session_data.start_time, "%H:%M").time()
    end_time = datetime.strptime(session_data.end_time, "%H:%M").time()
    
    start_datetime = datetime.combine(session_date, start_time)
    end_datetime = datetime.combine(session_date, end_time)
    
    # Determine day of week (1=Monday)
    day_of_week = session_date.isoweekday()
    
    # Create session(s)
    created_sessions = []
    
    if session_data.is_recurring:
        # Create recurring sessions
        for week in range(session_data.recurrence_weeks):
            current_date = session_date + timedelta(weeks=week)
            current_start = datetime.combine(current_date, start_time)
            current_end = datetime.combine(current_date, end_time)
            
            session = await prisma.emploitemps.create(
                data={
                    "date": current_date,
                    "heure_debut": current_start,
                    "heure_fin": current_end,
                    "id_salle": session_data.room_id,
                    "id_matiere": session_data.subject_id,
                    "id_groupe": session_data.group_id,
                    "id_enseignant": session_data.teacher_id,
                    "status": "PLANNED",
                    "semester": session_data.semester,
                    "week_day": day_of_week,
                    "is_recurring": True
                }
            )
            created_sessions.append(session.id)
    else:
        # Create single session
        session = await prisma.emploitemps.create(
            data={
                "date": session_date,
                "heure_debut": start_datetime,
                "heure_fin": end_datetime,
                "id_salle": session_data.room_id,
                "id_matiere": session_data.subject_id,
                "id_groupe": session_data.group_id,
                "id_enseignant": session_data.teacher_id,
                "status": "PLANNED",
                "semester": session_data.semester,
                "week_day": day_of_week,
                "is_recurring": False
            }
        )
        created_sessions.append(session.id)
    
    return {
        "status": "success",
        "message": f"Created {len(created_sessions)} session(s)",
        "session_ids": created_sessions,
        "conflicts": conflicts if conflicts else [],
        "warnings": [c for c in conflicts if c["severity"] == "warning"]
    }

@router.post("/sessions/bulk", status_code=status.HTTP_201_CREATED)
async def create_bulk_sessions(
    bulk_data: BulkSessionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Create multiple sessions at once with conflict checking"""
    results = {
        "created": [],
        "conflicts": [],
        "errors": []
    }
    
    for idx, session_data in enumerate(bulk_data.sessions):
        try:
            # Check conflicts
            if bulk_data.check_conflicts:
                detector = ConflictDetector(prisma)
                conflicts = await detector.detect_all_conflicts(session_data)
                
                critical = [c for c in conflicts if c["severity"] == "critical"]
                if critical:
                    results["conflicts"].append({
                        "index": idx,
                        "session": session_data.dict(),
                        "conflicts": conflicts
                    })
                    continue
            
            # Create session
            session_date = datetime.strptime(session_data.date, "%Y-%m-%d")
            start_time = datetime.strptime(session_data.start_time, "%H:%M").time()
            end_time = datetime.strptime(session_data.end_time, "%H:%M").time()
            
            session = await prisma.emploitemps.create(
                data={
                    "date": session_date,
                    "heure_debut": datetime.combine(session_date, start_time),
                    "heure_fin": datetime.combine(session_date, end_time),
                    "id_salle": session_data.room_id,
                    "id_matiere": session_data.subject_id,
                    "id_groupe": session_data.group_id,
                    "id_enseignant": session_data.teacher_id,
                    "status": "PLANNED",
                    "semester": session_data.semester,
                    "is_recurring": session_data.is_recurring
                }
            )
            
            results["created"].append(session.id)
            
        except Exception as e:
            results["errors"].append({
                "index": idx,
                "session": session_data.dict(),
                "error": str(e)
            })
    
    return results

@router.get("/sessions")
async def get_all_sessions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    department_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    room_id: Optional[str] = None,
    group_id: Optional[str] = None,
    specialty_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Get all timetable sessions with advanced filtering.
    Supports viewing by: Department, Teacher, Room, Group, Specialty
    """
    where_clause = {}
    
    # Date range filter
    if start_date:
        where_clause["date"] = {"gte": datetime.strptime(start_date, "%Y-%m-%d")}
    if end_date:
        if "date" in where_clause:
            where_clause["date"]["lte"] = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            where_clause["date"] = {"lte": datetime.strptime(end_date, "%Y-%m-%d")}
    
    # Entity filters
    if teacher_id:
        where_clause["id_enseignant"] = teacher_id
    if room_id:
        where_clause["id_salle"] = room_id
    if group_id:
        where_clause["id_groupe"] = group_id
    if status:
        where_clause["status"] = status
    
    # Department filter (through teacher)
    if department_id:
        where_clause["enseignant"] = {"id_departement": department_id}
    
    # Specialty filter (through subject)
    if specialty_id:
        where_clause["matiere"] = {"id_specialite": specialty_id}
    
    sessions = await prisma.emploitemps.find_many(
        where=where_clause,
        skip=skip,
        take=limit,
        include={
            "salle": True,
            "matiere": {
                "include": {"specialite": {"include": {"departement": True}}}
            },
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            },
            "enseignant": {
                "include": {
                    "departement": True,
                    "utilisateur": True
                }
            }
        },
        order={"date": "asc"}
    )
    
    total = await prisma.emploitemps.count(where=where_clause)
    
    # Format response
    formatted_sessions = []
    for s in sessions:
        formatted_sessions.append({
            "id": s.id,
            "date": s.date.strftime("%Y-%m-%d"),
            "day_of_week": s.week_day,
            "start_time": s.heure_debut.strftime("%H:%M"),
            "end_time": s.heure_fin.strftime("%H:%M"),
            "status": s.status,
            "is_recurring": s.is_recurring,
            "semester": s.semester,
            "room": {
                "id": s.salle.id,
                "code": s.salle.code,
                "type": s.salle.type,
                "capacity": s.salle.capacite
            },
            "subject": {
                "id": s.matiere.id,
                "name": s.matiere.nom,
                "specialty": s.matiere.specialite.nom if s.matiere.specialite else None,
                "department": s.matiere.specialite.departement.nom if s.matiere.specialite and s.matiere.specialite.departement else None
            },
            "group": {
                "id": s.groupe.id,
                "name": s.groupe.nom,
                "level": s.groupe.niveau.nom if s.groupe.niveau else None
            },
            "teacher": {
                "id": s.enseignant.id,
                "name": f"{s.enseignant.prenom} {s.enseignant.nom}",
                "email": s.enseignant.utilisateur.email if s.enseignant.utilisateur else None,
                "department": s.enseignant.departement.nom if s.enseignant.departement else None
            },
            "created_at": s.createdAt.isoformat(),
            "updated_at": s.updatedAt.isoformat()
        })
    
    return {
        "data": formatted_sessions,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit,
        "filters_applied": {
            "start_date": start_date,
            "end_date": end_date,
            "department_id": department_id,
            "teacher_id": teacher_id,
            "room_id": room_id,
            "group_id": group_id,
            "specialty_id": specialty_id,
            "status": status
        }
    }

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get a single session with full details"""
    session = await prisma.emploitemps.find_unique(
        where={"id": session_id},
        include={
            "salle": True,
            "matiere": {"include": {"specialite": {"include": {"departement": True}}}},
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            },
            "enseignant": {"include": {"departement": True, "utilisateur": True}}
        }
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get counts separately
    absences_count = await prisma.absence.count(where={"id_seance": session_id})
    group_size = 0
    if session.groupe:
        group_size = await prisma.etudiant.count(where={"id_groupe": session.groupe.id})
    
    return {
        "id": session.id,
        "date": session.date.strftime("%Y-%m-%d"),
        "start_time": session.heure_debut.strftime("%H:%M"),
        "end_time": session.heure_fin.strftime("%H:%M"),
        "status": session.status,
        "is_recurring": session.is_recurring,
        "semester": session.semester,
        "room": session.salle,
        "subject": session.matiere,
        "group": session.groupe,
        "teacher": session.enseignant,
        "stats": {
            "absences_count": absences_count,
            "group_size": group_size
        }
    }

@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    check_conflicts: bool = Query(True),
    force: bool = Query(False),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Update a timetable session with conflict checking"""
    # Get existing session
    existing = await prisma.emploitemps.find_unique(where={"id": session_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Prepare update data
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    # If time/date/entities changed, check conflicts
    if check_conflicts and any(k in update_dict for k in ['date', 'start_time', 'end_time', 'teacher_id', 'room_id', 'group_id']):
        # Build temporary session data for conflict check
        temp_session = SessionCreate(
            date=update_data.date or existing.date.strftime("%Y-%m-%d"),
            start_time=update_data.start_time or existing.heure_debut.strftime("%H:%M"),
            end_time=update_data.end_time or existing.heure_fin.strftime("%H:%M"),
            subject_id=update_data.subject_id or existing.id_matiere,
            group_id=update_data.group_id or existing.id_groupe,
            teacher_id=update_data.teacher_id or existing.id_enseignant,
            room_id=update_data.room_id or existing.id_salle
        )
        
        detector = ConflictDetector(prisma)
        conflicts = await detector.detect_all_conflicts(temp_session, session_id)
        
        critical = [c for c in conflicts if c["severity"] == "critical"]
        if critical and not force:
            return {
                "status": "conflict_detected",
                "message": "Critical conflicts found. Set force=true to override.",
                "conflicts": conflicts
            }
    
    # Convert time strings to datetime if provided
    if update_data.date or update_data.start_time or update_data.end_time:
        date = datetime.strptime(update_data.date, "%Y-%m-%d") if update_data.date else existing.date
        start_time = datetime.strptime(update_data.start_time, "%H:%M").time() if update_data.start_time else existing.heure_debut.time()
        end_time = datetime.strptime(update_data.end_time, "%H:%M").time() if update_data.end_time else existing.heure_fin.time()
        
        update_dict["date"] = date
        update_dict["heure_debut"] = datetime.combine(date, start_time)
        update_dict["heure_fin"] = datetime.combine(date, end_time)
        update_dict.pop("start_time", None)
        update_dict.pop("end_time", None)
    
    # Update session
    session = await prisma.emploitemps.update(
        where={"id": session_id},
        data=update_dict,
        include={
            "salle": True,
            "matiere": True,
            "groupe": True,
            "enseignant": True
        }
    )
    
    return {
        "status": "success",
        "message": "Session updated successfully",
        "data": session
    }

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    cascade: bool = Query(False, description="Delete related absences"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Delete a timetable session"""
    session = await prisma.emploitemps.find_unique(
        where={"id": session_id}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    absences_count = await prisma.absence.count(
        where={"id_seance": session_id}
    )
    
    if absences_count > 0 and not cascade:
        raise HTTPException(
            status_code=400,
            detail=f"Session has {absences_count} absences. Set cascade=true to delete them."
        )
    
    # Delete session (absences will cascade if configured in schema)
    await prisma.emploitemps.delete(where={"id": session_id})
    
    return {"message": "Session deleted successfully"}

@router.post("/sessions/check-conflicts")
async def check_session_conflicts(
    session_data: SessionCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """
    Check for conflicts without creating the session.
    Returns detailed conflict analysis with suggestions.
    """
    detector = ConflictDetector(prisma)
    conflicts = await detector.detect_all_conflicts(session_data)
    
    critical = [c for c in conflicts if c["severity"] == "critical"]
    warnings = [c for c in conflicts if c["severity"] == "warning"]
    
    return {
        "has_conflicts": len(conflicts) > 0,
        "has_critical": len(critical) > 0,
        "conflicts_count": len(conflicts),
        "critical_count": len(critical),
        "warnings_count": len(warnings),
        "conflicts": conflicts,
        "can_proceed": len(critical) == 0,
        "session_data": session_data.dict()
    }


# ============================================================================
# ANALYTICS & STATISTICS
# ============================================================================

@router.get("/analytics/overview")
async def get_timetable_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get timetable analytics and statistics"""
    where_clause = {}
    
    if start_date:
        where_clause["date"] = {"gte": datetime.strptime(start_date, "%Y-%m-%d")}
    if end_date:
        if "date" in where_clause:
            where_clause["date"]["lte"] = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            where_clause["date"] = {"lte": datetime.strptime(end_date, "%Y-%m-%d")}
    
    # Count sessions by status
    total_sessions = await prisma.emploitemps.count(where=where_clause)
    planned = await prisma.emploitemps.count(where={**where_clause, "status": "PLANNED"})
    canceled = await prisma.emploitemps.count(where={**where_clause, "status": "CANCELED"})
    makeup = await prisma.emploitemps.count(where={**where_clause, "status": "MAKEUP"})
    
    # Count unique entities
    sessions = await prisma.emploitemps.find_many(
        where=where_clause,
        select={
            "id_enseignant": True,
            "id_salle": True,
            "id_groupe": True,
            "id_matiere": True
        }
    )
    
    unique_teachers = len(set(s.id_enseignant for s in sessions))
    unique_rooms = len(set(s.id_salle for s in sessions))
    unique_groups = len(set(s.id_groupe for s in sessions))
    unique_subjects = len(set(s.id_matiere for s in sessions))
    
    return {
        "total_sessions": total_sessions,
        "by_status": {
            "planned": planned,
            "canceled": canceled,
            "makeup": makeup
        },
        "unique_entities": {
            "teachers": unique_teachers,
            "rooms": unique_rooms,
            "groups": unique_groups,
            "subjects": unique_subjects
        },
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }
