#!/usr/bin/env python3
"""
Complete Database Population Script
Creates comprehensive test data including:
- Departments, Specialties, Levels (Niveaux), Groups
- Subjects (Matières) with coefficients
- Teachers, Students, Rooms (Salles)
- Schedule entries for testing absences
"""
import asyncio
import bcrypt
from prisma import Prisma
from datetime import datetime, timedelta, time
import random

# Password for all test users
TEST_PASSWORD = "Test123!"

# Department and specialty configuration
DEPARTMENTS_CONFIG = {
    "Technologie d'Informatique": {
        "code": "TI",
        "specialties": [
            {
                "name": "Développement des Systèmes d'Information",
                "code": "DSI",
                "levels": [
                    {"name": "Licence 1 DSI", "code": "L1-DSI"},
                    {"name": "Licence 2 DSI", "code": "L2-DSI"},
                    {"name": "Licence 3 DSI", "code": "L3-DSI"}
                ]
            },
            {
                "name": "Réseaux et Télécommunications",
                "code": "RT",
                "levels": [
                    {"name": "Licence 1 RT", "code": "L1-RT"},
                    {"name": "Licence 2 RT", "code": "L2-RT"},
                    {"name": "Licence 3 RT", "code": "L3-RT"}
                ]
            }
        ],
        "subjects": [
            {"name": "Programmation Orientée Objet", "code": "POO", "coefficient": 3.0},
            {"name": "Base de Données", "code": "BD", "coefficient": 2.5},
            {"name": "Développement Web", "code": "WEB", "coefficient": 2.5},
            {"name": "Réseaux Informatiques", "code": "RESEAUX", "coefficient": 2.5},
            {"name": "Systèmes d'Exploitation", "code": "SE", "coefficient": 2.0},
            {"name": "Algorithmique", "code": "ALGO", "coefficient": 3.0},
            {"name": "Structures de Données", "code": "SD", "coefficient": 2.5},
            {"name": "Sécurité Informatique", "code": "SECU", "coefficient": 2.0}
        ]
    },
    "Génie Mécanique": {
        "code": "GM",
        "specialties": [
            {
                "name": "Génie Mécanique - Production",
                "code": "GMP",
                "levels": [
                    {"name": "Licence 1 GMP", "code": "L1-GMP"},
                    {"name": "Licence 2 GMP", "code": "L2-GMP"},
                    {"name": "Licence 3 GMP", "code": "L3-GMP"}
                ]
            }
        ],
        "subjects": [
            {"name": "Mécanique des Fluides", "code": "MF", "coefficient": 3.0},
            {"name": "Thermodynamique", "code": "THERMO", "coefficient": 2.5},
            {"name": "Résistance des Matériaux", "code": "RDM", "coefficient": 3.0},
            {"name": "Fabrication Mécanique", "code": "FAB", "coefficient": 2.0}
        ]
    },
    "Génie Électrique": {
        "code": "GE",
        "specialties": [
            {
                "name": "Génie Électrique - Automatique",
                "code": "GEA",
                "levels": [
                    {"name": "Licence 1 GEA", "code": "L1-GEA"},
                    {"name": "Licence 2 GEA", "code": "L2-GEA"},
                    {"name": "Licence 3 GEA", "code": "L3-GEA"}
                ]
            }
        ],
        "subjects": [
            {"name": "Électronique de Puissance", "code": "EP", "coefficient": 3.0},
            {"name": "Automatique", "code": "AUTO", "coefficient": 2.5},
            {"name": "Circuits Électriques", "code": "CE", "coefficient": 2.5}
        ]
    }
}

# Rooms configuration
ROOMS_CONFIG = [
    # Amphithéâtres
    {"code": "AMPHA", "type": "LECTURE", "capacite": 200},
    {"code": "AMPHB", "type": "LECTURE", "capacite": 150},
    
    # Salles de cours
    {"code": "A101", "type": "LECTURE", "capacite": 40},
    {"code": "A102", "type": "LECTURE", "capacite": 35},
    {"code": "A103", "type": "LECTURE", "capacite": 40},
    {"code": "A201", "type": "LECTURE", "capacite": 45},
    {"code": "A202", "type": "LECTURE", "capacite": 40},
    {"code": "B101", "type": "LECTURE", "capacite": 35},
    {"code": "B102", "type": "LECTURE", "capacite": 40},
    {"code": "B201", "type": "LECTURE", "capacite": 35},
    
    # Laboratoires informatique
    {"code": "LI1", "type": "LAB", "capacite": 30},
    {"code": "LI2", "type": "LAB", "capacite": 25},
    {"code": "LI3", "type": "LAB", "capacite": 30},
    {"code": "LI4", "type": "LAB", "capacite": 28},
    
    # Laboratoires spécialisés
    {"code": "LM1", "type": "LAB", "capacite": 20},
    {"code": "LE1", "type": "LAB", "capacite": 25},
    {"code": "LA1", "type": "LAB", "capacite": 20},
    
    # Ateliers
    {"code": "AM1", "type": "OTHER", "capacite": 25},
    {"code": "AE1", "type": "OTHER", "capacite": 20}
]

# Teacher names
TEACHER_NAMES = [
    ("Mohamed", "Ben Ali"),
    ("Fatma", "Trabelsi"),
    ("Ahmed", "Khaled"),
    ("Salma", "Mansour"),
    ("Karim", "Bouaziz"),
    ("Amira", "Toumi"),
    ("Youssef", "Gharbi"),
    ("Leila", "Jebali"),
    ("Hichem", "Sassi"),
    ("Nadia", "Mejri")
]

# Student first names
STUDENT_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Ali", "Youssef", "Karim", "Mehdi", "Amir", "Rami",
    "Fatma", "Salma", "Amira", "Leila", "Nour", "Hiba", "Mariem", "Ines",
    "Safa", "Wafa", "Nesrine", "Rahma"
]

# Student last names  
STUDENT_LAST_NAMES = [
    "Ben Ali", "Trabelsi", "Khaled", "Mansour", "Bouaziz", "Toumi", "Gharbi",
    "Jebali", "Sassi", "Mejri", "Hamdi", "Chaouch", "Dridi", "Fourati",
    "Yahyaoui", "Ktari", "Rebai", "Zouari", "Bahri", "Nasr"
]

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def populate_database():
    """Main function to populate the database"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=" * 80)
        print("STARTING DATABASE POPULATION")
        print("=" * 80)
        
        # Store created data for later use
        created_data = {
            "departments": {},
            "specialties": {},
            "levels": {},
            "groups": {},
            "subjects": {},
            "teachers": [],
            "students": [],
            "rooms": []
        }
        
        # 1. Create Rooms (Salles)
        print("\n📦 CREATING ROOMS...")
        for room_data in ROOMS_CONFIG:
            # Check if room already exists
            existing_room = await prisma.salle.find_unique(where={"code": room_data["code"]})
            if existing_room:
                created_data["rooms"].append(existing_room)
                print(f"  ✓ Room exists: {existing_room.code} ({existing_room.type})")
            else:
                room = await prisma.salle.create(data=room_data)
                created_data["rooms"].append(room)
                print(f"  ✅ Created room: {room.code} ({room.type})")
        
        # 2. Create Departments, Specialties, Levels, Groups, and Subjects
        print("\n🏛️  CREATING ACADEMIC STRUCTURE...")
        for dept_name, dept_config in DEPARTMENTS_CONFIG.items():
            # Create Department
            existing_dept = await prisma.departement.find_first(where={"nom": dept_name})
            if existing_dept:
                department = existing_dept
                print(f"\n  ✓ Department exists: {dept_name}")
            else:
                department = await prisma.departement.create(
                    data={
                        "nom": dept_name
                    }
                )
                print(f"\n  ✅ Created department: {dept_name}")
            created_data["departments"][dept_name] = department
            
            # Create Specialties and their Levels
            for specialty_config in dept_config["specialties"]:
                specialty = await prisma.specialite.create(
                    data={
                        "nom": specialty_config["name"],
                        "id_departement": department.id
                    }
                )
                created_data["specialties"][specialty_config["code"]] = specialty
                print(f"    ➡️  Specialty: {specialty_config['name']}")
                
                # Create Levels (Niveaux) for this specialty
                for level_config in specialty_config["levels"]:
                    level = await prisma.niveau.create(
                        data={
                            "nom": level_config["name"],
                            "id_specialite": specialty.id
                        }
                    )
                    created_data["levels"][level_config["code"]] = level
                    print(f"      ➡️  Level: {level_config['name']}")
                    
                    # Create 2 groups per level (Groupe 1 and Groupe 2)
                    for group_num in [1, 2]:
                        group = await prisma.groupe.create(
                            data={
                                "nom": f"{level_config['code']}-G{group_num}",
                                "id_niveau": level.id
                            }
                        )
                        created_data["groups"][f"{level_config['code']}-G{group_num}"] = group
                        print(f"        ➡️  Group: {group.nom}")
            
            # Create Subjects for this department
            print(f"\n  📚 Creating subjects for {dept_name}...")
            for subject_config in dept_config["subjects"]:
                subject = await prisma.matiere.create(
                    data={
                        "nom": subject_config["name"],
                        "coefficient": subject_config["coefficient"],
                        "id_specialite": created_data["specialties"][dept_config["specialties"][0]["code"]].id
                    }
                )
                created_data["subjects"][subject_config["code"]] = subject
                print(f"    ✅ Subject: {subject_config['name']} (coef: {subject_config['coefficient']})")
        
        # 3. Create Department Heads
        print("\n👔 CREATING DEPARTMENT HEADS...")
        dept_counter = 1
        for dept_name, department in created_data["departments"].items():
            # Check if department head already exists
            existing_head = await prisma.chefdepartement.find_first(where={"id_departement": department.id})
            if existing_head:
                print(f"  ✓ Department head exists for {dept_name}")
                dept_counter += 1
                continue
            
            # Create user account
            user = await prisma.utilisateur.create(
                data={
                    "prenom": f"Chef",
                    "nom": f"Departement{dept_counter}",
                    "email": f"chef.dept{dept_counter}@university.tn",
                    "role": "DEPARTMENT_HEAD",
                    "mdp_hash": hash_password(TEST_PASSWORD)
                }
            )
            
            # Create department head profile
            dept_head = await prisma.chefdepartement.create(
                data={
                    "id_utilisateur": user.id,
                    "id_departement": department.id
                }
            )
            print(f"  ✅ Created: {user.email} for {dept_name}")
            dept_counter += 1
        
        # 4. Create Teachers
        print("\n👨‍🏫 CREATING TEACHERS...")
        teacher_counter = 1
        all_specialties = list(created_data["specialties"].values())
        
        for idx, (prenom, nom) in enumerate(TEACHER_NAMES):
            email = f"teacher{teacher_counter}@university.tn"
            
            # Check if teacher already exists
            existing_teacher = await prisma.enseignant.find_unique(where={"email": email})
            if existing_teacher:
                created_data["teachers"].append(existing_teacher)
                teacher_counter += 1
                continue
            
            # Assign teacher to a specialty (distribute evenly)
            specialty = all_specialties[idx % len(all_specialties)]
            
            # Get the department for this specialty
            specialty_with_dept = await prisma.specialite.find_unique(
                where={"id": specialty.id},
                include={"departement": True}
            )
            
            # Check if user already exists
            existing_user = await prisma.utilisateur.find_unique(where={"email": email})
            if not existing_user:
                # Create user account
                user = await prisma.utilisateur.create(
                    data={
                        "prenom": prenom,
                        "nom": nom,
                        "email": email,
                        "role": "TEACHER",
                        "mdp_hash": hash_password(TEST_PASSWORD)
                    }
                )
            else:
                user = existing_user
            
            # Create teacher profile
            teacher = await prisma.enseignant.create(
                data={
                    "prenom": prenom,
                    "nom": nom,
                    "email": user.email,
                    "id_departement": specialty_with_dept.departement.id
                }
            )
            
            # Link user to teacher profile
            await prisma.utilisateur.update(
                where={"id": user.id},
                data={"enseignant_id": teacher.id}
            )
            
            created_data["teachers"].append(teacher)
            print(f"  ✅ Created: {prenom} {nom} ({user.email}) - {specialty.nom}")
            teacher_counter += 1
        
        # 5. Create Students
        print("\n👨‍🎓 CREATING STUDENTS...")
        student_counter = 1
        all_groups = list(created_data["groups"].values())
        
        # Create 10 students per group
        for group in all_groups:
            print(f"\n  Creating students for group: {group.nom}")
            for i in range(10):
                email = f"student{student_counter}@university.tn"
                
                # Check if student already exists
                existing_student = await prisma.etudiant.find_unique(where={"email": email})
                if existing_student:
                    created_data["students"].append(existing_student)
                    student_counter += 1
                    continue
                
                prenom = random.choice(STUDENT_FIRST_NAMES)
                nom = random.choice(STUDENT_LAST_NAMES)
                
                # Get the level and specialty for this group
                level = await prisma.niveau.find_unique(
                    where={"id": group.id_niveau},
                    include={"specialite": True}
                )
                
                # Check if user already exists
                existing_user = await prisma.utilisateur.find_unique(where={"email": email})
                if not existing_user:
                    # Create user account
                    user = await prisma.utilisateur.create(
                        data={
                            "prenom": prenom,
                            "nom": nom,
                            "email": email,
                            "role": "STUDENT",
                            "mdp_hash": hash_password(TEST_PASSWORD)
                        }
                    )
                else:
                    user = existing_user
                
                # Create student profile
                student = await prisma.etudiant.create(
                    data={
                        "prenom": prenom,
                        "nom": nom,
                        "email": user.email,
                        "id_specialite": level.specialite.id,
                        "id_groupe": group.id
                    }
                )
                
                # Link user to student profile
                await prisma.utilisateur.update(
                    where={"id": user.id},
                    data={"etudiant_id": student.id}
                )
                
                created_data["students"].append(student)
                print(f"    ✅ ST{student_counter:04d}: {prenom} {nom} ({user.email})")
                student_counter += 1
        
        # 6. Create Schedule Entries (Emploi du Temps)
        print("\n📅 CREATING SCHEDULE ENTRIES...")
        
        # Create schedules for next week (Monday to Friday)
        today = datetime.now().date()
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        # Schedule template: (day_offset, start_hour, end_hour)
        schedule_times = [
            (0, 8, 10),   # Monday 8-10
            (0, 10, 12),  # Monday 10-12
            (0, 14, 16),  # Monday 14-16
            (1, 8, 10),   # Tuesday 8-10
            (1, 10, 12),  # Tuesday 10-12
            (2, 8, 10),   # Wednesday 8-10
            (2, 14, 16),  # Wednesday 14-16
            (3, 8, 10),   # Thursday 8-10
            (3, 10, 12),  # Thursday 10-12
            (4, 8, 10),   # Friday 8-10
        ]
        
        schedule_count = 0
        for group in all_groups[:3]:  # Create schedules for first 3 groups
            # Get level and specialty
            level = await prisma.niveau.find_unique(
                where={"id": group.id_niveau},
                include={"specialite": {"include": {"departement": True}}}
            )
            
            # Get subjects for this specialty's department
            dept_subjects = [s for s in created_data["subjects"].values() 
                           if s.id_specialite == level.specialite.id]
            
            if not dept_subjects:
                continue
            
            print(f"\n  Creating schedule for group: {group.nom}")
            
            for day_offset, start_hour, end_hour in schedule_times:
                schedule_date = next_monday + timedelta(days=day_offset)
                start_datetime = datetime.combine(schedule_date, time(start_hour, 0))
                end_datetime = datetime.combine(schedule_date, time(end_hour, 0))
                
                # Randomly select teacher, subject, and room
                teacher = random.choice(created_data["teachers"])
                subject = random.choice(dept_subjects)
                room = random.choice(created_data["rooms"])
                
                # Create schedule entry
                schedule = await prisma.emploitemps.create(
                    data={
                        "date": start_datetime,
                        "heure_debut": start_datetime,
                        "heure_fin": end_datetime,
                        "id_salle": room.id,
                        "id_matiere": subject.id,
                        "id_groupe": group.id,
                        "id_enseignant": teacher.id,
                        "status": "PLANNED"
                    }
                )
                schedule_count += 1
                print(f"    ✅ {schedule_date.strftime('%A %Y-%m-%d')} {start_hour}:00-{end_hour}:00 "
                      f"- {subject.nom} - {teacher.prenom} {teacher.nom} - {room.code}")
        
        # Summary
        print("\n" + "=" * 80)
        print("DATABASE POPULATION COMPLETE!")
        print("=" * 80)
        print(f"\n📊 SUMMARY:")
        print(f"  🏛️  Departments: {len(created_data['departments'])}")
        print(f"  📚 Specialties: {len(created_data['specialties'])}")
        print(f"  📊 Levels (Niveaux): {len(created_data['levels'])}")
        print(f"  👥 Groups: {len(created_data['groups'])}")
        print(f"  📖 Subjects (Matières): {len(created_data['subjects'])}")
        print(f"  👨‍🏫 Teachers: {len(created_data['teachers'])}")
        print(f"  👨‍🎓 Students: {len(created_data['students'])}")
        print(f"  🏢 Rooms (Salles): {len(created_data['rooms'])}")
        print(f"  📅 Schedule Entries: {schedule_count}")
        
        print(f"\n🔑 TEST CREDENTIALS:")
        print(f"  Password for all users: {TEST_PASSWORD}")
        print(f"\n  Department Heads:")
        for i in range(1, len(created_data['departments']) + 1):
            print(f"    chef.dept{i}@university.tn")
        print(f"\n  Teachers: teacher1@university.tn to teacher{len(TEACHER_NAMES)}@university.tn")
        print(f"  Students: student1@university.tn to student{len(created_data['students'])}@university.tn")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(populate_database())
