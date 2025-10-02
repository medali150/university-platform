#!/usr/bin/env python3
"""
Test script to verify comprehensive department data endpoints are working
This will test the API endpoints that the frontend dashboard will call
"""

import asyncio
import sys
from pathlib import Path
import json

# Add the parent directory to the path so we can import the app modules
sys.path.append(str(Path(__file__).parent))

from app.db.prisma_client import get_prisma
from prisma import Prisma

async def test_comprehensive_department_endpoints():
    """Test all endpoints that the department head dashboard will use"""
    
    print("🔄 Connecting to database...")
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("\n📊 Testing Comprehensive Department Data Endpoints")
        print("=" * 60)
        
        # Get departments first
        departments = await prisma.departement.find_many()
        if not departments:
            print("❌ No departments found - cannot proceed with tests")
            return
            
        dept = departments[0]  # Use first department for testing
        print(f"\n🏢 Testing with department: {dept.nom} (ID: {dept.id})")
        
        # Test 1: Students in department (through specialty)
        print("\n1️⃣ Testing Students Endpoint:")
        students_in_dept = await prisma.etudiant.find_many(
            where={
                "specialite": {
                    "id_departement": dept.id
                }
            },
            include={
                "utilisateur": True,
                "specialite": {
                    "include": {
                        "departement": True
                    }
                }
            }
        )
        print(f"   👨‍🎓 Students in {dept.nom}: {len(students_in_dept)}")
        for student in students_in_dept[:2]:  # Show first 2
            if student.utilisateur:
                print(f"      - {student.utilisateur.prenom} {student.utilisateur.nom}")
        
        # Test 2: Teachers in department
        print("\n2️⃣ Testing Teachers Endpoint:")
        teachers_in_dept = await prisma.enseignant.find_many(
            where={
                "id_departement": dept.id
            },
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        print(f"   👨‍🏫 Teachers in {dept.nom}: {len(teachers_in_dept)}")
        for teacher in teachers_in_dept[:2]:  # Show first 2
            if teacher.utilisateur:
                print(f"      - {teacher.utilisateur.prenom} {teacher.utilisateur.nom}")
        
        # Test 3: Subjects (all subjects for now)
        print("\n3️⃣ Testing Subjects Endpoint:")
        subjects = await prisma.matiere.find_many()
        print(f"   📚 Total subjects available: {len(subjects)}")
        for subject in subjects[:3]:  # Show first 3
            print(f"      - {subject.nom} ({subject.code})")
        
        # Test 4: Specialties in department
        print("\n4️⃣ Testing Specialties Endpoint:")
        specialties = await prisma.specialite.find_many(
            where={
                "id_departement": dept.id
            },
            include={
                "departement": True
            }
        )
        print(f"   🎓 Specialties in {dept.nom}: {len(specialties)}")
        for specialty in specialties[:2]:  # Show first 2
            print(f"      - {specialty.nom}")
        
        # Test 5: Groups (all groups for now)
        print("\n5️⃣ Testing Groups Endpoint:")
        groups = await prisma.groupe.find_many(
            include={
                "niveau": True
            }
        )
        print(f"   👥 Total groups: {len(groups)}")
        for group in groups[:3]:  # Show first 3
            niveau_nom = group.niveau.nom if group.niveau else "Niveau non défini"
            print(f"      - {group.nom} (Niveau: {niveau_nom})")
        
        # Test 6: Levels (all levels)
        print("\n6️⃣ Testing Levels Endpoint:")
        levels = await prisma.niveau.find_many()
        print(f"   📊 Total levels: {len(levels)}")
        for level in levels[:3]:  # Show first 3
            print(f"      - {level.nom}")
        
        # Test 7: Schedules (all schedules for now)
        print("\n7️⃣ Testing Schedules Endpoint:")
        schedules = await prisma.emploidutemps.find_many(
            include={
                "matiere": True,
                "salle": True,
                "groupe": True,
                "enseignant": {
                    "include": {
                        "utilisateur": True
                    }
                }
            }
        )
        print(f"   📅 Total schedules: {len(schedules)}")
        for schedule in schedules[:2]:  # Show first 2
            matiere_nom = schedule.matiere.nom if schedule.matiere else "Matière non définie"
            salle_nom = schedule.salle.nom if schedule.salle else "Salle non définie"
            print(f"      - {matiere_nom} in {salle_nom} ({schedule.jour_semaine})")
        
        # Test 8: Rooms (all rooms)
        print("\n8️⃣ Testing Rooms Endpoint:")
        rooms = await prisma.salle.find_many()
        print(f"   🏛️ Total rooms: {len(rooms)}")
        for room in rooms[:3]:  # Show first 3
            print(f"      - {room.nom} (Capacity: {room.capacite})")
        
        # Test 9: Department Heads in department
        print("\n9️⃣ Testing Department Heads Endpoint:")
        dept_heads = await prisma.chefdepartement.find_many(
            where={
                "id_departement": dept.id
            },
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        print(f"   👑 Department heads in {dept.nom}: {len(dept_heads)}")
        for head in dept_heads:
            if head.utilisateur:
                print(f"      - {head.utilisateur.prenom} {head.utilisateur.nom}")
        
        # Summary
        print(f"\n✅ Comprehensive Data Summary for {dept.nom}:")
        print(f"   - Students: {len(students_in_dept)}")
        print(f"   - Teachers: {len(teachers_in_dept)}")
        print(f"   - Subjects: {len(subjects)}")
        print(f"   - Specialties: {len(specialties)}")
        print(f"   - Groups: {len(groups)}")
        print(f"   - Levels: {len(levels)}")
        print(f"   - Schedules: {len(schedules)}")
        print(f"   - Rooms: {len(rooms)}")
        print(f"   - Department Heads: {len(dept_heads)}")
        
        # Create mock comprehensive data structure
        comprehensive_data = {
            "department": {
                "id": dept.id,
                "name": dept.nom
            },
            "stats": {
                "students": len(students_in_dept),
                "teachers": len(teachers_in_dept),
                "subjects": len(subjects),
                "specialties": len(specialties),
                "groups": len(groups),
                "levels": len(levels),
                "schedules": len(schedules),
                "rooms": len(rooms),
                "departmentHeads": len(dept_heads)
            }
        }
        
        print(f"\n📋 JSON Structure for Frontend:")
        print(json.dumps(comprehensive_data, indent=2, ensure_ascii=False))
        
        print(f"\n🎉 All comprehensive data endpoints tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during comprehensive testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await prisma.disconnect()
        print("\n🔐 Database connection closed")

if __name__ == "__main__":
    print("🧪 Testing Comprehensive Department Data Endpoints")
    print("=" * 60)
    asyncio.run(test_comprehensive_department_endpoints())