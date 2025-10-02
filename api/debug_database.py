"""
Debug script to investigate and fix role/data issues in the database
"""

import asyncio
from prisma import Prisma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def investigate_role_issues():
    """Check for role inconsistencies in the database"""
    print("🔍 Investigating Role and Data Issues")
    print("=" * 60)
    
    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Check users and their roles
        print("👥 USERS AND ROLES:")
        users = await prisma.user.find_many(
            include={
                "admin": True,
                "teacher": {"include": {"department": True}},
                "student": {
                    "include": {
                        "group": True,
                        "specialty": True
                    }
                },
                "departmentHead": {"include": {"department": True}}
            }
        )
        
        for user in users:
            print(f"   📋 {user.firstName} {user.lastName} ({user.email})")
            print(f"      Role: {user.role}")
            print(f"      Login: {user.login}")
            
            if user.role == "ADMIN" and user.admin:
                print(f"      ✅ Admin entry: ID {user.admin.id}, Level {user.admin.level}")
            elif user.role == "TEACHER" and user.teacher:
                dept_name = user.teacher.department.name if user.teacher.department else "No Department"
                print(f"      ✅ Teacher entry: ID {user.teacher.id}, Department: {dept_name}")
            elif user.role == "STUDENT" and user.student:
                group_name = user.student.group.name if user.student.group else "No Group"
                specialty_name = user.student.specialty.name if user.student.specialty else "No Specialty"
                print(f"      ✅ Student entry: ID {user.student.id}, Group: {group_name}, Specialty: {specialty_name}")
            elif user.role == "DEPARTMENT_HEAD" and user.departmentHead:
                dept_name = user.departmentHead.department.name if user.departmentHead.department else "No Department"
                print(f"      ✅ Department Head entry: ID {user.departmentHead.id}, Department: {dept_name}")
            else:
                print(f"      ❌ Missing role entry for {user.role}")
            print()
        
        # Check departments
        print("\n🏛️  DEPARTMENTS:")
        departments = await prisma.department.count()
        print(f"   Total departments: {departments}")
        
        # Check specialties
        print("\n📚 SPECIALTIES:")
        specialties = await prisma.specialty.count()
        print(f"   Total specialties: {specialties}")
        
        # Check levels
        print("\n📈 LEVELS:")
        levels = await prisma.level.count()
        print(f"   Total levels: {levels}")
        
        # Check groups
        print("\n👥 GROUPS:")
        groups = await prisma.group.count()
        print(f"   Total groups: {groups}")
        
        # Check subjects
        print("\n📖 SUBJECTS:")
        subjects = await prisma.subject.count()
        print(f"   Total subjects: {subjects}")
        
        # Test the admin user login credentials
        print("\n🔐 TESTING ADMIN CREDENTIALS:")
        admin_user = await prisma.user.find_unique(
            where={"login": "mohamedali.gh15@gmail.com"},
            include={"admin": True}
        )
        
        if admin_user:
            print(f"   ✅ Found admin user: {admin_user.firstName} {admin_user.lastName}")
            print(f"   📧 Email: {admin_user.email}")
            print(f"   🔑 Login: {admin_user.login}")
            print(f"   👤 Role: {admin_user.role}")
            if admin_user.admin:
                print(f"   🎯 Admin record exists: Level {admin_user.admin.level}")
            else:
                print("   ❌ No admin record found")
        else:
            print("   ❌ Admin user not found")
        
        print("\n✅ Database debug completed!")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
    finally:
        await prisma.disconnect()


async def main():
    """Main function"""
    await debug_database()


if __name__ == "__main__":
    asyncio.run(main())