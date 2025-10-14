#!/usr/bin/env python3
"""
Create a department head user for testing the schedule creator
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma import Prisma
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_department_head():
    prisma = Prisma()
    await prisma.connect()

    try:
        print("🎯 Creating department head user for schedule management testing...")

        # Hash password
        hashed_password = pwd_context.hash("depthead2025")

        # Create department head user
        dept_head_user = await prisma.utilisateur.create(
            data={
                "prenom": "Sarah",
                "nom": "MANAGER",
                "email": "sarah.manager@university.edu",
                "mot_de_passe": hashed_password,
                "role": "department_head",
                "created_at": "2025-01-01T00:00:00.000Z"
            }
        )

        print(f"✅ Created department head user: {dept_head_user.prenom} {dept_head_user.nom}")
        print(f"   Email: {dept_head_user.email}")
        print(f"   Password: depthead2025")
        print(f"   Role: {dept_head_user.role}")
        print(f"   ID: {dept_head_user.id}")

        # Find or create a department to associate with
        department = await prisma.department.find_first()
        if not department:
            department = await prisma.department.create(
                data={
                    "name": "Informatique",
                    "description": "Département des Sciences Informatiques"
                }
            )
            print(f"✅ Created department: {department.name}")
        else:
            print(f"✅ Using existing department: {department.name}")

        # Create department head info
        dept_head_info = await prisma.departmenthead.create(
            data={
                "user_id": dept_head_user.id,
                "department_id": department.id
            }
        )

        print(f"✅ Created department head info linking user to department")

        print("\n" + "="*60)
        print("🎓 DEPARTMENT HEAD SCHEDULE CREATOR TEST ACCOUNT")
        print("="*60)
        print(f"URL: http://localhost:3000/dashboard/department-head/schedule")
        print(f"Email: sarah.manager@university.edu")
        print(f"Password: depthead2025")
        print(f"Department: {department.name}")
        print("="*60)

        # Verify some groups exist
        groups = await prisma.studentgroup.find_many()
        if groups:
            print(f"\n✅ Found {len(groups)} student groups available:")
            for group in groups[:5]:  # Show first 5
                print(f"   - {group.name}")
        else:
            print("\n⚠️  No student groups found. Creating sample groups...")
            sample_groups = ['LI 02', 'LI 04', 'LI 05', 'LI 10', 'SI 01', 'SI 03']
            for group_name in sample_groups:
                await prisma.studentgroup.create(
                    data={
                        "name": group_name,
                        "level": "L2" if group_name.startswith('LI') else "L3"
                    }
                )
                print(f"   ✅ Created group: {group_name}")

        print("\n🚀 Ready to test department head schedule creator!")
        print("   1. Go to: http://localhost:3000/dashboard/department-head/schedule")
        print("   2. Login with the credentials above")
        print("   3. Select a group and start creating schedules!")

    except Exception as e:
        print(f"❌ Error creating department head user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_department_head())