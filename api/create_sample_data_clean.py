#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta, date
from app.db.prisma_client import DatabaseManager

async def create_sample_schedule_data():
    """Create comprehensive schedule data similar to the timetable in the image"""
    print("=== CREATING SAMPLE SCHEDULE DATA ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Get or create department
        dept = await prisma.department.find_unique(where={"name": "Computer Science"})
        if not dept:
            dept = await prisma.department.create(data={"name": "Computer Science"})
        print(f"✅ Department: {dept.name}")
        
        # Get or create specialty
        specialty = await prisma.specialty.find_first(where={"departmentId": dept.id})
        if not specialty:
            specialty = await prisma.specialty.create(data={
                "name": "Software Engineering",
                "departmentId": dept.id
            })
        print(f"✅ Specialty: {specialty.name}")
        
        # Get or create level
        level = await prisma.level.find_first(where={"specialtyId": specialty.id})
        if not level:
            level = await prisma.level.create(data={
                "name": "L3",
                "specialtyId": specialty.id
            })
        print(f"✅ Level: {level.name}")
        
        # Get or create group
        group = await prisma.group.find_first(where={"levelId": level.id})
        if not group:
            group = await prisma.group.create(data={
                "name": "L3-G1",
                "levelId": level.id
            })
        print(f"✅ Group: {group.name}")
        
        # Create sample schedule for tomorrow
        tomorrow = date.today() + timedelta(days=1)
        start_datetime = datetime.combine(tomorrow, datetime.min.time().replace(hour=10, minute=0))
        end_datetime = datetime.combine(tomorrow, datetime.min.time().replace(hour=12, minute=0))
        
        # Get existing room or create one
        room = await prisma.room.find_first()
        if not room:
            room = await prisma.room.create(data={
                "code": "TI-11",
                "type": "LAB", 
                "capacity": 30
            })
        
        # Get existing teacher or create one
        teacher = await prisma.teacher.find_first(where={"departmentId": dept.id})
        if not teacher:
            # Create teacher user first
            from app.core.security import hash_password
            teacher_user = await prisma.user.create(data={
                "firstName": "Sample",
                "lastName": "Teacher",
                "email": "teacher@university.com",
                "login": "sampleteacher",
                "passwordHash": hash_password("teacher123"),
                "role": "TEACHER"
            })
            
            teacher = await prisma.teacher.create(data={
                "userId": teacher_user.id,
                "departmentId": dept.id
            })
        
        # Get existing subject or create one
        subject = await prisma.subject.find_first(where={"levelId": level.id})
        if not subject:
            subject = await prisma.subject.create(data={
                "name": "Sample Programming Course",
                "levelId": level.id,
                "teacherId": teacher.id
            })
        
        # Check if schedule already exists
        existing = await prisma.schedule.find_first(where={
            "date": start_datetime,
            "startTime": start_datetime,
            "subjectId": subject.id,
            "groupId": group.id
        })
        
        if not existing:
            schedule = await prisma.schedule.create(data={
                "date": start_datetime,
                "startTime": start_datetime,
                "endTime": end_datetime,
                "roomId": room.id,
                "subjectId": subject.id,
                "groupId": group.id,
                "teacherId": subject.teacherId,
                "status": "PLANNED"
            })
            print(f"✅ Created sample schedule for {tomorrow}")
        else:
            print(f"✅ Schedule already exists for {tomorrow}")
        
        print(f"\n🎉 SAMPLE DATA CREATION COMPLETE!")
        print(f"   🏫 Department: {dept.name}")
        print(f"   👥 Group: {group.name}")
        
        return {
            "department_id": dept.id,
            "group_id": group.id,
            "date": tomorrow
        }
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return None
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_sample_schedule_data())