#!/usr/bin/env python3
"""
Fix the authentication issue properly
"""
import asyncio
from prisma import Prisma

async def fix_auth_issue():
    """Fix authentication and department head issues"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== FIXING AUTHENTICATION ISSUE ===\n")
        
        # Check current situation
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
        
        # Let's find out what departments we have
        departments = await prisma.department.find_many(
            include={"departmentHead": {"include": {"user": True}}}
        )
        
        print(f"\n📍 Available Departments:")
        departments_without_heads = []
        for dept in departments:
            if dept.departmentHead:
                print(f"  {dept.name} - Head: {dept.departmentHead.user.firstName} {dept.departmentHead.user.lastName}")
            else:
                print(f"  {dept.name} - NO HEAD")
                departments_without_heads.append(dept)
        
        # Handle the problematic user "chef"
        chef_user = await prisma.user.find_unique(
            where={"login": "chef dep"},
            include={
                "departmentHead": {
                    "include": {"department": True}
                }
            }
        )
        
        if chef_user and not chef_user.departmentHead:
            if departments_without_heads:
                # Assign chef to the first department without a head
                target_dept = departments_without_heads[0]
                print(f"\n🔧 Assigning 'chef' to {target_dept.name} department...")
                
                new_dept_head = await prisma.departmenthead.create(
                    data={
                        "userId": chef_user.id,
                        "departmentId": target_dept.id
                    },
                    include={
                        "user": True,
                        "department": True
                    }
                )
                
                print(f"✅ Created DepartmentHead record:")
                print(f"    User: {new_dept_head.user.firstName} {new_dept_head.user.lastName}")
                print(f"    Department: {new_dept_head.department.name}")
            else:
                print(f"\n⚠️  No available departments for 'chef'. Changing role to ADMIN...")
                await prisma.user.update(
                    where={"id": chef_user.id},
                    data={"role": "ADMIN"}
                )
                
                # Create admin record if needed
                admin_record = await prisma.admin.find_unique(
                    where={"userId": chef_user.id}
                )
                if not admin_record:
                    await prisma.admin.create(
                        data={
                            "userId": chef_user.id,
                            "level": "ADMIN"
                        }
                    )
                print(f"✅ Changed 'chef' role to ADMIN")
        
        print("\n=== VERIFICATION ===")
        dept_head_users = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "departmentHead": {
                    "include": {"department": True}
                }
            }
        )
        
        print("Final Department Head Status:")
        all_good = True
        for user in dept_head_users:
            if user.departmentHead:
                print(f"✅ {user.login} ({user.firstName} {user.lastName}) -> {user.departmentHead.department.name}")
            else:
                print(f"❌ {user.login} -> STILL MISSING RECORD")
                all_good = False
        
        if all_good:
            print(f"\n🎉 All Department Head records are properly linked!")
            print(f"\n📋 Now you can test with these credentials:")
            for user in dept_head_users:
                if user.departmentHead:
                    print(f"  Login: '{user.login}' / Password: 'password123'")
        else:
            print(f"\n⚠️  Some issues still remain")
            
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_auth_issue())