#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta, date, time
from app.db.prisma_client import DatabaseManager

async def create_schedule_for_student_group():
    """Create schedule entries for the student's group"""
    
    print("=== CREATING SCHEDULE FOR STUDENT GROUP ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Get the student's group info
        student_group_id = "cmg6pgscy000bbm1o5iy4kd06"  # From diagnostic
        
        # Get group info
        group = await prisma.groupe.find_unique(
            where={"id": student_group_id},
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                }
            }
        )
        
        if not group:
            print(f"❌ Group not found: {student_group_id}")
            return
        
        print(f"✅ Found group: {group.nom}")
        print(f"   Level: {group.niveau.nom}")
        print(f"   Specialty: {group.niveau.specialite.nom}")
        
        # Get available teachers, subjects, and rooms
        teachers = await prisma.enseignant.find_many(take=3)
        subjects = await prisma.matiere.find_many(take=5)
        rooms = await prisma.salle.find_many(take=3)
        
        print(f"✅ Found {len(teachers)} teachers, {len(subjects)} subjects, {len(rooms)} rooms")
        
        if not teachers or not subjects or not rooms:
            print("❌ Missing basic data (teachers, subjects, or rooms)")
            return
        
        # Create schedule for next week (Monday to Friday)
        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        schedules_created = []
        
        # Create a typical weekly schedule
        schedule_template = [
            # Monday
            {"day": 0, "start": "08:00", "end": "10:00", "subject_idx": 0, "teacher_idx": 0, "room_idx": 0},
            {"day": 0, "start": "10:30", "end": "12:30", "subject_idx": 1, "teacher_idx": 1, "room_idx": 1},
            # Tuesday  
            {"day": 1, "start": "08:00", "end": "10:00", "subject_idx": 2, "teacher_idx": 2, "room_idx": 0},
            {"day": 1, "start": "14:00", "end": "16:00", "subject_idx": 0, "teacher_idx": 0, "room_idx": 2},
            # Wednesday
            {"day": 2, "start": "10:30", "end": "12:30", "subject_idx": 1, "teacher_idx": 1, "room_idx": 1},
            # Thursday
            {"day": 3, "start": "08:00", "end": "10:00", "subject_idx": 3, "teacher_idx": 0, "room_idx": 0},
            {"day": 3, "start": "14:00", "end": "16:00", "subject_idx": 2, "teacher_idx": 2, "room_idx": 2},
            # Friday
            {"day": 4, "start": "08:00", "end": "10:00", "subject_idx": 4, "teacher_idx": 1, "room_idx": 1},
        ]
        
        for schedule_info in schedule_template:
            try:
                # Calculate the date
                schedule_date = next_monday + timedelta(days=schedule_info["day"])
                
                # Parse times
                start_time = datetime.strptime(schedule_info["start"], "%H:%M").time()
                end_time = datetime.strptime(schedule_info["end"], "%H:%M").time()
                
                # Create datetime objects
                start_datetime = datetime.combine(schedule_date, start_time)
                end_datetime = datetime.combine(schedule_date, end_time)
                
                # Get resources (with safe indexing)
                subject = subjects[schedule_info["subject_idx"] % len(subjects)]
                teacher = teachers[schedule_info["teacher_idx"] % len(teachers)]
                room = rooms[schedule_info["room_idx"] % len(rooms)]
                
                # Create schedule entry
                new_schedule = await prisma.emploitemps.create(
                    data={
                        "date": start_datetime,
                        "heure_debut": start_datetime,
                        "heure_fin": end_datetime,
                        "id_salle": room.id,
                        "id_matiere": subject.id,
                        "id_groupe": student_group_id,
                        "id_enseignant": teacher.id,
                        "status": "PLANNED"
                    }
                )
                
                schedules_created.append({
                    "date": schedule_date.strftime("%Y-%m-%d"),
                    "time": f"{schedule_info['start']}-{schedule_info['end']}",
                    "subject": subject.nom,
                    "teacher": f"{teacher.prenom} {teacher.nom}",
                    "room": room.code
                })
                
                print(f"✅ Created: {schedule_date.strftime('%A %Y-%m-%d')} {schedule_info['start']}-{schedule_info['end']} - {subject.nom}")
                
            except Exception as e:
                print(f"❌ Failed to create schedule: {e}")
        
        print(f"\n🎉 SCHEDULE CREATION COMPLETE!")
        print(f"Created {len(schedules_created)} schedule entries for group: {group.nom}")
        
        # Verify the schedules were created
        verification = await prisma.emploitemps.count(
            where={"id_groupe": student_group_id}
        )
        print(f"✅ Verification: {verification} schedules now exist for this group")
        
        return schedules_created
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_schedule_for_student_group())