#!/usr/bin/env python3

import asyncio
import random
from datetime import datetime, timedelta
from app.db.prisma_client import DatabaseManager
from app.core.security import hash_password

async def setup_wahid_students():
    """Create students, groups, and teaching assignments for wahid@gmail.com"""
    print("=== SETTING UP STUDENTS AND ASSIGNMENTS FOR WAHID ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # 1. Verify wahid exists as teacher
        print("\n1. Verifying wahid teacher...")
        user_wahid = await prisma.utilisateur.find_unique(
            where={"email": "wahid@gmail.com"},
            include={
                "enseignant": True
            }
        )
        
        if not user_wahid or not user_wahid.enseignant:
            print("❌ Wahid not found as teacher. Need to create teacher record first.")
            return
            
        teacher = user_wahid.enseignant
        print(f"✅ Teacher found: {teacher.nom} {teacher.prenom}")
        
        # 2. Get or create department
        print("\n2. Setting up department...")
        dept = await prisma.departement.find_first()
        if not dept:
            dept = await prisma.departement.create(data={
                "nom": "Informatique"
            })
        print(f"✅ Department: {dept.nom}")
        
        # 3. Get or create specialty
        print("\n3. Setting up specialty...")
        specialty = await prisma.specialite.find_first(
            where={"id_departement": dept.id}
        )
        if not specialty:
            specialty = await prisma.specialite.create(data={
                "nom": "Licence Informatique",
                "id_departement": dept.id
            })
        print(f"✅ Specialty: {specialty.nom}")
        
        # 4. Get or create level
        print("\n4. Setting up level...")
        level = await prisma.niveau.find_first(
            where={"id_specialite": specialty.id}
        )
        if not level:
            level = await prisma.niveau.create(data={
                "nom": "L3",
                "id_specialite": specialty.id
            })
        print(f"✅ Level: {level.nom}")
        
        # 5. Create groups for the teacher
        print("\n5. Creating groups...")
        groups_data = [
            {"nom": "L3-INFO-G1"},
            {"nom": "L3-INFO-G2"},
            {"nom": "L3-INFO-G3"}
        ]
        
        created_groups = []
        for group_data in groups_data:
            # Check if group exists
            existing_group = await prisma.groupe.find_first(
                where={
                    "nom": group_data["nom"],
                    "id_niveau": level.id
                }
            )
            
            if not existing_group:
                group = await prisma.groupe.create(data={
                    "nom": group_data["nom"],
                    "id_niveau": level.id
                })
                created_groups.append(group)
                print(f"✅ Created group: {group.nom}")
            else:
                created_groups.append(existing_group)
                print(f"✅ Using existing group: {existing_group.nom}")
        
        # 6. Create subjects for the teacher
        print("\n6. Creating subjects for wahid...")
        subjects_data = [
            {"nom": "Programmation Web", "id_specialite": specialty.id, "id_enseignant": teacher.id},
            {"nom": "Base de Données", "id_specialite": specialty.id, "id_enseignant": teacher.id},
            {"nom": "Algorithmes Avancés", "id_specialite": specialty.id, "id_enseignant": teacher.id}
        ]
        
        created_subjects = []
        for subject_data in subjects_data:
            # Check if subject exists
            existing_subject = await prisma.matiere.find_first(
                where={
                    "nom": subject_data["nom"],
                    "id_enseignant": teacher.id
                }
            )
            
            if not existing_subject:
                subject = await prisma.matiere.create(data=subject_data)
                created_subjects.append(subject)
                print(f"✅ Created subject: {subject.nom}")
            else:
                created_subjects.append(existing_subject)
                print(f"✅ Using existing subject: {existing_subject.nom}")
        
        # 7. Create students for each group
        print("\n7. Creating students...")
        student_names = [
            ("Ahmed", "Ben Ali"), ("Fatima", "Jlassi"), ("Mohamed", "Trabelsi"),
            ("Amina", "Kacem"), ("Youssef", "Mansour"), ("Leila", "Gharbi"),
            ("Karim", "Bouazizi"), ("Nadia", "Sfar"), ("Slim", "Mejri"),
            ("Salma", "Kammoun"), ("Omar", "Chebbi"), ("Ines", "Tlili"),
            ("Bilel", "Dhaoui"), ("Rania", "Mokrani"), ("Hedi", "Zouari"),
            ("Marwa", "Belaid"), ("Fares", "Sassi"), ("Yasmine", "Haddad"),
            ("Walid", "Chouchane"), ("Sonia", "Kouki"), ("Amine", "Lazaar"),
            ("Emna", "Turki"), ("Mehdi", "Ouali"), ("Jihen", "Agrebi")
        ]
        
        all_students = []
        for i, group in enumerate(created_groups):
            # Create 8 students per group
            group_students = []
            start_idx = i * 8
            end_idx = min(start_idx + 8, len(student_names))
            
            for j, (prenom, nom) in enumerate(student_names[start_idx:end_idx]):
                student_email = f"{prenom.lower()}.{nom.lower()}@student.iset.tn"
                
                # Check if student exists
                existing_student = await prisma.etudiant.find_unique(
                    where={"email": student_email}
                )
                
                if not existing_student:
                    # Create student
                    student = await prisma.etudiant.create(data={
                        "nom": nom,
                        "prenom": prenom,
                        "email": student_email,
                        "id_groupe": group.id,
                        "id_specialite": specialty.id
                    })
                    
                    # Create user account for student
                    hashed_password = hash_password("student123")
                    await prisma.utilisateur.create(data={
                        "nom": nom,
                        "prenom": prenom,
                        "email": student_email,
                        "role": "STUDENT",
                        "mdp_hash": hashed_password,
                        "etudiant_id": student.id
                    })
                    
                    group_students.append(student)
                    print(f"✅ Created student: {student.prenom} {student.nom} in {group.nom}")
                else:
                    group_students.append(existing_student)
                    print(f"✅ Using existing student: {existing_student.prenom} {existing_student.nom}")
            
            all_students.extend(group_students)
        
        # 8. Create room if needed
        print("\n8. Setting up room...")
        room = await prisma.salle.find_first()
        if not room:
            room = await prisma.salle.create(data={
                "code": "SALLE-001",
                "type": "LECTURE",
                "capacite": 40
            })
        print(f"✅ Room: {room.code}")
        
        # 9. Create schedule entries for today and next few days
        print("\n9. Creating schedule entries...")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        schedule_entries = []
        for day_offset in range(5):  # Create for next 5 days
            schedule_date = today + timedelta(days=day_offset)
            
            # Create 2 classes per day
            for hour in [8, 10]:  # 8:00 AM and 10:00 AM
                start_time = schedule_date.replace(hour=hour, minute=0)
                end_time = start_time + timedelta(hours=2)  # 2-hour classes
                
                # Rotate through subjects and groups
                subject = created_subjects[day_offset % len(created_subjects)]
                group = created_groups[hour // 10 % len(created_groups)]  # 8->0, 10->1
                
                # Check if schedule exists
                existing_schedule = await prisma.emploitemps.find_first(
                    where={
                        "date": schedule_date,
                        "heure_debut": start_time,
                        "id_enseignant": teacher.id,
                        "id_groupe": group.id
                    }
                )
                
                if not existing_schedule:
                    schedule = await prisma.emploitemps.create(data={
                        "date": schedule_date,
                        "heure_debut": start_time,
                        "heure_fin": end_time,
                        "id_salle": room.id,
                        "id_matiere": subject.id,
                        "id_groupe": group.id,
                        "id_enseignant": teacher.id,
                        "status": "PLANNED"
                    })
                    schedule_entries.append(schedule)
                    print(f"✅ Created schedule: {subject.nom} - {group.nom} on {schedule_date.strftime('%Y-%m-%d')} at {hour}:00")
                else:
                    schedule_entries.append(existing_schedule)
                    print(f"✅ Using existing schedule: {subject.nom} - {group.nom} on {schedule_date.strftime('%Y-%m-%d')} at {hour}:00")
        
        # 10. Create some sample absences
        print("\n10. Creating sample absences...")
        # Create a few absences for yesterday's classes (if any)
        yesterday = today - timedelta(days=1)
        yesterday_schedules = await prisma.emploitemps.find_many(
            where={
                "date": yesterday,
                "id_enseignant": teacher.id
            },
            include={"groupe": {"include": {"etudiants": True}}}
        )
        
        absence_count = 0
        for schedule in yesterday_schedules:
            if schedule.groupe.etudiants:
                # Create absences for 2-3 random students
                absent_students = random.sample(
                    schedule.groupe.etudiants, 
                    min(3, len(schedule.groupe.etudiants))
                )
                
                for student in absent_students:
                    # Check if absence already exists
                    existing_absence = await prisma.absence.find_first(
                        where={
                            "id_etudiant": student.id,
                            "id_emploitemps": schedule.id
                        }
                    )
                    
                    if not existing_absence:
                        motifs = ["Maladie", "Problème personnel", "Transport", "Urgence familiale"]
                        await prisma.absence.create(data={
                            "id_etudiant": student.id,
                            "id_emploitemps": schedule.id,
                            "motif": random.choice(motifs),
                            "statut": "unjustified"
                        })
                        absence_count += 1
                        print(f"✅ Created absence for {student.prenom} {student.nom}")
        
        print(f"\n🎉 SETUP COMPLETE!")
        print(f"✅ Created {len(created_groups)} groups")
        print(f"✅ Created {len(created_subjects)} subjects")
        print(f"✅ Created {len(all_students)} students")
        print(f"✅ Created {len(schedule_entries)} schedule entries")
        print(f"✅ Created {absence_count} sample absences")
        
        print(f"\n📋 SUMMARY FOR WAHID:")
        print(f"👨‍🏫 Teacher: {teacher.prenom} {teacher.nom}")
        print(f"🏢 Department: {dept.nom}")
        print(f"🎓 Specialty: {specialty.nom}")
        print(f"📚 Subjects: {', '.join([s.nom for s in created_subjects])}")
        print(f"👥 Groups: {', '.join([g.nom for g in created_groups])}")
        print(f"👨‍🎓 Total Students: {len(all_students)}")
        
        print(f"\n🧪 TEST DATA READY!")
        print(f"You can now test the absence system with:")
        print(f"• Login: wahid@gmail.com")
        print(f"• Password: dalighgh15")
        print(f"• Groups with students are available")
        print(f"• Schedule entries exist for the next 5 days")
        print(f"• Sample absences exist for testing")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_wahid_students())