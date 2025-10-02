#!/usr/bin/env python3
"""
Get resource IDs for testing schedule creation
"""
import asyncio
from prisma import Prisma

async def get_resources():
    """Get all resource IDs needed for schedule creation"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== GETTING RESOURCE IDS FOR SCHEDULE CREATION ===\n")
        
        # Get subjects with their IDs
        subjects = await prisma.subject.find_many(
            include={
                "teacher": {"include": {"user": True}},
                "level": {
                    "include": {
                        "specialty": {"include": {"department": True}}
                    }
                }
            }
        )
        
        print("📚 SUBJECTS:")
        for subject in subjects:
            print(f"  ID: {subject.id}")
            print(f"  Name: {subject.name}")
            print(f"  Teacher: {subject.teacher.user.firstName} {subject.teacher.user.lastName}")
            print(f"  Department: {subject.level.specialty.department.name}")
            print(f"  ---")
        
        # Get groups
        groups = await prisma.group.find_many(
            include={
                "level": {
                    "include": {
                        "specialty": {"include": {"department": True}}
                    }
                }
            }
        )
        
        print("\n👥 GROUPS:")
        for group in groups:
            print(f"  ID: {group.id}")
            print(f"  Name: {group.name}")
            print(f"  Level: {group.level.name}")
            print(f"  Specialty: {group.level.specialty.name}")
            print(f"  Department: {group.level.specialty.department.name}")
            print(f"  ---")
        
        # Get teachers
        teachers = await prisma.teacher.find_many(
            include={
                "user": True,
                "department": True
            }
        )
        
        print("\n👨‍🏫 TEACHERS:")
        for teacher in teachers:
            print(f"  ID: {teacher.id}")
            print(f"  Name: {teacher.user.firstName} {teacher.user.lastName}")
            print(f"  Department: {teacher.department.name}")
            print(f"  ---")
        
        # Get rooms
        rooms = await prisma.room.find_many()
        
        print("\n🏢 ROOMS:")
        for room in rooms:
            print(f"  ID: {room.id}")
            print(f"  Code: {room.code}")
            print(f"  Type: {room.type}")
            print(f"  Capacity: {room.capacity}")
            print(f"  ---")
        
        # Get department heads for authentication
        dept_heads = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "departmentHead": {
                    "include": {"department": True}
                }
            }
        )
        
        print("\n👤 DEPARTMENT HEADS FOR AUTH:")
        for user in dept_heads:
            print(f"  Login: {user.login}")
            print(f"  Name: {user.firstName} {user.lastName}")
            if user.departmentHead:
                print(f"  Department: {user.departmentHead.department.name}")
            print(f"  ---")
        
        print("\n✅ Resource IDs retrieved successfully!")
        
        # Provide a sample payload
        if subjects and groups and teachers and rooms:
            first_subject = subjects[0]
            first_group = groups[0]
            first_teacher = teachers[0]
            first_room = rooms[0]
            
            print("\n📋 SAMPLE SWAGGER PAYLOAD:")
            print("{")
            print(f'  "date": "2025-09-29T08:00:00.000Z",')
            print(f'  "startTime": "2025-09-29T08:00:00.000Z",')
            print(f'  "endTime": "2025-09-29T10:00:00.000Z",')
            print(f'  "roomId": "{first_room.id}",')
            print(f'  "subjectId": "{first_subject.id}",')
            print(f'  "groupId": "{first_group.id}",')
            print(f'  "teacherId": "{first_teacher.id}",')
            print(f'  "status": "PLANNED"')
            print("}")
            
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(get_resources())