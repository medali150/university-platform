"""
Optimized Timetable Management Service

Architecture:
- Chef de département creates SEMESTER schedules (not daily/weekly)
- One source of truth: Student group schedules
- Teacher schedules are auto-generated from student schedules
- Read-only access for teachers and students
- Efficient conflict detection and validation
- Support for recurring patterns (same time every week)

Author: Senior Developer
Date: October 2025
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, time, timedelta, date
from prisma import Prisma
from dataclasses import dataclass
from enum import Enum


class DayOfWeek(str, Enum):
    """Days of the week for recurring schedules"""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"


class RecurrenceType(str, Enum):
    """How schedules repeat"""
    WEEKLY = "WEEKLY"  # Same time every week
    BIWEEKLY = "BIWEEKLY"  # Every 2 weeks
    CUSTOM = "CUSTOM"  # Custom dates


@dataclass
class ScheduleTemplate:
    """Template for creating semester schedules"""
    matiere_id: str
    groupe_id: str
    enseignant_id: str
    salle_id: str
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    recurrence_type: RecurrenceType = RecurrenceType.WEEKLY
    
    # Semester boundaries
    semester_start: date = None
    semester_end: date = None


@dataclass
class ConflictInfo:
    """Information about a schedule conflict"""
    type: str  # 'room', 'teacher', 'group'
    message: str
    conflicting_id: str
    conflicting_time: str


class TimetableConflictChecker:
    """
    Efficient conflict detection for schedules
    
    Checks:
    1. Room availability
    2. Teacher availability (can't teach 2 classes at once)
    3. Group availability (students can't be in 2 places at once)
    """
    
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
    
    async def check_conflicts(
        self,
        schedule_date: datetime,
        start_time: datetime,
        end_time: datetime,
        salle_id: str,
        enseignant_id: str,
        groupe_id: str,
        exclude_schedule_id: Optional[str] = None
    ) -> List[ConflictInfo]:
        """
        Check for all types of conflicts
        Returns list of conflicts found
        """
        conflicts = []
        
        # Build time overlap query
        overlap_query = self._build_overlap_query(
            schedule_date, start_time, end_time, exclude_schedule_id
        )
        
        # Check room conflicts
        room_conflicts = await self.prisma.emploitemps.find_many(
            where={**overlap_query, "id_salle": salle_id},
            include={
                "matiere": True,
                "groupe": True,
                "enseignant": True,
                "salle": True
            }
        )
        
        for conflict in room_conflicts:
            conflicts.append(ConflictInfo(
                type="room",
                message=f"Salle {conflict.salle.nom} est déjà réservée de {conflict.heure_debut.strftime('%H:%M')} à {conflict.heure_fin.strftime('%H:%M')}",
                conflicting_id=conflict.id,
                conflicting_time=f"{conflict.heure_debut.strftime('%H:%M')}-{conflict.heure_fin.strftime('%H:%M')}"
            ))
        
        # Check teacher conflicts
        teacher_conflicts = await self.prisma.emploitemps.find_many(
            where={**overlap_query, "id_enseignant": enseignant_id},
            include={
                "matiere": True,
                "groupe": True,
                "enseignant": True,
                "salle": True
            }
        )
        
        for conflict in teacher_conflicts:
            conflicts.append(ConflictInfo(
                type="teacher",
                message=f"Enseignant déjà occupé de {conflict.heure_debut.strftime('%H:%M')} à {conflict.heure_fin.strftime('%H:%M')} avec le groupe {conflict.groupe.nom}",
                conflicting_id=conflict.id,
                conflicting_time=f"{conflict.heure_debut.strftime('%H:%M')}-{conflict.heure_fin.strftime('%H:%M')}"
            ))
        
        # Check group conflicts
        group_conflicts = await self.prisma.emploitemps.find_many(
            where={**overlap_query, "id_groupe": groupe_id},
            include={
                "matiere": True,
                "groupe": True,
                "enseignant": True,
                "salle": True
            }
        )
        
        for conflict in group_conflicts:
            conflicts.append(ConflictInfo(
                type="group",
                message=f"Groupe {conflict.groupe.nom} a déjà cours de {conflict.heure_debut.strftime('%H:%M')} à {conflict.heure_fin.strftime('%H:%M')}",
                conflicting_id=conflict.id,
                conflicting_time=f"{conflict.heure_debut.strftime('%H:%M')}-{conflict.heure_fin.strftime('%H:%M')}"
            ))
        
        return conflicts
    
    def _build_overlap_query(
        self,
        schedule_date: datetime,
        start_time: datetime,
        end_time: datetime,
        exclude_id: Optional[str] = None
    ) -> dict:
        """Build query to find overlapping schedules"""
        # Same day
        day_start = datetime.combine(schedule_date.date(), time.min)
        day_end = datetime.combine(schedule_date.date(), time.max)
        
        query = {
            "date": {"gte": day_start, "lte": day_end},
            "status": {"not": "CANCELED"},
            "OR": [
                # New schedule starts during existing schedule
                {"AND": [
                    {"heure_debut": {"lte": start_time}},
                    {"heure_fin": {"gt": start_time}}
                ]},
                # New schedule ends during existing schedule
                {"AND": [
                    {"heure_debut": {"lt": end_time}},
                    {"heure_fin": {"gte": end_time}}
                ]},
                # New schedule completely contains existing schedule
                {"AND": [
                    {"heure_debut": {"gte": start_time}},
                    {"heure_fin": {"lte": end_time}}
                ]}
            ]
        }
        
        if exclude_id:
            query["NOT"] = {"id": exclude_id}
        
        return query


class TimetableGenerator:
    """
    Generate semester schedules from templates
    
    Key feature: Creates all schedule entries for the entire semester
    based on recurring patterns (e.g., every Monday 8:30-10:00)
    """
    
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.conflict_checker = TimetableConflictChecker(prisma)
    
    async def generate_semester_schedule(
        self,
        template: ScheduleTemplate
    ) -> Tuple[List[str], List[ConflictInfo]]:
        """
        Generate all schedule entries for a semester based on template
        
        Returns:
            (list of created schedule IDs, list of conflicts encountered)
        """
        created_ids = []
        all_conflicts = []
        
        # Get all dates for this day of week in the semester
        dates = self._get_recurring_dates(
            template.semester_start,
            template.semester_end,
            template.day_of_week,
            template.recurrence_type
        )
        
        # Create schedule entry for each date
        for schedule_date in dates:
            # Combine date with time
            start_datetime = datetime.combine(schedule_date, template.start_time)
            end_datetime = datetime.combine(schedule_date, template.end_time)
            
            # Check for conflicts
            conflicts = await self.conflict_checker.check_conflicts(
                datetime.combine(schedule_date, time.min),
                start_datetime,
                end_datetime,
                template.salle_id,
                template.enseignant_id,
                template.groupe_id
            )
            
            if conflicts:
                # Log conflict but continue (let caller decide how to handle)
                all_conflicts.extend(conflicts)
                continue
            
            # Create the schedule entry
            try:
                schedule = await self.prisma.emploitemps.create(
                    data={
                        "date": datetime.combine(schedule_date, time.min),
                        "heure_debut": start_datetime,
                        "heure_fin": end_datetime,
                        "id_salle": template.salle_id,
                        "id_matiere": template.matiere_id,
                        "id_groupe": template.groupe_id,
                        "id_enseignant": template.enseignant_id,
                        "status": "PLANNED"
                    }
                )
                created_ids.append(schedule.id)
            except Exception as e:
                print(f"Error creating schedule for {schedule_date}: {e}")
        
        return created_ids, all_conflicts
    
    def _get_recurring_dates(
        self,
        start_date: date,
        end_date: date,
        day_of_week: DayOfWeek,
        recurrence_type: RecurrenceType
    ) -> List[date]:
        """
        Get all dates for a recurring schedule
        
        Example: Get all Mondays between September and December
        """
        dates = []
        
        # Map day of week to Python weekday (0=Monday, 6=Sunday)
        day_map = {
            DayOfWeek.MONDAY: 0,
            DayOfWeek.TUESDAY: 1,
            DayOfWeek.WEDNESDAY: 2,
            DayOfWeek.THURSDAY: 3,
            DayOfWeek.FRIDAY: 4,
            DayOfWeek.SATURDAY: 5
        }
        
        target_weekday = day_map[day_of_week]
        
        # Find first occurrence of target weekday
        current = start_date
        while current.weekday() != target_weekday:
            current += timedelta(days=1)
            if current > end_date:
                return dates
        
        # Add dates based on recurrence type
        increment = timedelta(weeks=1) if recurrence_type == RecurrenceType.WEEKLY else timedelta(weeks=2)
        
        while current <= end_date:
            dates.append(current)
            current += increment
        
        return dates


class TimetableService:
    """
    Main service for timetable management
    
    Responsibilities:
    1. Create semester schedules for student groups (chef de département)
    2. Provide read-only views for teachers and students
    3. Manage schedule updates and cancellations
    4. Generate teacher schedules automatically
    """
    
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.generator = TimetableGenerator(prisma)
        self.conflict_checker = TimetableConflictChecker(prisma)
    
    async def create_semester_schedule(
        self,
        template: ScheduleTemplate,
        department_id: str
    ) -> Dict:
        """
        Create a complete semester schedule from a template
        
        This is the main entry point for chef de département
        """
        # Validate department ownership
        await self._validate_department_ownership(
            template.matiere_id,
            template.groupe_id,
            template.enseignant_id,
            department_id
        )
        
        # Generate all schedule entries
        created_ids, conflicts = await self.generator.generate_semester_schedule(template)
        
        return {
            "success": len(created_ids) > 0,
            "created_count": len(created_ids),
            "schedule_ids": created_ids,
            "conflicts": [
                {
                    "type": c.type,
                    "message": c.message,
                    "time": c.conflicting_time
                }
                for c in conflicts
            ],
            "message": f"Créé {len(created_ids)} séances pour le semestre"
        }
    
    async def get_student_timetable(
        self,
        groupe_id: str,
        week_start: Optional[date] = None
    ) -> Dict:
        """
        Get timetable for a student group (weekly view)
        
        READ-ONLY - Students cannot modify
        """
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        schedules = await self.prisma.emploitemps.find_many(
            where={
                "id_groupe": groupe_id,
                "date": {
                    "gte": datetime.combine(week_start, time.min),
                    "lte": datetime.combine(week_end, time.max)
                },
                "status": {"not": "CANCELED"}
            },
            include={
                "matiere": True,
                "enseignant": True,
                "salle": True,
                "groupe": {
                    "include": {
                        "niveau": {
                            "include": {
                                "specialite": True
                            }
                        }
                    }
                }
            },
            order=[
                {"date": "asc"},
                {"heure_debut": "asc"}
            ]
        )
        
        # Organize by day of week
        timetable = self._organize_by_day(schedules)
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "timetable": timetable,
            "total_hours": self._calculate_total_hours(schedules)
        }
    
    async def get_teacher_timetable(
        self,
        enseignant_id: str,
        week_start: Optional[date] = None
    ) -> Dict:
        """
        Get timetable for a teacher (weekly view)
        
        READ-ONLY - Teachers cannot modify (auto-generated from student schedules)
        """
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        schedules = await self.prisma.emploitemps.find_many(
            where={
                "id_enseignant": enseignant_id,
                "date": {
                    "gte": datetime.combine(week_start, time.min),
                    "lte": datetime.combine(week_end, time.max)
                },
                "status": {"not": "CANCELED"}
            },
            include={
                "matiere": True,
                "groupe": {
                    "include": {
                        "niveau": {
                            "include": {
                                "specialite": True
                            }
                        }
                    }
                },
                "salle": True,
                "enseignant": True
            },
            order=[
                {"date": "asc"},
                {"heure_debut": "asc"}
            ]
        )
        
        # Organize by day of week
        timetable = self._organize_by_day(schedules)
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "timetable": timetable,
            "total_hours": self._calculate_total_hours(schedules),
            "note": "Emploi du temps généré automatiquement à partir des cours assignés"
        }
    
    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict,
        department_id: str
    ) -> Dict:
        """
        Update a single schedule entry
        
        Only allowed for chef de département
        """
        # Get existing schedule
        existing = await self.prisma.emploitemps.find_unique(
            where={"id": schedule_id},
            include={
                "matiere": {
                    "include": {
                        "specialite": {
                            "include": {"departement": True}
                        }
                    }
                }
            }
        )
        
        if not existing:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        # Verify department ownership
        if existing.matiere.specialite.id_departement != department_id:
            raise PermissionError("Not authorized to modify this schedule")
        
        # Apply updates
        updated = await self.prisma.emploitemps.update(
            where={"id": schedule_id},
            data=updates
        )
        
        return {"success": True, "schedule": updated}
    
    async def cancel_schedule(
        self,
        schedule_id: str,
        department_id: str,
        reason: str = None
    ) -> Dict:
        """
        Cancel a schedule (mark as CANCELED, don't delete)
        
        This preserves history for absences and reporting
        """
        await self.update_schedule(
            schedule_id,
            {"status": "CANCELED"},
            department_id
        )
        
        return {
            "success": True,
            "message": "Séance annulée avec succès"
        }
    
    async def _validate_department_ownership(
        self,
        matiere_id: str,
        groupe_id: str,
        enseignant_id: str,
        department_id: str
    ):
        """Verify all resources belong to the same department"""
        # Check matiere
        matiere = await self.prisma.matiere.find_unique(
            where={"id": matiere_id},
            include={"specialite": True}
        )
        
        if not matiere or matiere.specialite.id_departement != department_id:
            raise PermissionError("Matière n'appartient pas à votre département")
        
        # Check groupe
        groupe = await self.prisma.groupe.find_unique(
            where={"id": groupe_id},
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                }
            }
        )
        
        if not groupe or groupe.niveau.specialite.id_departement != department_id:
            raise PermissionError("Groupe n'appartient pas à votre département")
        
        # Check enseignant
        enseignant = await self.prisma.enseignant.find_unique(
            where={"id": enseignant_id}
        )
        
        if not enseignant or enseignant.id_departement != department_id:
            raise PermissionError("Enseignant n'appartient pas à votre département")
    
    def _organize_by_day(self, schedules) -> Dict:
        """Organize schedules by day of week"""
        days = {
            0: "lundi",
            1: "mardi",
            2: "mercredi",
            3: "jeudi",
            4: "vendredi",
            5: "samedi"
        }
        
        timetable = {day_name: [] for day_name in days.values()}
        
        for schedule in schedules:
            day_num = schedule.date.weekday()
            if day_num in days:
                day_name = days[day_num]
                timetable[day_name].append({
                    "id": schedule.id,
                    "date": schedule.date.isoformat(),
                    "start_time": schedule.heure_debut.strftime("%H:%M"),
                    "end_time": schedule.heure_fin.strftime("%H:%M"),
                    "status": schedule.status,
                    "matiere": {
                        "id": schedule.matiere.id,
                        "nom": schedule.matiere.nom,
                        "code": schedule.matiere.code if hasattr(schedule.matiere, 'code') else None
                    },
                    "enseignant": {
                        "id": schedule.enseignant.id,
                        "nom": schedule.enseignant.nom,
                        "prenom": schedule.enseignant.prenom,
                        "email": schedule.enseignant.email if hasattr(schedule.enseignant, 'email') else None
                    },
                    "salle": {
                        "id": schedule.salle.id,
                        "code": schedule.salle.code,
                        "type": schedule.salle.type,
                        "capacite": schedule.salle.capacite
                    },
                    "groupe": {
                        "id": schedule.groupe.id,
                        "nom": schedule.groupe.nom,
                        "niveau": schedule.groupe.niveau.nom if schedule.groupe.niveau else None,
                        "specialite": schedule.groupe.niveau.specialite.nom if schedule.groupe.niveau and schedule.groupe.niveau.specialite else None
                    }
                })
        
        return timetable
    
    def _calculate_total_hours(self, schedules) -> str:
        """Calculate total hours from schedules"""
        total_minutes = sum(
            (s.heure_fin - s.heure_debut).total_seconds() / 60
            for s in schedules
        )
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        return f"{hours}h{minutes:02d}"
