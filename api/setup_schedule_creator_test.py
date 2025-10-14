#!/usr/bin/env python3
"""
Comprehensive setup for Department Head Schedule Creator Testing
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma import Prisma
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup_complete_testing_environment():
    prisma = Prisma()
    await prisma.connect()

    try:
        print("🎯 Setting up complete testing environment for Department Head Schedule Creator...")

        # Hash password
        hashed_password = pwd_context.hash("chef2025")

        # 1. Create department head user
        dept_head_user = await prisma.utilisateur.upsert(
            where={"email": "chef.departement@university.edu"},
            data={
                "create": {
                    "prenom": "Sarah",
                    "nom": "CHEF",
                    "email": "chef.departement@university.edu",
                    "mot_de_passe": hashed_password,
                    "role": "department_head",
                    "created_at": "2025-01-01T00:00:00.000Z"
                },
                "update": {
                    "mot_de_passe": hashed_password,
                    "role": "department_head"
                }
            }
        )

        print(f"✅ Department Head User: {dept_head_user.prenom} {dept_head_user.nom}")
        print(f"   Email: {dept_head_user.email}")
        print(f"   Password: chef2025")

        # 2. Ensure department exists
        department = await prisma.department.upsert(
            where={"name": "Informatique"},
            data={
                "create": {
                    "name": "Informatique",
                    "description": "Département des Sciences Informatiques"
                },
                "update": {
                    "description": "Département des Sciences Informatiques"
                }
            }
        )
        print(f"✅ Department: {department.name}")

        # 3. Link department head to department
        dept_head_info = await prisma.departmenthead.upsert(
            where={"user_id": dept_head_user.id},
            data={
                "create": {
                    "user_id": dept_head_user.id,
                    "department_id": department.id
                },
                "update": {
                    "department_id": department.id
                }
            }
        )
        print(f"✅ Department Head Info linked")

        # 4. Create student groups for testing
        groups_to_create = [
            {"name": "LI 02", "level": "L2"},
            {"name": "LI 04", "level": "L2"},
            {"name": "LI 05", "level": "L2"},
            {"name": "LI 10", "level": "L2"},
            {"name": "SI 01", "level": "L3"},
            {"name": "SI 03", "level": "L3"},
            {"name": "AMPHI", "level": "ALL"}
        ]

        for group_data in groups_to_create:
            group = await prisma.studentgroup.upsert(
                where={"name": group_data["name"]},
                data={
                    "create": group_data,
                    "update": {"level": group_data["level"]}
                }
            )
            print(f"   ✅ Group: {group.name}")

        # 5. Create teachers for schedule assignment
        teachers_to_create = [
            {"name": "Abdelkader MAATALLAH", "email": "abdelkader.maatallah@university.edu"},
            {"name": "Ahmed NEFZAOUI", "email": "ahmed.nefzaoui@university.edu"},
            {"name": "Wahid HAMDI", "email": "wahid.hamdi@university.edu"},
            {"name": "Dziriya ARFAOUI", "email": "dziriya.arfaoui@university.edu"},
            {"name": "Haithem HAFSI", "email": "haithem.hafsi@university.edu"},
            {"name": "Mariem JERIDI", "email": "mariem.jeridi@university.edu"},
            {"name": "Mohamed TOUMI", "email": "mohamed.toumi@university.edu"}
        ]

        for teacher_data in teachers_to_create:
            teacher = await prisma.teacher.upsert(
                where={"name": teacher_data["name"]},
                data={
                    "create": {
                        "name": teacher_data["name"],
                        "email": teacher_data["email"],
                        "department_id": department.id
                    },
                    "update": {
                        "email": teacher_data["email"],
                        "department_id": department.id
                    }
                }
            )
            print(f"   ✅ Teacher: {teacher.name}")

        # 6. Create subjects for course assignment
        subjects_to_create = [
            {"name": "Développement Mobile", "code": "DEV-MOB", "credits": 3},
            {"name": "Environnement de développement", "code": "ENV-DEV", "credits": 2},
            {"name": "Atelier développement Mobile natif", "code": "AT-MOB-NAT", "credits": 3},
            {"name": "Atelier Framework cross-platform", "code": "AT-CROSS", "credits": 3},
            {"name": "Web 3.0", "code": "WEB-30", "credits": 3},
            {"name": "Preparing TOEIC", "code": "TOEIC", "credits": 2},
            {"name": "Projet d'Intégration", "code": "PROJ-INT", "credits": 4},
            {"name": "Méthodologie de Conception Objet", "code": "MCO", "credits": 3},
            {"name": "Atelier Base de Données Avancée", "code": "AT-BDA", "credits": 3},
            {"name": "SOA", "code": "SOA", "credits": 3},
            {"name": "Technique de recherche d'emploi et marketing de soi", "code": "TRE-MS", "credits": 2},
            {"name": "Atelier SOA", "code": "AT-SOA", "credits": 3},
            {"name": "Gestion des données Massives", "code": "GDM", "credits": 3}
        ]

        for subject_data in subjects_to_create:
            subject = await prisma.subject.upsert(
                where={"code": subject_data["code"]},
                data={
                    "create": {
                        "name": subject_data["name"],
                        "code": subject_data["code"],
                        "credits": subject_data["credits"],
                        "department_id": department.id
                    },
                    "update": {
                        "name": subject_data["name"],
                        "credits": subject_data["credits"],
                        "department_id": department.id
                    }
                }
            )
            print(f"   ✅ Subject: {subject.name}")

        # 7. Create rooms for schedule assignment
        rooms_to_create = [
            {"name": "AMPHI", "capacity": 200, "type": "Amphithéâtre"},
            {"name": "Salle A1", "capacity": 30, "type": "Salle de cours"},
            {"name": "Salle A2", "capacity": 30, "type": "Salle de cours"},
            {"name": "Lab Info", "capacity": 25, "type": "Laboratoire"},
            {"name": "Atelier", "capacity": 20, "type": "Atelier"},
            {"name": "TI 11", "capacity": 30, "type": "Salle informatique"},
            {"name": "TI 12", "capacity": 30, "type": "Salle informatique"},
            {"name": "DSI 31", "capacity": 25, "type": "Salle spécialisée"},
            {"name": "RSI 21", "capacity": 25, "type": "Salle réseaux"}
        ]

        for room_data in rooms_to_create:
            room = await prisma.room.upsert(
                where={"name": room_data["name"]},
                data={
                    "create": room_data,
                    "update": {
                        "capacity": room_data["capacity"],
                        "type": room_data["type"]
                    }
                }
            )
            print(f"   ✅ Room: {room.name} ({room.capacity} places)")

        print("\n" + "="*80)
        print("🎓 DEPARTMENT HEAD SCHEDULE CREATOR - COMPLETE TESTING ENVIRONMENT")
        print("="*80)
        print(f"🔐 LOGIN CREDENTIALS:")
        print(f"   Frontend URL: http://localhost:3000/dashboard/department-head/schedule")
        print(f"   Email: chef.departement@university.edu")
        print(f"   Password: chef2025")
        print(f"   Role: Department Head")
        print()
        print(f"📊 CREATED RESOURCES:")
        print(f"   • {len(groups_to_create)} Student Groups (LI 02, LI 04, SI 01, etc.)")
        print(f"   • {len(teachers_to_create)} Teachers (Abdelkader MAATALLAH, Ahmed NEFZAOUI, etc.)")
        print(f"   • {len(subjects_to_create)} Subjects (Développement Mobile, Web 3.0, SOA, etc.)")
        print(f"   • {len(rooms_to_create)} Rooms (AMPHI, Lab Info, TI 11, etc.)")
        print()
        print(f"🎯 FEATURES TO TEST:")
        print(f"   ✅ Empty timetable like the image you provided")
        print(f"   ✅ Click cells to add/edit courses")
        print(f"   ✅ Drag & drop support")
        print(f"   ✅ Templates for quick setup")
        print(f"   ✅ Bulk editing mode")
        print(f"   ✅ Conflict detection")
        print(f"   ✅ Statistics view")
        print(f"   ✅ Advanced view with enhanced UI")
        print(f"   ✅ Group switching")
        print(f"   ✅ Week navigation")
        print()
        print(f"🚀 NEXT STEPS:")
        print(f"   1. Start frontend: cd frontend && npm run dev")
        print(f"   2. Start backend: cd api && uvicorn main:app --reload")
        print(f"   3. Login with credentials above")
        print(f"   4. Test the advanced schedule creator!")
        print("="*80)

    except Exception as e:
        print(f"❌ Error setting up testing environment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_complete_testing_environment())