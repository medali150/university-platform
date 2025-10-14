#!/usr/bin/env python3
"""
Create Real University Timetable based on user's actual schedule
This script will create all teachers, subjects, rooms, and schedule entries using Prisma
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.prisma_client import get_prisma
from datetime import datetime, time, timedelta
import logging
import bcrypt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def create_real_timetable():
    """Create the complete real timetable from user's schedule"""
    
    # Get prisma client
    prisma = await get_prisma()
    
    try:
        logger.info("🚀 Starting Real Timetable Creation...")
        
        # 1. Create Groups
        logger.info("📚 Creating Groups...")
        
        groups_to_create = [
            {"name": "LI 02", "level": "L2"},
            {"name": "LI 04", "level": "L2"}, 
            {"name": "LI 05", "level": "L2"},
            {"name": "LI 10", "level": "L1"},
            {"name": "SI 01", "level": "L3"},
            {"name": "SI 03", "level": "L3"},
            {"name": "AMPHI", "level": "ALL"}
        ]
        
        created_groups = {}
        for group_data in groups_to_create:
            existing_group = await prisma.group.find_first(
                where={"name": group_data["name"]}
            )
            if not existing_group:
                new_group = await prisma.group.create(
                    data={
                        "name": group_data["name"],
                        "level": group_data["level"],
                        "department": "Informatique"
                    }
                )
                created_groups[group_data["name"]] = new_group
                logger.info(f"✅ Created group: {group_data['name']}")
            else:
                created_groups[group_data["name"]] = existing_group
                logger.info(f"📍 Using existing group: {group_data['name']}")
        
        # 2. Create Rooms
        logger.info("🏛️ Creating Rooms...")
        
        rooms_to_create = [
            {"name": "AMPHI", "capacity": 200, "type": "Amphithéâtre"},
            {"name": "Salle A1", "capacity": 30, "type": "Salle de cours"},
            {"name": "Salle A2", "capacity": 30, "type": "Salle de cours"},
            {"name": "Lab Info", "capacity": 25, "type": "Laboratoire"},
            {"name": "Atelier", "capacity": 20, "type": "Atelier"}
        ]
        
        created_rooms = {}
        for room_data in rooms_to_create:
            existing_room = await prisma.room.find_first(
                where={"name": room_data["name"]}
            )
            if not existing_room:
                new_room = await prisma.room.create(
                    data={
                        "name": room_data["name"],
                        "capacity": room_data["capacity"],
                        "room_type": room_data["type"]
                    }
                )
                created_rooms[room_data["name"]] = new_room
                logger.info(f"✅ Created room: {room_data['name']}")
            else:
                created_rooms[room_data["name"]] = existing_room
                logger.info(f"📍 Using existing room: {room_data['name']}")
        
        # 3. Create Subjects
        logger.info("📖 Creating Subjects...")
        
        subjects_to_create = [
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
        for subject_data in subjects_to_create:
            existing_subject = await prisma.subject.find_first(
                where={"code": subject_data["code"]}
            )
            if not existing_subject:
                new_subject = await prisma.subject.create(
                    data={
                        "name": subject_data["name"],
                        "code": subject_data["code"],
                        "credits": subject_data["credits"]
                    }
                )
                created_subjects[subject_data["name"]] = new_subject
                logger.info(f"✅ Created subject: {subject_data['name']}")
            else:
                created_subjects[subject_data["name"]] = existing_subject
                logger.info(f"📍 Using existing subject: {subject_data['name']}")
        
        # 4. Create Teachers
        logger.info("👨‍🏫 Creating Teachers...")
        
        teachers_to_create = [
            {"name": "Abdelkader MAATALLAH", "email": "abdelkader.maatallah@univ.tn", "speciality": "Développement Mobile"},
            {"name": "Ahmed NEFZAOUI", "email": "ahmed.nefzaoui@univ.tn", "speciality": "Environnement de développement"},
            {"name": "Wahid HAMDI", "email": "wahid.hamdi@univ.tn", "speciality": "Frameworks"},
            {"name": "Dziriya ARFAOUI", "email": "dziriya.arfaoui@univ.tn", "speciality": "Anglais"},
            {"name": "Haithem HAFSI", "email": "haithem.hafsi@univ.tn", "speciality": "Projets"},
            {"name": "Mariem JERIDI", "email": "mariem.jeridi@univ.tn", "speciality": "Méthodologie"},
            {"name": "Mohamed TOUMI", "email": "mohamed.toumi@univ.tn", "speciality": "Marketing"}
        ]
        
        created_teachers = {}
        for teacher_data in teachers_to_create:
            # Check if user exists
            existing_user = await prisma.user.find_first(
                where={"email": teacher_data["email"]}
            )
            if not existing_user:
                # Create user account for teacher
                teacher_user = await prisma.user.create(
                    data={
                        "first_name": teacher_data["name"].split()[0],
                        "last_name": " ".join(teacher_data["name"].split()[1:]),
                        "email": teacher_data["email"],
                        "password": hash_password("teacher123"),
                        "role": "teacher"
                    }
                )
                
                # Create teacher record
                new_teacher = await prisma.teacher.create(
                    data={
                        "user_id": teacher_user.id,
                        "speciality": teacher_data["speciality"],
                        "department": "Informatique"
                    }
                )
                created_teachers[teacher_data["name"]] = new_teacher
                logger.info(f"✅ Created teacher: {teacher_data['name']}")
            else:
                existing_teacher = await prisma.teacher.find_first(
                    where={"user_id": existing_user.id}
                )
                if existing_teacher:
                    created_teachers[teacher_data["name"]] = existing_teacher
                    logger.info(f"📍 Using existing teacher: {teacher_data['name']}")
        
        # 5. Create the actual schedule based on the timetable
        logger.info("📅 Creating Real Schedule...")
        
        # Define the schedule structure based on the timetable image
        schedule_data = [
            # Monday
            {
                "day": "lundi",
                "start_time": "08:30", "end_time": "10:00",
                "subject": "Développement Mobile",
                "teacher": "Abdelkader MAATALLAH",
                "group": "LI 02", "room": "Salle A1"
            },
            {
                "day": "lundi", 
                "start_time": "10:10", "end_time": "11:40",
                "subject": "Web 3.0",
                "teacher": "Ahmed NEFZAOUI", 
                "group": "LI 10", "room": "Salle A1"
            },
            {
                "day": "lundi",
                "start_time": "11:50", "end_time": "13:20", 
                "subject": "Preparing TOEIC",
                "teacher": "Dziriya ARFAOUI",
                "group": "LI 02", "room": "Salle A2"
            },
            {
                "day": "lundi", 
                "start_time": "14:30", "end_time": "16:00",
                "subject": "Atelier Base de Données Avancée",
                "teacher": "Abdelkader MAATALLAH",
                "group": "LI 04", "room": "Lab Info"
            },
            {
                "day": "lundi",
                "start_time": "16:10", "end_time": "17:40",
                "subject": "Atelier Base de Données Avancée", 
                "teacher": "Abdelkader MAATALLAH",
                "group": "LI 04", "room": "Lab Info"
            },
            
            # Tuesday
            {
                "day": "mardi",
                "start_time": "08:30", "end_time": "10:00",
                "subject": "Environnement de développement",
                "teacher": "Ahmed NEFZAOUI",
                "group": "LI 04", "room": "Salle A1"
            },
            {
                "day": "mardi",
                "start_time": "11:50", "end_time": "13:20",
                "subject": "Projet d'Intégration", 
                "teacher": "Haithem HAFSI",
                "group": "AMPHI", "room": "AMPHI"
            },
            {
                "day": "mardi",
                "start_time": "16:10", "end_time": "17:40",
                "subject": "SOA",
                "teacher": "Abdelkader MAATALLAH",
                "group": "LI 05", "room": "Salle A2"
            },
            
            # Wednesday  
            {
                "day": "mercredi",
                "start_time": "08:30", "end_time": "10:00",
                "subject": "Atelier développement Mobile natif",
                "teacher": "Abdelkader MAATALLAH", 
                "group": "LI 04", "room": "Atelier"
            },
            {
                "day": "mercredi",
                "start_time": "11:50", "end_time": "13:20",
                "subject": "Méthodologie de Conception Objet",
                "teacher": "Mariem JERIDI",
                "group": "AMPHI", "room": "AMPHI"
            },
            
            # Thursday
            {
                "day": "jeudi", 
                "start_time": "08:30", "end_time": "10:00",
                "subject": "Atelier Framework cross-platform",
                "teacher": "Wahid HAMDI",
                "group": "LI 04", "room": "Atelier"
            },
            {
                "day": "jeudi",
                "start_time": "14:30", "end_time": "16:00", 
                "subject": "Technique de recherche d'emploi et marketing de soi",
                "teacher": "Mohamed TOUMI",
                "group": "SI 03", "room": "Salle A2"
            },
            
            # Friday
            {
                "day": "vendredi",
                "start_time": "14:30", "end_time": "16:00",
                "subject": "Atelier SOA", 
                "teacher": "Abdelkader MAATALLAH",
                "group": "LI 04", "room": "Lab Info"
            },
            {
                "day": "vendredi",
                "start_time": "16:10", "end_time": "17:40",
                "subject": "Gestion des données Massives",
                "teacher": "Abdelkader MAATALLAH", 
                "group": "LI 04", "room": "Lab Info"
            }
        ]
        
        # Calculate target Monday for this week
        today = datetime.now().date()
        days_since_monday = today.weekday()
        target_monday = today - timedelta(days=days_since_monday)
        
        created_schedules = 0
        for schedule_item in schedule_data:
            try:
                # Get day index (0=Monday, 1=Tuesday, etc.)
                day_mapping = {
                    "lundi": 0, "mardi": 1, "mercredi": 2, 
                    "jeudi": 3, "vendredi": 4, "samedi": 5
                }
                day_index = day_mapping.get(schedule_item["day"], 0)
                schedule_date = target_monday + timedelta(days=day_index)
                
                # Parse times
                start_hour, start_min = map(int, schedule_item["start_time"].split(":"))
                end_hour, end_min = map(int, schedule_item["end_time"].split(":"))
                
                # Get references
                subject = created_subjects.get(schedule_item["subject"])
                teacher = created_teachers.get(schedule_item["teacher"])
                group = created_groups.get(schedule_item["group"])
                room = created_rooms.get(schedule_item["room"])
                
                if subject and teacher and group and room:
                    # Check if schedule already exists
                    existing_schedule = await prisma.schedule.find_first(
                        where={
                            "date": schedule_date,
                            "start_time": f"{start_hour:02d}:{start_min:02d}",
                            "group_id": group.id,
                            "subject_id": subject.id
                        }
                    )
                    
                    if not existing_schedule:
                        new_schedule = await prisma.schedule.create(
                            data={
                                "date": schedule_date,
                                "start_time": f"{start_hour:02d}:{start_min:02d}",
                                "end_time": f"{end_hour:02d}:{end_min:02d}",
                                "subject_id": subject.id,
                                "teacher_id": teacher.id,
                                "group_id": group.id,
                                "room_id": room.id
                            }
                        )
                        created_schedules += 1
                        logger.info(f"✅ Created schedule: {schedule_item['subject']} - {schedule_item['day']} {schedule_item['start_time']}")
                    else:
                        logger.info(f"📍 Schedule exists: {schedule_item['subject']} - {schedule_item['day']}")
                else:
                    logger.warning(f"⚠️ Missing references for: {schedule_item}")
                    
            except Exception as e:
                logger.error(f"❌ Error creating schedule {schedule_item}: {e}")
        
        # Create sample student for testing
        logger.info("👨‍🎓 Creating sample student for LI 04...")
        existing_student_user = await prisma.user.find_first(
            where={"email": "student.li04@univ.tn"}
        )
        if not existing_student_user:
            student_user = await prisma.user.create(
                data={
                    "first_name": "Test",
                    "last_name": "Student LI04",
                    "email": "student.li04@univ.tn", 
                    "password": hash_password("student123"),
                    "role": "student"
                }
            )
            
            li04_group = created_groups.get("LI 04")
            if li04_group:
                student_record = await prisma.student.create(
                    data={
                        "user_id": student_user.id,
                        "student_number": "LI04001",
                        "group_id": li04_group.id
                    }
                )
                logger.info("✅ Created test student for LI 04")
        
        logger.info("=" * 60)
        logger.info("🎉 REAL TIMETABLE CREATION COMPLETED! 🎉")
        logger.info("=" * 60)
        logger.info(f"📊 Summary:")
        logger.info(f"   👥 Groups: {len(created_groups)}")
        logger.info(f"   🏛️  Rooms: {len(created_rooms)}")
        logger.info(f"   📖 Subjects: {len(created_subjects)}")
        logger.info(f"   👨‍🏫 Teachers: {len(created_teachers)}")
        logger.info(f"   📅 Schedules: {created_schedules}")
        logger.info("=" * 60)
        logger.info("🔑 Test Login Credentials:")
        logger.info("   Student (LI 04): student.li04@univ.tn / student123")
        logger.info("   Teachers: [teacher_email] / teacher123")
        logger.info("=" * 60)
        logger.info("🌐 Frontend URL: http://localhost:3000/dashboard/student/timetable")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error creating real timetable: {e}")
        raise
    finally:
        # Disconnect is handled by the context manager
        pass

if __name__ == "__main__":
    asyncio.run(create_real_timetable())