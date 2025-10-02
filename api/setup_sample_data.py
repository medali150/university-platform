#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import hash_password

async def setup_sample_data():
    """Create sample data for department head testing"""
    print("=== SETTING UP SAMPLE DATA FOR DEPARTMENT HEAD ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # 1. First ensure department head is set up
        print("\n1. Setting up department and department head...")
        
        # Create or get department
        dept = await prisma.department.find_unique(where={"name": "Computer Science"})
        if not dept:
            dept = await prisma.department.create(data={"name": "Computer Science"})
        print(f"✅ Department: {dept.name}")
        
        # Create or get department head user
        hashed_password = hash_password("depthead123")
        user = await prisma.user.find_unique(where={"login": "depthead"})
        if not user:
            user = await prisma.user.create(data={
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@university.com", 
                "login": "depthead",
                "passwordHash": hashed_password,
                "role": "DEPARTMENT_HEAD"
            })
        else:
            user = await prisma.user.update(
                where={"id": user.id},
                data={"role": "DEPARTMENT_HEAD"}
            )
        print(f"✅ Department Head User: {user.firstName} {user.lastName}")
        
        # Create department head record
        dept_head = await prisma.departmenthead.find_unique(where={"userId": user.id})
        if not dept_head:
            dept_head = await prisma.departmenthead.create(data={
                "userId": user.id,
                "departmentId": dept.id
            })
        else:
            dept_head = await prisma.departmenthead.update(
                where={"userId": user.id},
                data={"departmentId": dept.id}
            )
        
        # 2. Create sample teachers
        print("\n2. Creating sample teachers...")
        
        teacher_data = [
            {"firstName": "Alice", "lastName": "Smith", "email": "alice.smith@university.com", "login": "teacher1"},
            {"firstName": "Bob", "lastName": "Johnson", "email": "bob.johnson@university.com", "login": "teacher2"},
            {"firstName": "Carol", "lastName": "Williams", "email": "carol.williams@university.com", "login": "teacher3"},
            {"firstName": "David", "lastName": "Brown", "email": "david.brown@university.com", "login": "teacher4"},
        ]
        
        teachers = []
        for data in teacher_data:
            # Check if teacher user already exists by login or email
            teacher_user = await prisma.user.find_unique(where={"login": data["login"]})
            if not teacher_user:
                teacher_user = await prisma.user.find_unique(where={"email": data["email"]})
            
            if not teacher_user:
                teacher_user = await prisma.user.create(data={
                    "firstName": data["firstName"],
                    "lastName": data["lastName"],
                    "email": data["email"],
                    "login": data["login"],
                    "passwordHash": hash_password("teacher123"),
                    "role": "TEACHER"
                })
            else:
                teacher_user = await prisma.user.update(
                    where={"id": teacher_user.id},
                    data={"role": "TEACHER"}
                )
            
            # Create teacher record
            teacher = await prisma.teacher.find_unique(where={"userId": teacher_user.id})
            if not teacher:
                teacher = await prisma.teacher.create(data={
                    "userId": teacher_user.id,
                    "departmentId": dept.id
                })
            else:
                teacher = await prisma.teacher.update(
                    where={"userId": teacher_user.id},
                    data={"departmentId": dept.id}
                )
            teachers.append(teacher)
            print(f"✅ Teacher: {teacher_user.firstName} {teacher_user.lastName}")
        
        # 3. Create specialties and levels
        print("\n3. Creating specialties and levels...")
        
        specialty = await prisma.specialty.find_first(where={
            "name": "Software Engineering",
            "departmentId": dept.id
        })
        if not specialty:
            specialty = await prisma.specialty.create(data={
                "name": "Software Engineering",
                "departmentId": dept.id
            })
        print(f"✅ Specialty: {specialty.name}")
        
        levels = []
        for level_name in ["L1", "L2", "L3", "M1", "M2"]:
            level = await prisma.level.find_first(where={
                "name": level_name,
                "specialtyId": specialty.id
            })
            if not level:
                level = await prisma.level.create(data={
                    "name": level_name,
                    "specialtyId": specialty.id
                })
            levels.append(level)
            print(f"✅ Level: {level.name}")
        
        # 4. Create sample subjects
        print("\n4. Creating sample subjects...")
        
        subject_data = [
            {"name": "Database Systems"},
            {"name": "Web Development"},
            {"name": "Data Structures"},
            {"name": "Machine Learning"},
            {"name": "Software Engineering"},
            {"name": "Network Security"},
        ]
        
        subjects = []
        for i, data in enumerate(subject_data):
            teacher = teachers[i % len(teachers)]  # Assign teachers cyclically
            level = levels[i % len(levels)]  # Assign levels cyclically
            
            subject = await prisma.subject.find_first(where={
                "name": data["name"],
                "levelId": level.id
            })
            if not subject:
                subject = await prisma.subject.create(data={
                    "name": data["name"],
                    "teacherId": teacher.id,
                    "levelId": level.id
                })
            else:
                subject = await prisma.subject.update(
                    where={"id": subject.id},
                    data={
                        "teacherId": teacher.id,
                        "levelId": level.id
                    }
                )
            subjects.append(subject)
            print(f"✅ Subject: {subject.name}")
        
        # 5. Create sample groups
        print("\n5. Creating sample groups...")
        
        groups = []
        for level in levels:
            for group_num in [1, 2]:
                group = await prisma.group.find_first(where={
                    "name": f"{level.name}-G{group_num}",
                    "levelId": level.id
                })
                if not group:
                    group = await prisma.group.create(data={
                        "name": f"{level.name}-G{group_num}",
                        "levelId": level.id
                    })
                groups.append(group)
                print(f"✅ Group: {group.name}")
        
        # 6. Create sample rooms
        print("\n6. Creating sample rooms...")
        
        room_data = [
            {"code": "A101", "type": "LECTURE", "capacity": 100},
            {"code": "A102", "type": "LECTURE", "capacity": 80},
            {"code": "B201", "type": "LECTURE", "capacity": 30},
            {"code": "B202", "type": "LECTURE", "capacity": 30},
            {"code": "C301", "type": "LAB", "capacity": 25},
            {"code": "C302", "type": "LAB", "capacity": 25},
            {"code": "D401", "type": "OTHER", "capacity": 20},
        ]
        
        rooms = []
        for data in room_data:
            room = await prisma.room.find_first(where={"code": data["code"]})
            if not room:
                room = await prisma.room.create(data={
                    "code": data["code"],
                    "type": data["type"],
                    "capacity": data["capacity"]
                })
            rooms.append(room)
            print(f"✅ Room: {room.code} ({room.type}, {room.capacity} seats)")
        
        # 7. Create some sample schedules
        print("\n7. Creating sample schedules...")
        
        from datetime import datetime, timedelta
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        sample_schedules = [
            {
                "date": base_date + timedelta(days=1),
                "start_hour": 8,
                "start_minute": 0,
                "end_hour": 9,
                "end_minute": 30,
                "subject": subjects[0],
                "teacher": teachers[0],
                "group": groups[0],
                "room": rooms[0]
            },
            {
                "date": base_date + timedelta(days=1),
                "start_hour": 10,
                "start_minute": 0,
                "end_hour": 11,
                "end_minute": 30,
                "subject": subjects[1],
                "teacher": teachers[1],
                "group": groups[1],
                "room": rooms[1]
            },
            {
                "date": base_date + timedelta(days=2),
                "start_hour": 14,
                "start_minute": 0,
                "end_hour": 15,
                "end_minute": 30,
                "subject": subjects[2],
                "teacher": teachers[2],
                "group": groups[0],
                "room": rooms[2]
            }
        ]
        
        schedules = []
        for data in sample_schedules:
            # Create proper DateTime objects for start and end times
            start_time = data["date"].replace(
                hour=data["start_hour"], 
                minute=data["start_minute"]
            )
            end_time = data["date"].replace(
                hour=data["end_hour"], 
                minute=data["end_minute"]
            )
            
            schedule = await prisma.schedule.create(
                data={
                    "date": data["date"],
                    "startTime": start_time,
                    "endTime": end_time,
                    "subjectId": data["subject"].id,
                    "teacherId": data["teacher"].id,
                    "groupId": data["group"].id,
                    "roomId": data["room"].id,
                    "status": "PLANNED"
                }
            )
            schedules.append(schedule)
            print(f"✅ Schedule: {data['subject'].name} - {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
        
        print(f"\n🎉 SAMPLE DATA SETUP COMPLETE!")
        print(f"   📊 Created {len(teachers)} teachers")
        print(f"   📚 Created {len(subjects)} subjects")
        print(f"   👥 Created {len(groups)} groups")
        print(f"   🏫 Created {len(rooms)} rooms")
        print(f"   📅 Created {len(schedules)} sample schedules")
        
        print(f"\n🔑 LOGIN CREDENTIALS:")
        print(f"   Department Head: depthead / depthead123")
        print(f"   Teachers: teacher1, teacher2, teacher3, teacher4 / teacher123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_sample_data())