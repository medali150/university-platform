#!/usr/bin/env python3
"""
Direct database population with your real university timetable
Using the DatabaseManager approach like other working scripts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.prisma_client import DatabaseManager
from datetime import datetime, timedelta
import bcrypt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def populate_real_timetable():
    """Populate database with your real university timetable"""
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        logger.info("🚀 POPULATING REAL UNIVERSITY TIMETABLE")
        logger.info("=" * 60)
        
        # 1. Create/verify groups from your timetable
        logger.info("📚 Creating Groups...")
        groups_data = [
            {"name": "LI 02", "level": "L2", "department": "Informatique"},
            {"name": "LI 04", "level": "L2", "department": "Informatique"},
            {"name": "LI 05", "level": "L2", "department": "Informatique"},
            {"name": "LI 10", "level": "L1", "department": "Informatique"},
            {"name": "SI 01", "level": "L3", "department": "Informatique"},
            {"name": "SI 03", "level": "L3", "department": "Informatique"},
            {"name": "AMPHI", "level": "ALL", "department": "Informatique"}
        ]
        
        created_groups = {}
        for group_data in groups_data:
            existing = await prisma.group.find_first(where={"name": group_data["name"]})
            if not existing:
                new_group = await prisma.group.create(data=group_data)
                created_groups[group_data["name"]] = new_group
                logger.info(f"✅ Created group: {group_data['name']}")
            else:
                created_groups[group_data["name"]] = existing
                logger.info(f"📍 Group exists: {group_data['name']}")
        
        # 2. Create rooms
        logger.info("🏛️ Creating Rooms...")
        rooms_data = [
            {"name": "AMPHI", "capacity": 200, "room_type": "Amphithéâtre"},
            {"name": "Salle A1", "capacity": 30, "room_type": "Salle de cours"},
            {"name": "Salle A2", "capacity": 30, "room_type": "Salle de cours"},
            {"name": "Lab Info", "capacity": 25, "room_type": "Laboratoire"},
            {"name": "Atelier", "capacity": 20, "room_type": "Atelier"}
        ]
        
        created_rooms = {}
        for room_data in rooms_data:
            existing = await prisma.room.find_first(where={"name": room_data["name"]})
            if not existing:
                new_room = await prisma.room.create(data=room_data)
                created_rooms[room_data["name"]] = new_room
                logger.info(f"✅ Created room: {room_data['name']}")
            else:
                created_rooms[room_data["name"]] = existing
                logger.info(f"📍 Room exists: {room_data['name']}")
        
        # 3. Create subjects from your timetable
        logger.info("📖 Creating Subjects...")
        subjects_data = [
            {"name": "Développement Mobile", "code": "DEV_MOB", "credits": 4},
            {"name": "Environnement de développement", "code": "ENV_DEV", "credits": 3},
            {"name": "Atelier développement Mobile natif", "code": "ATL_MOB", "credits": 3},
            {"name": "Atelier Framework cross-platform", "code": "ATL_FRM", "credits": 3},
            {"name": "Web 3.0", "code": "WEB30", "credits": 4},
            {"name": "Preparing TOEIC", "code": "TOEIC", "credits": 2},
            {"name": "Projet d'Intégration", "code": "PROJ_INT", "credits": 4},
            {"name": "Méthodologie de Conception Objet", "code": "MCO", "credits": 4},
            {"name": "Atelier Base de Données Avancée", "code": "ATL_BDA", "credits": 3},
            {"name": "SOA", "code": "SOA", "credits": 4},
            {"name": "Technique de recherche d'emploi et marketing de soi", "code": "TRE_MKT", "credits": 2},
            {"name": "Atelier SOA", "code": "ATL_SOA", "credits": 3},
            {"name": "Gestion des données Massives", "code": "GDM", "credits": 4}
        ]
        
        created_subjects = {}
        for subject_data in subjects_data:
            existing = await prisma.subject.find_first(where={"code": subject_data["code"]})
            if not existing:
                new_subject = await prisma.subject.create(data=subject_data)
                created_subjects[subject_data["name"]] = new_subject
                logger.info(f"✅ Created subject: {subject_data['name']}")
            else:
                created_subjects[subject_data["name"]] = existing
                logger.info(f"📍 Subject exists: {subject_data['name']}")
        
        # 4. Create teachers
        logger.info("👨‍🏫 Creating Teachers...")
        teachers_data = [
            {"name": "Abdelkader MAATALLAH", "email": "abdelkader.maatallah@univ.tn", "speciality": "Développement Mobile"},
            {"name": "Ahmed NEFZAOUI", "email": "ahmed.nefzaoui@univ.tn", "speciality": "Environnement de développement"},
            {"name": "Wahid HAMDI", "email": "wahid.hamdi@univ.tn", "speciality": "Frameworks"},
            {"name": "Dziriya ARFAOUI", "email": "dziriya.arfaoui@univ.tn", "speciality": "Anglais"},
            {"name": "Haithem HAFSI", "email": "haithem.hafsi@univ.tn", "speciality": "Projets"},
            {"name": "Mariem JERIDI", "email": "mariem.jeridi@univ.tn", "speciality": "Méthodologie"},
            {"name": "Mohamed TOUMI", "email": "mohamed.toumi@univ.tn", "speciality": "Marketing"}
        ]
        
        created_teachers = {}
        for teacher_data in teachers_data:
            # Check if user exists
            existing_user = await prisma.user.find_first(where={"email": teacher_data["email"]})
            if not existing_user:
                # Create user
                name_parts = teacher_data["name"].split()
                user_data = {
                    "first_name": name_parts[0],
                    "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                    "email": teacher_data["email"],
                    "password": hash_password("teacher123"),
                    "role": "teacher"
                }
                new_user = await prisma.user.create(data=user_data)
                
                # Create teacher
                teacher_record = await prisma.teacher.create(data={
                    "user_id": new_user.id,
                    "speciality": teacher_data["speciality"],
                    "department": "Informatique"
                })
                created_teachers[teacher_data["name"]] = teacher_record
                logger.info(f"✅ Created teacher: {teacher_data['name']}")
            else:
                existing_teacher = await prisma.teacher.find_first(where={"user_id": existing_user.id})
                if existing_teacher:
                    created_teachers[teacher_data["name"]] = existing_teacher
                    logger.info(f"📍 Teacher exists: {teacher_data['name']}")
        
        # 5. Create your actual schedule
        logger.info("📅 Creating Your Real Schedule...")
        
        # Calculate target Monday for current week
        today = datetime.now().date()
        days_since_monday = today.weekday()
        target_monday = today - timedelta(days=days_since_monday)
        
        # Your real timetable schedule
        schedule_data = [
            # Monday
            {"day": "lundi", "start_time": "08:30", "end_time": "10:00", "subject": "Développement Mobile", "teacher": "Abdelkader MAATALLAH", "group": "LI 02", "room": "Salle A1"},
            {"day": "lundi", "start_time": "10:10", "end_time": "11:40", "subject": "Web 3.0", "teacher": "Ahmed NEFZAOUI", "group": "LI 10", "room": "Salle A1"},
            {"day": "lundi", "start_time": "11:50", "end_time": "13:20", "subject": "Preparing TOEIC", "teacher": "Dziriya ARFAOUI", "group": "LI 02", "room": "Salle A2"},
            {"day": "lundi", "start_time": "14:30", "end_time": "16:00", "subject": "Atelier Base de Données Avancée", "teacher": "Abdelkader MAATALLAH", "group": "LI 04", "room": "Lab Info"},
            {"day": "lundi", "start_time": "16:10", "end_time": "17:40", "subject": "Atelier Base de Données Avancée", "teacher": "Abdelkader MAATALLAH", "group": "LI 04", "room": "Lab Info"},
            
            # Tuesday
            {"day": "mardi", "start_time": "08:30", "end_time": "10:00", "subject": "Environnement de développement", "teacher": "Ahmed NEFZAOUI", "group": "LI 04", "room": "Salle A1"},
            {"day": "mardi", "start_time": "11:50", "end_time": "13:20", "subject": "Projet d'Intégration", "teacher": "Haithem HAFSI", "group": "AMPHI", "room": "AMPHI"},
            {"day": "mardi", "start_time": "16:10", "end_time": "17:40", "subject": "SOA", "teacher": "Abdelkader MAATALLAH", "group": "LI 05", "room": "Salle A2"},
            
            # Wednesday
            {"day": "mercredi", "start_time": "08:30", "end_time": "10:00", "subject": "Atelier développement Mobile natif", "teacher": "Abdelkader MAATALLAH", "group": "LI 04", "room": "Atelier"},
            {"day": "mercredi", "start_time": "11:50", "end_time": "13:20", "subject": "Méthodologie de Conception Objet", "teacher": "Mariem JERIDI", "group": "AMPHI", "room": "AMPHI"},
            
            # Thursday
            {"day": "jeudi", "start_time": "08:30", "end_time": "10:00", "subject": "Atelier Framework cross-platform", "teacher": "Wahid HAMDI", "group": "LI 04", "room": "Atelier"},
            {"day": "jeudi", "start_time": "14:30", "end_time": "16:00", "subject": "Technique de recherche d'emploi et marketing de soi", "teacher": "Mohamed TOUMI", "group": "SI 03", "room": "Salle A2"},
            
            # Friday
            {"day": "vendredi", "start_time": "14:30", "end_time": "16:00", "subject": "Atelier SOA", "teacher": "Abdelkader MAATALLAH", "group": "LI 04", "room": "Lab Info"},
            {"day": "vendredi", "start_time": "16:10", "end_time": "17:40", "subject": "Gestion des données Massives", "teacher": "Abdelkader MAATALLAH", "group": "LI 04", "room": "Lab Info"}
        ]
        
        created_schedules = 0
        day_mapping = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, "vendredi": 4, "samedi": 5}
        
        for schedule_item in schedule_data:
            try:
                day_index = day_mapping.get(schedule_item["day"], 0)
                schedule_date = target_monday + timedelta(days=day_index)
                
                # Get references
                subject = created_subjects.get(schedule_item["subject"])
                teacher = created_teachers.get(schedule_item["teacher"])
                group = created_groups.get(schedule_item["group"])
                room = created_rooms.get(schedule_item["room"])
                
                if subject and teacher and group and room:
                    # Check if schedule exists
                    existing = await prisma.schedule.find_first(where={
                        "date": schedule_date,
                        "start_time": schedule_item["start_time"],
                        "group_id": group.id,
                        "subject_id": subject.id
                    })
                    
                    if not existing:
                        new_schedule = await prisma.schedule.create(data={
                            "date": schedule_date,
                            "start_time": schedule_item["start_time"],
                            "end_time": schedule_item["end_time"],
                            "subject_id": subject.id,
                            "teacher_id": teacher.id,
                            "group_id": group.id,
                            "room_id": room.id
                        })
                        created_schedules += 1
                        logger.info(f"✅ Created: {schedule_item['subject']} - {schedule_item['day']} {schedule_item['start_time']} - {schedule_item['group']}")
                    else:
                        logger.info(f"📍 Exists: {schedule_item['subject']} - {schedule_item['day']}")
                else:
                    logger.warning(f"⚠️ Missing refs for: {schedule_item}")
            except Exception as e:
                logger.error(f"❌ Error creating schedule {schedule_item}: {e}")
        
        # 6. Create/update student for LI 04
        logger.info("👨‍🎓 Setting up LI 04 Student...")
        li04_group = created_groups.get("LI 04")
        if li04_group:
            existing_student_user = await prisma.user.find_first(where={"email": "student.li04@univ.tn"})
            if not existing_student_user:
                student_user = await prisma.user.create(data={
                    "first_name": "Test",
                    "last_name": "Student LI04",
                    "email": "student.li04@univ.tn",
                    "password": hash_password("student123"),
                    "role": "student"
                })
                
                await prisma.student.create(data={
                    "user_id": student_user.id,
                    "student_number": "LI04001",
                    "group_id": li04_group.id
                })
                logger.info("✅ Created LI 04 student account")
            else:
                # Update existing student to be in LI 04 group
                existing_student = await prisma.student.find_first(where={"user_id": existing_student_user.id})
                if existing_student:
                    await prisma.student.update(
                        where={"id": existing_student.id},
                        data={"group_id": li04_group.id}
                    )
                    logger.info("✅ Updated student to LI 04 group")
        
        logger.info("=" * 60)
        logger.info("🎉 REAL TIMETABLE POPULATED SUCCESSFULLY! 🎉")
        logger.info("=" * 60)
        logger.info(f"📊 Summary:")
        logger.info(f"   👥 Groups: {len(created_groups)}")
        logger.info(f"   🏛️  Rooms: {len(created_rooms)}")
        logger.info(f"   📖 Subjects: {len(created_subjects)}")
        logger.info(f"   👨‍🏫 Teachers: {len(created_teachers)}")
        logger.info(f"   📅 Schedules: {created_schedules}")
        logger.info("=" * 60)
        logger.info("🔑 LOGIN CREDENTIALS:")
        logger.info("   Student LI 04: student.li04@univ.tn / student123")
        logger.info("=" * 60)
        logger.info("🌐 FRONTEND TEST:")
        logger.info("   URL: http://localhost:3000/dashboard/student/timetable")
        logger.info("   Login and check your real timetable!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error populating timetable: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(populate_real_timetable())