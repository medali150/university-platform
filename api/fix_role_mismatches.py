"""
Fix role mismatches and missing records
"""
import asyncio
from prisma import Prisma

async def fix_role_mismatches():
    """Fix users who have roles but missing corresponding records"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔧 FIXING ROLE MISMATCHES")
        print("=" * 60)
        
        # Find users with TEACHER role but no teacher record
        teachers_without_record = await prisma.user.find_many(
            where={
                "role": "TEACHER",
                "teacher": None
            }
        )
        
        print(f"👨‍🏫 Found {len(teachers_without_record)} teachers without teacher records:")
        
        for user in teachers_without_record:
            print(f"   • {user.firstName} {user.lastName} ({user.login})")
            
            # Get available departments
            departments = await prisma.department.find_many()
            if departments:
                # Create teacher record with first available department
                teacher = await prisma.teacher.create(
                    data={
                        "userId": user.id,
                        "departmentId": departments[0].id
                    }
                )
                print(f"     ✅ Created teacher record: {teacher.id} (assigned to {departments[0].name})")
            else:
                print(f"     ❌ No departments available to assign teacher")
        
        # Find users with DEPARTMENT_HEAD role but no department head record
        dept_heads_without_record = await prisma.user.find_many(
            where={
                "role": "DEPARTMENT_HEAD",
                "departmentHead": None
            }
        )
        
        print(f"\n👨‍💼 Found {len(dept_heads_without_record)} dept heads without dept head records:")
        
        for user in dept_heads_without_record:
            print(f"   • {user.firstName} {user.lastName} ({user.login})")
            
            # We need a department for dept heads, let's check available departments
            departments = await prisma.department.find_many()
            if departments:
                # Use first available department for now
                dept_head = await prisma.departmentHead.create(
                    data={
                        "userId": user.id,
                        "departmentId": departments[0].id
                    }
                )
                print(f"     ✅ Created dept head record: {dept_head.id} (assigned to {departments[0].name})")
            else:
                print(f"     ❌ No departments available to assign")
        
        # Find users with STUDENT role but no student record
        students_without_record = await prisma.user.find_many(
            where={
                "role": "STUDENT",
                "student": None
            }
        )
        
        print(f"\n👨‍🎓 Found {len(students_without_record)} students without student records:")
        
        for user in students_without_record:
            print(f"   • {user.firstName} {user.lastName} ({user.login})")
            
            # Get available groups and specialties
            groups = await prisma.group.find_many()
            specialties = await prisma.specialty.find_many()
            
            if groups and specialties:
                # Create student record with first available group and specialty
                student = await prisma.student.create(
                    data={
                        "userId": user.id,
                        "groupId": groups[0].id,
                        "specialtyId": specialties[0].id
                    }
                )
                print(f"     ✅ Created student record: {student.id} (group: {groups[0].name}, specialty: {specialties[0].name})")
            else:
                print(f"     ❌ Missing groups ({len(groups)}) or specialties ({len(specialties)}) to assign student")
        
        print(f"\n🎉 Fixed role mismatches!")
        
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_role_mismatches())