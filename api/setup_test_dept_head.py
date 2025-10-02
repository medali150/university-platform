#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import hash_password

async def setup_department_head():
    """Create a department head for testing"""
    print("=== SETTING UP DEPARTMENT HEAD FOR TESTING ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Create or get department
        existing_dept = await prisma.department.find_unique(where={"name": "Computer Science"})
        
        if existing_dept:
            dept = existing_dept
            print(f"✅ Using existing department: {dept.name}")
        else:
            dept = await prisma.department.create(
                data={"name": "Computer Science"}
            )
            print(f"✅ Created new department: {dept.name}")
        print(f"✅ Department: {dept.name} ({dept.id})")
        
        # Check if department head user exists
        existing_user = await prisma.user.find_unique(where={"login": "depthead"})
        
        if existing_user:
            print(f"✅ User 'depthead' already exists")
            user = existing_user
        else:
            # Create department head user
            hashed_password = hash_password("depthead123")
            user = await prisma.user.create(
                data={
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@university.com", 
                    "login": "depthead",
                    "passwordHash": hashed_password,
                    "role": "DEPARTMENT_HEAD"
                }
            )
            print(f"✅ Created user: {user.firstName} {user.lastName} (login: {user.login})")
        
        # Create or update department head record
        existing_dept_head = await prisma.departmenthead.find_unique(where={"userId": user.id})
        
        if existing_dept_head:
            dept_head = await prisma.departmenthead.update(
                where={"userId": user.id},
                data={"departmentId": dept.id}
            )
            print(f"✅ Updated existing department head record")
        else:
            dept_head = await prisma.departmenthead.create(
                data={
                    "userId": user.id,
                    "departmentId": dept.id
                }
            )
            print(f"✅ Created new department head record")
        
        print(f"✅ Department Head record created/updated")
        print(f"   User ID: {dept_head.userId}")
        print(f"   Department ID: {dept_head.departmentId}")
        
        # Also create teacher record for the same user (so they can have subjects)
        existing_teacher = await prisma.teacher.find_unique(where={"userId": user.id})
        
        if existing_teacher:
            teacher = await prisma.teacher.update(
                where={"userId": user.id},
                data={"departmentId": dept.id}
            )
            print(f"✅ Updated existing teacher record")
        else:
            teacher = await prisma.teacher.create(
                data={
                    "userId": user.id,
                    "departmentId": dept.id
                }
            )
            print(f"✅ Created new teacher record")
        
        print(f"✅ Teacher record created/updated: {teacher.id}")
        
        print(f"\n🎯 TEST CREDENTIALS:")
        print(f"   Login: depthead")
        print(f"   Password: depthead123")
        print(f"   Role: DEPARTMENT_HEAD")
        print(f"   Department: {dept.name}")
        
        return {
            "user_id": user.id,
            "department_id": dept.id,
            "teacher_id": teacher.id,
            "login": "depthead",
            "password": "depthead123"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_department_head())