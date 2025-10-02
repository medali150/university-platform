#!/usr/bin/env python3
"""
Check department heads in the database
"""
import asyncio
from prisma import Prisma


async def main():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== CHECKING DEPARTMENT HEADS ===")
        
        # Check all users with DEPARTMENT_HEAD role
        users = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"}
        )
        print(f"\nUsers with DEPARTMENT_HEAD role: {len(users)}")
        for user in users:
            print(f"  - {user.firstName} {user.lastName} (ID: {user.id}, Email: {user.email})")
        
        # Check department head records
        dept_heads = await prisma.departmenthead.find_many(
            include={
                "user": True,
                "department": True
            }
        )
        print(f"\nDepartment Head records: {len(dept_heads)}")
        for dh in dept_heads:
            print(f"  - {dh.user.firstName} {dh.user.lastName} -> {dh.department.name} (UserID: {dh.userId})")
        
        # Check departments
        departments = await prisma.department.find_many()
        print(f"\nDepartments: {len(departments)}")
        for dept in departments:
            print(f"  - {dept.name} (ID: {dept.id})")
            
        # Check if there are any subjects, groups, teachers for testing
        subjects = await prisma.subject.find_many()
        groups = await prisma.group.find_many()
        teachers = await prisma.teacher.find_many()
        rooms = await prisma.room.find_many()
        
        print(f"\nResources available:")
        print(f"  - Subjects: {len(subjects)}")
        print(f"  - Groups: {len(groups)}")
        print(f"  - Teachers: {len(teachers)}")
        print(f"  - Rooms: {len(rooms)}")
        
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(main())