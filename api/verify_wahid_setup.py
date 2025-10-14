#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager

async def verify_wahid_setup():
    """Verify that wahid's setup is complete in the database"""
    print("=== VERIFYING WAHID'S SETUP IN DATABASE ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # 1. Verify wahid teacher exists
        print("\n1. 👨‍🏫 Checking Wahid teacher...")
        user_wahid = await prisma.utilisateur.find_unique(
            where={"email": "wahid@gmail.com"},
            include={
                "enseignant": {
                    "include": {
                        "departement": True,
                        "matieres": True
                    }
                }
            }
        )
        
        if user_wahid and user_wahid.enseignant:
            teacher = user_wahid.enseignant
            print(f"✅ Teacher: {teacher.prenom} {teacher.nom}")
            print(f"   Email: {teacher.email}")
            print(f"   Department: {teacher.departement.nom}")
            print(f"   Subjects: {len(teacher.matieres)}")
            for subject in teacher.matieres:
                print(f"     - {subject.nom}")
        else:
            print("❌ Wahid teacher not found")
            return
        
        # 2. Check groups
        print("\n2. 👥 Checking Groups...")
        groups = await prisma.groupe.find_many(
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                },
                "etudiants": True
            }
        )
        
        print(f"✅ Total groups: {len(groups)}")
        for group in groups:
            print(f"   - {group.nom}: {len(group.etudiants)} students")
        
        # 3. Check students
        print("\n3. 👨‍🎓 Checking Students...")
        students = await prisma.etudiant.find_many(
            include={
                "groupe": True,
                "specialite": True
            }
        )
        
        print(f"✅ Total students: {len(students)}")
        
        # Group students by group
        students_by_group = {}
        for student in students:
            group_name = student.groupe.nom
            if group_name not in students_by_group:
                students_by_group[group_name] = []
            students_by_group[group_name].append(student)
        
        for group_name, group_students in students_by_group.items():
            print(f"   📚 {group_name}: {len(group_students)} students")
            for student in group_students[:3]:  # Show first 3
                print(f"     - {student.prenom} {student.nom} ({student.email})")
            if len(group_students) > 3:
                print(f"     ... and {len(group_students) - 3} more")
        
        # 4. Check schedule
        print("\n4. 📅 Checking Schedule...")
        schedules = await prisma.emploitemps.find_many(
            where={"id_enseignant": teacher.id},
            include={
                "matiere": True,
                "groupe": True,
                "salle": True
            }
        )
        
        print(f"✅ Total schedule entries: {len(schedules)}")
        
        # Group by date
        from datetime import datetime
        schedules_by_date = {}
        for schedule in schedules:
            date_str = schedule.date.strftime("%Y-%m-%d")
            if date_str not in schedules_by_date:
                schedules_by_date[date_str] = []
            schedules_by_date[date_str].append(schedule)
        
        for date_str, day_schedules in list(schedules_by_date.items())[:5]:  # Show first 5 days
            print(f"   📅 {date_str}: {len(day_schedules)} classes")
            for schedule in day_schedules:
                time_str = schedule.heure_debut.strftime("%H:%M")
                print(f"     - {time_str} | {schedule.matiere.nom} | {schedule.groupe.nom} | {schedule.salle.code}")
        
        # 5. Check absences
        print("\n5. ✏️ Checking Absences...")
        absences = await prisma.absence.find_many(
            include={
                "etudiant": True,
                "emploitemps": {
                    "include": {
                        "matiere": True,
                        "groupe": True
                    }
                }
            }
        )
        
        print(f"✅ Total absences: {len(absences)}")
        for absence in absences[:5]:  # Show first 5
            student = absence.etudiant
            schedule = absence.emploitemps
            print(f"   - {student.prenom} {student.nom} | {schedule.matiere.nom} | {schedule.groupe.nom} | {absence.motif}")
        
        # 6. Summary for testing
        print(f"\n🎯 TESTING SUMMARY:")
        print(f"✅ Teacher: wahid@gmail.com (ID: {teacher.id})")
        print(f"✅ Department: {teacher.departement.nom}")
        print(f"✅ Subjects: {len(teacher.matieres)} subjects assigned")
        print(f"✅ Groups: {len(groups)} groups available")
        print(f"✅ Students: {len(students)} students in total")
        print(f"✅ Schedule: {len(schedules)} classes scheduled")
        print(f"✅ Absences: {len(absences)} sample absences")
        
        print(f"\n🧪 API TESTING READY:")
        print(f"• Teacher ID: {teacher.id}")
        print(f"• Available groups: {', '.join([g.nom for g in groups])}")
        print(f"• Students per group: {[len(g.etudiants) for g in groups]}")
        print(f"• Schedule entries for next 5 days available")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"1. Start the API server: python -m uvicorn main:app --reload --port 8000")
        print(f"2. Test login: POST /auth/login with {{\"email\": \"wahid@gmail.com\", \"password\": \"dalighgh15\"}}")
        print(f"3. Test teacher endpoints with the Bearer token")
        print(f"4. Use the frontend absence management system")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_wahid_setup())