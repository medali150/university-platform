#!/usr/bin/env python3
"""
Test script to verify API endpoints for fetching real data
Tests departments, students, teachers, and department heads endpoints
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app modules
sys.path.append(str(Path(__file__).parent))

from app.db.prisma_client import get_prisma
from prisma import Prisma

async def test_data_fetching():
    """Test fetching real data from the database"""
    
    print("🔄 Connecting to database...")
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("\n📊 Testing Data Fetching Endpoints")
        print("=" * 50)
        
        # Test 1: Fetch Departments
        print("\n1️⃣ Testing Departments:")
        departments = await prisma.departement.find_many()
        print(f"   📍 Found {len(departments)} departments:")
        for dept in departments[:3]:  # Show first 3
            print(f"      - {dept.nom} (ID: {dept.id})")
        if len(departments) > 3:
            print(f"      ... and {len(departments) - 3} more")
        
        # Test 2: Fetch Students (using French schema)
        print("\n2️⃣ Testing Students:")
        # Get students through the etudiant table
        students = await prisma.etudiant.find_many(
            include={
                "utilisateur": True,  # Include user data
                "specialite": {
                    "include": {
                        "departement": True
                    }
                }
            }
        )
        print(f"   👨‍🎓 Found {len(students)} students:")
        for student in students[:3]:  # Show first 3
            if student.utilisateur:
                print(f"      - {student.utilisateur.prenom} {student.utilisateur.nom} ({student.utilisateur.email})")
                if student.specialite:
                    print(f"        Specialité: {student.specialite.nom}")
                    if student.specialite.departement:
                        print(f"        Département: {student.specialite.departement.nom}")
        if len(students) > 3:
            print(f"      ... and {len(students) - 3} more")
        
        # Test 3: Fetch Teachers (using French schema)
        print("\n3️⃣ Testing Teachers:")
        teachers = await prisma.enseignant.find_many(
            include={
                "utilisateur": True,  # Include user data
                "departement": True   # Include department
            }
        )
        print(f"   👨‍🏫 Found {len(teachers)} teachers:")
        for teacher in teachers[:3]:  # Show first 3
            if teacher.utilisateur:
                print(f"      - {teacher.utilisateur.prenom} {teacher.utilisateur.nom} ({teacher.utilisateur.email})")
                if teacher.departement:
                    print(f"        Département: {teacher.departement.nom}")
        if len(teachers) > 3:
            print(f"      ... and {len(teachers) - 3} more")
        
        # Test 4: Fetch Department Heads (using French schema)
        print("\n4️⃣ Testing Department Heads:")
        dept_heads = await prisma.chefdepartement.find_many(
            include={
                "utilisateur": True,  # Include user data
                "departement": True   # Include department
            }
        )
        print(f"   👑 Found {len(dept_heads)} department heads:")
        for head in dept_heads[:3]:  # Show first 3
            if head.utilisateur:
                print(f"      - {head.utilisateur.prenom} {head.utilisateur.nom} ({head.utilisateur.email})")
                if head.departement:
                    print(f"        Chef de: {head.departement.nom}")
        if len(dept_heads) > 3:
            print(f"      ... and {len(dept_heads) - 3} more")
        
        # Test 5: Test Department Filtering
        if departments:
            dept_id = departments[0].id
            dept_name = departments[0].nom
            print(f"\n5️⃣ Testing Department Filtering (for {dept_name}):")
            
            # Filter students by department (through specialty)
            dept_students = await prisma.etudiant.find_many(
                where={
                    "specialite": {
                        "id_departement": dept_id
                    }
                },
                include={
                    "utilisateur": True,
                    "specialite": True
                }
            )
            print(f"   👨‍🎓 Students in {dept_name}: {len(dept_students)}")
            
            # Filter teachers by department
            dept_teachers = await prisma.enseignant.find_many(
                where={
                    "id_departement": dept_id
                },
                include={
                    "utilisateur": True
                }
            )
            print(f"   👨‍🏫 Teachers in {dept_name}: {len(dept_teachers)}")
            
            # Filter department heads by department
            dept_heads_filtered = await prisma.chefdepartement.find_many(
                where={
                    "id_departement": dept_id
                },
                include={
                    "utilisateur": True
                }
            )
            print(f"   👑 Department heads in {dept_name}: {len(dept_heads_filtered)}")
        
        print("\n✅ All data fetching tests completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Départements: {len(departments)}")
        print(f"   - Étudiants: {len(students)}")
        print(f"   - Enseignants: {len(teachers)}")
        print(f"   - Chefs de département: {len(dept_heads)}")
        
    except Exception as e:
        print(f"\n❌ Error during data fetching test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await prisma.disconnect()
        print("\n🔐 Database connection closed")

if __name__ == "__main__":
    print("🧪 Testing Real Data Fetching from Database")
    print("=" * 50)
    asyncio.run(test_data_fetching())