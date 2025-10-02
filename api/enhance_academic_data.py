"""
Data Enhancement Script: Add realistic academic structure

This script adds realistic departments, specialties, levels, and groups
to make the university system more functional.
"""

import asyncio
from prisma import Prisma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def enhance_academic_structure():
    """Add realistic academic structure to the database"""
    
    print("🎓 Starting Data Enhancement: Academic Structure")
    print("=" * 50)
    
    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Academic structure data
        departments_data = [
            {
                "name": "Computer Science Department",
                "specialties": [
                    {
                        "name": "Software Engineering",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    },
                    {
                        "name": "Artificial Intelligence",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    },
                    {
                        "name": "Cybersecurity",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    }
                ]
            },
            {
                "name": "Mathematics Department",
                "specialties": [
                    {
                        "name": "Applied Mathematics",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    },
                    {
                        "name": "Statistics",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    }
                ]
            },
            {
                "name": "Physics Department",
                "specialties": [
                    {
                        "name": "Theoretical Physics",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    },
                    {
                        "name": "Applied Physics",
                        "levels": ["License 1", "License 2", "License 3", "Master 1", "Master 2"]
                    }
                ]
            }
        ]
        
        # Check if we already have the enhanced structure
        existing_depts = await prisma.department.count()
        if existing_depts > 1:  # We already created "General Department" in the fix script
            print("📋 Enhanced academic structure already exists. Skipping creation.")
            await print_current_structure(prisma)
            return
        
        created_departments = 0
        created_specialties = 0
        created_levels = 0
        created_groups = 0
        
        # Create the academic structure
        for dept_data in departments_data:
            print(f"\n🏛️  Creating department: {dept_data['name']}")
            
            department = await prisma.department.create(
                data={"name": dept_data["name"]}
            )
            created_departments += 1
            
            for specialty_data in dept_data["specialties"]:
                print(f"   📚 Creating specialty: {specialty_data['name']}")
                
                specialty = await prisma.specialty.create(
                    data={
                        "name": specialty_data["name"],
                        "departmentId": department.id
                    }
                )
                created_specialties += 1
                
                for level_name in specialty_data["levels"]:
                    print(f"      📈 Creating level: {level_name}")
                    
                    level = await prisma.level.create(
                        data={
                            "name": level_name,
                            "specialtyId": specialty.id
                        }
                    )
                    created_levels += 1
                    
                    # Create groups for each level (A, B, C)
                    for group_name in ["Group A", "Group B", "Group C"]:
                        full_group_name = f"{level_name} - {group_name}"
                        print(f"         👥 Creating group: {full_group_name}")
                        
                        await prisma.group.create(
                            data={
                                "name": full_group_name,
                                "levelId": level.id
                            }
                        )
                        created_groups += 1
        
        print("\n" + "=" * 50)
        print("🎯 Academic Structure Enhancement Summary:")
        print(f"   Departments created: {created_departments}")
        print(f"   Specialties created: {created_specialties}")
        print(f"   Levels created: {created_levels}")
        print(f"   Groups created: {created_groups}")
        
        # Reassign users to better positions
        print("\n🔄 Reassigning users to new structure...")
        await reassign_users(prisma)
        
        # Print the current structure
        await print_current_structure(prisma)
        
        print("\n✅ Academic structure enhancement completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
    finally:
        await prisma.disconnect()


async def reassign_users(prisma):
    """Reassign users to the new academic structure"""
    
    # Get departments
    cs_dept = await prisma.department.find_first(
        where={"name": "Computer Science Department"}
    )
    math_dept = await prisma.department.find_first(
        where={"name": "Mathematics Department"}
    )
    physics_dept = await prisma.department.find_first(
        where={"name": "Physics Department"}
    )
    
    # Get specialties and groups
    software_eng = await prisma.specialty.find_first(
        where={"name": "Software Engineering"},
        include={"levels": {"include": {"groups": True}}}
    )
    
    ai_specialty = await prisma.specialty.find_first(
        where={"name": "Artificial Intelligence"},
        include={"levels": {"include": {"groups": True}}}
    )
    
    # Update teachers
    teachers = await prisma.teacher.find_many(include={"user": True})
    for i, teacher in enumerate(teachers):
        dept = [cs_dept, math_dept, physics_dept][i % 3]
        if dept:
            await prisma.teacher.update(
                where={"id": teacher.id},
                data={"departmentId": dept.id}
            )
            print(f"   ✅ Reassigned teacher {teacher.user.firstName} {teacher.user.lastName} to {dept.name}")
    
    # Update students
    students = await prisma.student.find_many(include={"user": True})
    for i, student in enumerate(students):
        if software_eng and software_eng.levels:
            level = software_eng.levels[0]  # License 1
            if level.groups:
                group = level.groups[i % len(level.groups)]
                await prisma.student.update(
                    where={"id": student.id},
                    data={
                        "groupId": group.id,
                        "specialtyId": software_eng.id
                    }
                )
                print(f"   ✅ Reassigned student {student.user.firstName} {student.user.lastName} to {group.name}")
    
    # Update department heads
    dept_heads = await prisma.department_head.find_many(include={"user": True})
    for i, dept_head in enumerate(dept_heads):
        dept = [cs_dept, math_dept, physics_dept][i % 3]
        if dept:
            await prisma.department_head.update(
                where={"id": dept_head.id},
                data={"departmentId": dept.id}
            )
            print(f"   ✅ Reassigned dept head {dept_head.user.firstName} {dept_head.user.lastName} to {dept.name}")


async def print_current_structure(prisma):
    """Print the current academic structure"""
    
    print("\n📊 Current Academic Structure:")
    print("=" * 50)
    
    departments = await prisma.department.find_many(
        include={
            "specialties": {
                "include": {
                    "levels": {
                        "include": {"groups": True}
                    }
                }
            },
            "teachers": {"include": {"user": True}},
            "departmentHead": {"include": {"user": True}}
        }
    )
    
    for dept in departments:
        print(f"\n🏛️  {dept.name}")
        if dept.departmentHead:
            print(f"   👨‍💼 Head: {dept.departmentHead.user.firstName} {dept.departmentHead.user.lastName}")
        
        print(f"   👨‍🏫 Teachers: {len(dept.teachers)}")
        for teacher in dept.teachers:
            print(f"      - {teacher.user.firstName} {teacher.user.lastName}")
        
        for specialty in dept.specialties:
            print(f"   📚 {specialty.name}")
            for level in specialty.levels:
                print(f"      📈 {level.name}")
                for group in level.groups:
                    print(f"         👥 {group.name}")


async def main():
    """Main function"""
    await enhance_academic_structure()


if __name__ == "__main__":
    asyncio.run(main())