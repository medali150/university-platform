#!/usr/bin/env python3
"""
Find resources that belong to the same department for schedule creation
"""
import asyncio
from prisma import Prisma

async def find_matching_resources():
    """Find resources that belong to the same department"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== FINDING MATCHING RESOURCES BY DEPARTMENT ===\n")
        
        # Get all department heads with their departments
        dept_heads = await prisma.departmenthead.find_many(
            include={
                "user": True,
                "department": True
            }
        )
        
        for dept_head in dept_heads:
            print(f"🏢 DEPARTMENT: {dept_head.department.name}")
            print(f"👤 DEPARTMENT HEAD: {dept_head.user.firstName} {dept_head.user.lastName} ({dept_head.user.login})")
            print(f"🆔 DEPARTMENT ID: {dept_head.departmentId}")
            
            # Find subjects in this department
            subjects = await prisma.subject.find_many(
                where={
                    "level": {
                        "specialty": {
                            "departmentId": dept_head.departmentId
                        }
                    }
                },
                include={
                    "teacher": {"include": {"user": True}},
                    "level": {
                        "include": {
                            "specialty": {"include": {"department": True}}
                        }
                    }
                }
            )
            
            # Find groups in this department
            groups = await prisma.group.find_many(
                where={
                    "level": {
                        "specialty": {
                            "departmentId": dept_head.departmentId
                        }
                    }
                },
                include={
                    "level": {
                        "include": {
                            "specialty": {"include": {"department": True}}
                        }
                    }
                }
            )
            
            # Find teachers in this department
            teachers = await prisma.teacher.find_many(
                where={"departmentId": dept_head.departmentId},
                include={
                    "user": True,
                    "department": True
                }
            )
            
            print(f"\n📚 SUBJECTS ({len(subjects)}):")
            for subject in subjects:
                print(f"  • {subject.name} (ID: {subject.id})")
                print(f"    Teacher: {subject.teacher.user.firstName} {subject.teacher.user.lastName}")
            
            print(f"\n👥 GROUPS ({len(groups)}):")
            for group in groups:
                print(f"  • {group.name} (ID: {group.id})")
                print(f"    Level: {group.level.name}, Specialty: {group.level.specialty.name}")
            
            print(f"\n👨‍🏫 TEACHERS ({len(teachers)}):")
            for teacher in teachers:
                print(f"  • {teacher.user.firstName} {teacher.user.lastName} (ID: {teacher.id})")
            
            # Get all rooms (rooms don't belong to specific departments)
            if dept_head.user.login == "depthead":  # Show rooms only once
                rooms = await prisma.room.find_many()
                print(f"\n🏢 ROOMS (Available to all):")
                for room in rooms:
                    print(f"  • {room.code} - {room.type} (Capacity: {room.capacity}) (ID: {room.id})")
            
            # Create a sample payload for this department
            if subjects and groups and teachers:
                first_subject = subjects[0]
                first_group = groups[0]
                first_teacher = teachers[0]
                
                # Get first room
                rooms = await prisma.room.find_many()
                first_room = rooms[0] if rooms else None
                
                if first_room:
                    print(f"\n📋 SAMPLE SWAGGER PAYLOAD FOR {dept_head.user.login}:")
                    print("{")
                    print(f'  "date": "2025-09-30T10:00:00.000Z",')
                    print(f'  "startTime": "2025-09-30T10:00:00.000Z",')
                    print(f'  "endTime": "2025-09-30T12:00:00.000Z",')
                    print(f'  "roomId": "{first_room.id}",')
                    print(f'  "subjectId": "{first_subject.id}",')
                    print(f'  "groupId": "{first_group.id}",')
                    print(f'  "teacherId": "{first_teacher.id}",')
                    print(f'  "status": "PLANNED"')
                    print("}")
            
            print("="*80)
            
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(find_matching_resources())