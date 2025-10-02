#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import hash_password

async def setup_student_user():
    """Create a student user for testing timetable endpoints"""
    print("=== CREATING TEST STUDENT USER ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Check if student user already exists
        existing_user = await prisma.user.find_unique(where={"login": "teststudent"})
        if existing_user:
            print("✅ Student user already exists")
            student = await prisma.student.find_unique(where={"userId": existing_user.id})
            if student:
                print(f"✅ Student profile exists: {existing_user.firstName} {existing_user.lastName}")
                return {"user_id": existing_user.id, "student_id": student.id}
            else:
                # User exists but no student profile, create the student profile
                print("Creating student profile for existing user...")
                
                # Get group for student assignment
                group = await prisma.group.find_first(where={"name": "L3-G1"})
                if not group:
                    print("❌ No group found for student assignment")
                    return None
                
                # Get specialty through the group's level
                level = await prisma.level.find_unique(where={"id": group.levelId}, include={"specialty": True})
                if not level or not level.specialty:
                    print("❌ No specialty found for student assignment")
                    return None
                
                # Create student profile
                student = await prisma.student.create(data={
                    "userId": existing_user.id,
                    "groupId": group.id,
                    "specialtyId": level.specialty.id
                })
                print(f"✅ Created student profile in group: {group.name}")
                
                return {
                    "user_id": existing_user.id,
                    "student_id": student.id,
                    "group_id": group.id
                }
        
        # Create student user
        student_user = await prisma.user.create(data={
            "firstName": "Test",
            "lastName": "Student",
            "email": "student@university.com",
            "login": "teststudent",
            "passwordHash": hash_password("student123"),
            "role": "STUDENT"
        })
        print(f"✅ Created student user: {student_user.firstName} {student_user.lastName}")
        
        # Get group for student assignment
        group = await prisma.group.find_first(where={"name": "L3-G1"})
        if not group:
            print("❌ No group found for student assignment")
            return None
        
        # Get specialty through the group's level
        level = await prisma.level.find_unique(where={"id": group.levelId}, include={"specialty": True})
        if not level or not level.specialty:
            print("❌ No specialty found for student assignment")
            return None
        
        # Create student profile
        student = await prisma.student.create(data={
            "userId": student_user.id,
            "groupId": group.id,
            "specialtyId": level.specialty.id
        })
        print(f"✅ Created student profile in group: {group.name}")
        
        print(f"\n🎉 TEST STUDENT SETUP COMPLETE!")
        print(f"   👤 Login: teststudent")
        print(f"   🔐 Password: student123")
        print(f"   👥 Group: {group.name}")
        
        return {
            "user_id": student_user.id,
            "student_id": student.id,
            "group_id": group.id
        }
        
    except Exception as e:
        print(f"❌ Error creating student user: {e}")
        return None
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_student_user())