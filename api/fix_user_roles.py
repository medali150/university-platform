"""
Data Fix Script: Create missing role entries for existing users

This script identifies users who have roles but are missing entries 
in their respective role tables (Admin, Teacher, Student, DepartmentHead).
"""

import asyncio
from prisma import Prisma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_user_role_assignments():
    """Fix missing role assignments for existing users"""
    
    print("🔧 Starting Data Fix: User Role Assignments")
    print("=" * 50)
    
    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get all users
        users = await prisma.user.find_many(
            include={
                "admin": True,
                "teacher": True,
                "student": True,
                "departmentHead": True
            }
        )
        
        print(f"📊 Found {len(users)} users in database")
        
        # Initialize counters
        fixed_admins = 0
        fixed_teachers = 0
        fixed_students = 0
        fixed_department_heads = 0
        
        # Process each user
        for user in users:
            print(f"\n👤 Processing user: {user.firstName} {user.lastName} ({user.email})")
            print(f"   Role: {user.role}")
            
            # Check and fix ADMIN role
            if user.role == "ADMIN" and not user.admin:
                print("   ❌ Missing Admin entry - Creating...")
                await prisma.admin.create(
                    data={
                        "userId": user.id,
                        "level": "ADMIN"
                    }
                )
                fixed_admins += 1
                print("   ✅ Admin entry created")
            elif user.role == "ADMIN" and user.admin:
                print("   ✅ Admin entry exists")
            
            # Check and fix TEACHER role
            elif user.role == "TEACHER" and not user.teacher:
                print("   ❌ Missing Teacher entry - Creating...")
                
                # First, we need to ensure we have departments
                departments = await prisma.department.find_many()
                if not departments:
                    print("   ⚠️  No departments found. Creating default department...")
                    default_dept = await prisma.department.create(
                        data={
                            "name": "General Department"
                        }
                    )
                    departments = [default_dept]
                
                # Create teacher entry with first available department
                await prisma.teacher.create(
                    data={
                        "userId": user.id,
                        "departmentId": departments[0].id
                    }
                )
                fixed_teachers += 1
                print(f"   ✅ Teacher entry created (assigned to {departments[0].name})")
            elif user.role == "TEACHER" and user.teacher:
                print("   ✅ Teacher entry exists")
            
            # Check and fix STUDENT role
            elif user.role == "STUDENT" and not user.student:
                print("   ❌ Missing Student entry - Creating...")
                
                # Ensure we have the required data structure
                departments = await prisma.department.find_many()
                if not departments:
                    print("   ⚠️  Creating default department...")
                    default_dept = await prisma.department.create(
                        data={"name": "General Department"}
                    )
                    departments = [default_dept]
                
                specialties = await prisma.specialty.find_many()
                if not specialties:
                    print("   ⚠️  Creating default specialty...")
                    default_specialty = await prisma.specialty.create(
                        data={
                            "name": "General Specialty",
                            "departmentId": departments[0].id
                        }
                    )
                    specialties = [default_specialty]
                
                levels = await prisma.level.find_many()
                if not levels:
                    print("   ⚠️  Creating default level...")
                    default_level = await prisma.level.create(
                        data={
                            "name": "Level 1",
                            "specialtyId": specialties[0].id
                        }
                    )
                    levels = [default_level]
                
                groups = await prisma.group.find_many()
                if not groups:
                    print("   ⚠️  Creating default group...")
                    default_group = await prisma.group.create(
                        data={
                            "name": "Group A",
                            "levelId": levels[0].id
                        }
                    )
                    groups = [default_group]
                
                # Create student entry
                await prisma.student.create(
                    data={
                        "userId": user.id,
                        "groupId": groups[0].id,
                        "specialtyId": specialties[0].id
                    }
                )
                fixed_students += 1
                print(f"   ✅ Student entry created (assigned to {groups[0].name} in {specialties[0].name})")
            elif user.role == "STUDENT" and user.student:
                print("   ✅ Student entry exists")
            
            # Check and fix DEPARTMENT_HEAD role
            elif user.role == "DEPARTMENT_HEAD" and not user.departmentHead:
                print("   ❌ Missing DepartmentHead entry - Creating...")
                
                # Ensure we have departments
                departments = await prisma.department.find_many()
                if not departments:
                    print("   ⚠️  Creating default department...")
                    default_dept = await prisma.department.create(
                        data={"name": "General Department"}
                    )
                    departments = [default_dept]
                
                # Find a department without a head or use the first one
                available_dept = None
                for dept in departments:
                    existing_head = await prisma.department_head.find_unique(
                        where={"departmentId": dept.id}
                    )
                    if not existing_head:
                        available_dept = dept
                        break
                
                if not available_dept:
                    print("   ⚠️  All departments have heads. Creating new department...")
                    available_dept = await prisma.department.create(
                        data={
                            "name": f"Department of {user.firstName} {user.lastName}"
                        }
                    )
                
                # Create department head entry
                await prisma.department_head.create(
                    data={
                        "userId": user.id,
                        "departmentId": available_dept.id
                    }
                )
                fixed_department_heads += 1
                print(f"   ✅ DepartmentHead entry created (assigned to {available_dept.name})")
            elif user.role == "DEPARTMENT_HEAD" and user.departmentHead:
                print("   ✅ DepartmentHead entry exists")
        
        print("\n" + "=" * 50)
        print("🎯 Data Fix Summary:")
        print(f"   Admins fixed: {fixed_admins}")
        print(f"   Teachers fixed: {fixed_teachers}")
        print(f"   Students fixed: {fixed_students}")
        print(f"   Department Heads fixed: {fixed_department_heads}")
        print(f"   Total fixes: {fixed_admins + fixed_teachers + fixed_students + fixed_department_heads}")
        
        # Verify the fixes
        print("\n🔍 Verification:")
        verification_users = await prisma.user.find_many(
            include={
                "admin": True,
                "teacher": True,
                "student": True,
                "departmentHead": True
            }
        )
        
        for user in verification_users:
            has_role_entry = False
            role_detail = ""
            
            if user.role == "ADMIN" and user.admin:
                has_role_entry = True
                role_detail = f"Admin (level: {user.admin.level})"
            elif user.role == "TEACHER" and user.teacher:
                has_role_entry = True
                role_detail = "Teacher"
            elif user.role == "STUDENT" and user.student:
                has_role_entry = True
                role_detail = "Student"
            elif user.role == "DEPARTMENT_HEAD" and user.departmentHead:
                has_role_entry = True
                role_detail = "Department Head"
            
            status = "✅" if has_role_entry else "❌"
            print(f"   {status} {user.firstName} {user.lastName}: {user.role} -> {role_detail}")
        
        print("\n✅ Data fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data fix: {e}")
    finally:
        await prisma.disconnect()


async def main():
    """Main function"""
    await fix_user_role_assignments()


if __name__ == "__main__":
    asyncio.run(main())