#!/usr/bin/env python3
"""
Fix the Department Head record issue
"""
import asyncio
from prisma import Prisma

async def fix_department_head_records():
    """Fix missing department head records"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== FIXING DEPARTMENT HEAD RECORDS ===\n")
        
        # Get all users with DEPARTMENT_HEAD role
        dept_head_users = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "departmentHead": {
                    "include": {"department": True}
                }
            }
        )
        
        print("Current Department Head Users:")
        for user in dept_head_users:
            print(f"  User: {user.firstName} {user.lastName} ({user.login})")
            if user.departmentHead:
                print(f"    ✅ Has DepartmentHead record - Department: {user.departmentHead.department.name}")
            else:
                print(f"    ❌ Missing DepartmentHead record")
        
        # Get Computer Science department
        cs_dept = await prisma.department.find_first(
            where={"name": {"contains": "Computer Science"}}
        )
        
        if not cs_dept:
            print("❌ Computer Science department not found!")
            return
        
        print(f"\n📍 Found Computer Science Department: {cs_dept.name} (ID: {cs_dept.id})")
        
        # Fix each department head user without a proper record
        for user in dept_head_users:
            if not user.departmentHead:
                print(f"\n🔧 Creating DepartmentHead record for {user.firstName} {user.lastName}...")
                
                # Create the DepartmentHead record
                new_dept_head = await prisma.departmenthead.create(
                    data={
                        "userId": user.id,
                        "departmentId": cs_dept.id
                    },
                    include={
                        "user": True,
                        "department": True
                    }
                )
                
                print(f"✅ Created DepartmentHead record:")
                print(f"    User: {new_dept_head.user.firstName} {new_dept_head.user.lastName}")
                print(f"    Department: {new_dept_head.department.name}")
        
        # Verify the fix
        print("\n=== VERIFICATION ===")
        dept_head_users = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "departmentHead": {
                    "include": {"department": True}
                }
            }
        )
        
        all_good = True
        for user in dept_head_users:
            if user.departmentHead:
                print(f"✅ {user.login} -> {user.departmentHead.department.name}")
            else:
                print(f"❌ {user.login} -> STILL MISSING RECORD")
                all_good = False
        
        if all_good:
            print("\n🎉 All Department Head records are now properly linked!")
        else:
            print("\n⚠️  Some issues still remain")
            
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_department_head_records())