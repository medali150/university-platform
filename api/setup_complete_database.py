"""
Complete Database Setup Script for University Platform
Creates a fresh database with all necessary data including:
- 4 Departments (Génie Mécanique, Génie Électrique, Génie Civil, Technologie d'Informatique)
- Department heads for each department
- Specialties, subjects with coefficients, levels, teachers, students, and rooms
"""
import asyncio
import bcrypt
from prisma import Prisma
from datetime import datetime, timedelta
import random

# Department and specialty data
DEPARTMENTS_DATA = {
    "Génie Mécanique": {
        "specialties": ["Génie Mécanique - Production", "Génie Mécanique - Maintenance"],
        "levels": ["GM1", "GM2", "GM3"],
        "subjects": [
            {"name": "Mécanique des Fluides", "coefficient": 3.0},
            {"name": "Thermodynamique", "coefficient": 2.5},
            {"name": "Résistance des Matériaux", "coefficient": 3.0},
            {"name": "Fabrication Mécanique", "coefficient": 2.0},
            {"name": "Conception Assistée par Ordinateur", "coefficient": 2.5},
            {"name": "Maintenance Industrielle", "coefficient": 2.0}
        ]
    },
    "Génie Électrique": {
        "specialties": ["Génie Électrique - Automatique", "Génie Électrique - Électronique"],
        "levels": ["GE1", "GE2", "GE3"],
        "subjects": [
            {"name": "Électronique de Puissance", "coefficient": 3.0},
            {"name": "Automatique", "coefficient": 2.5},
            {"name": "Circuits Électriques", "coefficient": 2.5},
            {"name": "Microprocesseurs", "coefficient": 2.0},
            {"name": "Systèmes Embarqués", "coefficient": 2.5},
            {"name": "Énergies Renouvelables", "coefficient": 2.0}
        ]
    },
    "Génie Civil": {
        "specialties": ["Génie Civil - Bâtiment", "Génie Civil - Travaux Publics"],
        "levels": ["GC1", "GC2", "GC3"],
        "subjects": [
            {"name": "Béton Armé", "coefficient": 3.5},
            {"name": "Mécanique des Sols", "coefficient": 3.0},
            {"name": "Topographie", "coefficient": 2.0},
            {"name": "Hydraulique", "coefficient": 2.5},
            {"name": "Métré et Devis", "coefficient": 2.0},
            {"name": "Pathologie du Bâtiment", "coefficient": 2.0}
        ]
    },
    "Technologie d'Informatique": {
        "specialties": ["Développement Logiciel", "Réseaux et Systèmes", "Systèmes d'Information"],
        "levels": ["TI1", "TI2", "TI3"],
        "subjects": [
            {"name": "Programmation Orientée Objet", "coefficient": 3.0},
            {"name": "Base de Données", "coefficient": 2.5},
            {"name": "Réseaux Informatiques", "coefficient": 2.5},
            {"name": "Développement Web", "coefficient": 2.0},
            {"name": "Systèmes d'Exploitation", "coefficient": 2.5},
            {"name": "Intelligence Artificielle", "coefficient": 3.0},
            {"name": "Cybersécurité", "coefficient": 2.5},
            {"name": "Gestion de Projets IT", "coefficient": 2.0}
        ]
    }
}

# Room data
ROOMS_DATA = [
    # Amphithéâtres
    {"nom": "AMPHI A", "code": "AMPHA", "type": "LECTURE", "capacite": 200},
    {"nom": "AMPHI B", "code": "AMPHB", "type": "LECTURE", "capacite": 150},
    {"nom": "AMPHI C", "code": "AMPHC", "type": "LECTURE", "capacite": 180},
    
    # Salles de cours classiques
    {"nom": "Salle A101", "code": "A101", "type": "LECTURE", "capacite": 40},
    {"nom": "Salle A102", "code": "A102", "type": "LECTURE", "capacite": 35},
    {"nom": "Salle A103", "code": "A103", "type": "LECTURE", "capacite": 40},
    {"nom": "Salle A201", "code": "A201", "type": "LECTURE", "capacite": 45},
    {"nom": "Salle A202", "code": "A202", "type": "LECTURE", "capacite": 40},
    {"nom": "Salle A203", "code": "A203", "type": "LECTURE", "capacite": 35},
    
    # Laboratoires informatique
    {"nom": "Lab Info 1", "code": "LI1", "type": "LAB", "capacite": 30},
    {"nom": "Lab Info 2", "code": "LI2", "type": "LAB", "capacite": 25},
    {"nom": "Lab Info 3", "code": "LI3", "type": "LAB", "capacite": 30},
    {"nom": "Lab Info 4", "code": "LI4", "type": "LAB", "capacite": 28},
    
    # Laboratoires spécialisés
    {"nom": "Lab Mécanique", "code": "LM1", "type": "LAB", "capacite": 20},
    {"nom": "Lab Électronique", "code": "LE1", "type": "LAB", "capacite": 25},
    {"nom": "Lab Matériaux", "code": "LMAT", "type": "LAB", "capacite": 15},
    {"nom": "Lab Hydraulique", "code": "LH1", "type": "LAB", "capacite": 20},
    
    # Ateliers
    {"nom": "Atelier Mécanique", "code": "AM1", "type": "OTHER", "capacite": 25},
    {"nom": "Atelier Soudure", "code": "AS1", "type": "OTHER", "capacite": 15},
    {"nom": "Atelier Électrique", "code": "AE1", "type": "OTHER", "capacite": 20},
    
    # Salles d'examens
    {"nom": "Salle Examen 1", "code": "EX1", "type": "EXAM", "capacite": 60},
    {"nom": "Salle Examen 2", "code": "EX2", "type": "EXAM", "capacite": 80},
    {"nom": "Salle Examen 3", "code": "EX3", "type": "EXAM", "capacite": 100}
]

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def create_complete_database():
    """Create complete database setup"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🗑️  Cleaning existing data...")
        
        # Delete all data in correct order (respecting foreign key constraints)
        await prisma.absence.delete_many()
        await prisma.emploitemps.delete_many()
        await prisma.matiere.delete_many()
        await prisma.etudiant.delete_many()
        await prisma.enseignant.delete_many()
        await prisma.groupe.delete_many()
        await prisma.niveau.delete_many()
        await prisma.specialite.delete_many()
        await prisma.chefdepartement.delete_many()
        await prisma.administrateur.delete_many()
        await prisma.salle.delete_many()
        await prisma.departement.delete_many()
        await prisma.utilisateur.delete_many()
        
        print("✅ Database cleaned successfully")
        
        # Create departments and collect IDs
        departments = {}
        print("\n📚 Creating departments...")
        
        for dept_name in DEPARTMENTS_DATA.keys():
            dept = await prisma.departement.create({
                "nom": dept_name
            })
            departments[dept_name] = dept.id
            print(f"   ✅ Created department: {dept_name}")
        
        # Create department heads
        department_heads = {}
        print("\n👥 Creating department heads...")
        
        dept_head_data = [
            {"nom": "MAATALLAH", "prenom": "Mohamed", "email": "mohamed.maatallah@university.tn", "dept": "Technologie d'Informatique"},
            {"nom": "NEFZAOUI", "prenom": "Fatma", "email": "fatma.nefzaoui@university.tn", "dept": "Génie Mécanique"},
            {"nom": "HAMDI", "prenom": "Ahmed", "email": "ahmed.hamdi@university.tn", "dept": "Génie Électrique"},
            {"nom": "ARFAOUI", "prenom": "Sarra", "email": "sarra.arfaoui@university.tn", "dept": "Génie Civil"}
        ]
        
        for head_data in dept_head_data:
            # Create user
            user = await prisma.utilisateur.create({
                "nom": head_data["nom"],
                "prenom": head_data["prenom"],
                "email": head_data["email"],
                "role": "DEPARTMENT_HEAD",
                "mdp_hash": hash_password("password123")
            })
            
            # Create department head
            dept_head = await prisma.chefdepartement.create({
                "id_utilisateur": user.id,
                "id_departement": departments[head_data["dept"]]
            })
            
            department_heads[head_data["dept"]] = dept_head.id
            print(f"   ✅ Created department head: {head_data['prenom']} {head_data['nom']} for {head_data['dept']}")
        
        # Create admin user
        print("\n🔐 Creating admin user...")
        admin_user = await prisma.utilisateur.create({
            "nom": "ADMIN",
            "prenom": "System",
            "email": "admin@university.tn",
            "role": "ADMIN",
            "mdp_hash": hash_password("admin123")
        })
        
        await prisma.administrateur.create({
            "id_utilisateur": admin_user.id,
            "niveau": "SUPER_ADMIN"
        })
        print("   ✅ Created admin user: admin@university.tn")
        
        # Create rooms
        print("\n🏢 Creating rooms...")
        rooms = []
        for room_data in ROOMS_DATA:
            room = await prisma.salle.create(room_data)
            rooms.append(room)
            print(f"   ✅ Created room: {room_data['nom']} ({room_data['capacite']} places)")
        
        # Create specialties, levels, teachers, students, and subjects for each department
        all_teachers = []
        all_students = []
        
        for dept_name, dept_data in DEPARTMENTS_DATA.items():
            print(f"\n🎓 Setting up {dept_name} department...")
            dept_id = departments[dept_name]
            
            # Create specialties
            specialties = {}
            for specialty_name in dept_data["specialties"]:
                specialty = await prisma.specialite.create({
                    "nom": specialty_name,
                    "id_departement": dept_id
                })
                specialties[specialty_name] = specialty.id
                print(f"   📋 Created specialty: {specialty_name}")
            
            # Create levels for each specialty
            levels = {}
            for specialty_name, specialty_id in specialties.items():
                for level_name in dept_data["levels"]:
                    full_level_name = f"{level_name} - {specialty_name.split(' - ')[-1] if ' - ' in specialty_name else specialty_name}"
                    level = await prisma.niveau.create({
                        "nom": full_level_name,
                        "id_specialite": specialty_id
                    })
                    levels[full_level_name] = level.id
                    print(f"     📚 Created level: {full_level_name}")
            
            # Create teachers for this department
            teacher_names = [
                {"nom": "BOUALI", "prenom": "Karim"},
                {"nom": "MEZGHANI", "prenom": "Leila"},
                {"nom": "TRABELSI", "prenom": "Youssef"},
                {"nom": "KARRAY", "prenom": "Amina"},
                {"nom": "MAHJOUB", "prenom": "Riadh"},
                {"nom": "SALEM", "prenom": "Nadia"}
            ]
            
            dept_teachers = []
            for i, teacher_data in enumerate(teacher_names):
                # Create user for teacher
                email = f"{teacher_data['prenom'].lower()}.{teacher_data['nom'].lower()}@{dept_name.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')}.tn"
                user = await prisma.utilisateur.create({
                    "nom": teacher_data["nom"],
                    "prenom": teacher_data["prenom"],
                    "email": email,
                    "role": "TEACHER",
                    "mdp_hash": hash_password("teacher123")
                })
                
                # Create teacher
                teacher = await prisma.enseignant.create({
                    "nom": teacher_data["nom"],
                    "prenom": teacher_data["prenom"],
                    "email": email,
                    "id_departement": dept_id
                })
                
                # Update user with teacher relation
                await prisma.utilisateur.update({
                    "where": {"id": user.id},
                    "data": {"enseignant_id": teacher.id}
                })
                
                dept_teachers.append(teacher)
                all_teachers.append(teacher)
                print(f"     👨‍🏫 Created teacher: {teacher_data['prenom']} {teacher_data['nom']}")
            
            # Create subjects for this department
            for specialty_name, specialty_id in specialties.items():
                for subject_data in dept_data["subjects"]:
                    # Assign random teacher
                    assigned_teacher = random.choice(dept_teachers)
                    
                    subject = await prisma.matiere.create({
                        "nom": subject_data["name"],
                        "coefficient": subject_data["coefficient"],
                        "id_specialite": specialty_id,
                        "id_enseignant": assigned_teacher.id
                    })
                    print(f"     📖 Created subject: {subject_data['name']} (coeff: {subject_data['coefficient']}) - {assigned_teacher.prenom} {assigned_teacher.nom}")
            
            # Create groups and students for each level
            for level_name, level_id in levels.items():
                # Create 2-3 groups per level
                groups_per_level = random.randint(2, 3)
                
                for group_num in range(1, groups_per_level + 1):
                    group_name = f"{level_name.split(' - ')[0]} G{group_num}"
                    group = await prisma.groupe.create({
                        "nom": group_name,
                        "id_niveau": level_id
                    })
                    
                    print(f"     👥 Created group: {group_name}")
                    
                    # Create students for this group (15-25 students per group)
                    students_per_group = random.randint(15, 25)
                    
                    first_names = ["Ahmed", "Fatma", "Mohamed", "Sarra", "Youssef", "Leila", "Karim", "Amina", 
                                 "Riadh", "Nadia", "Hamdi", "Mariam", "Slim", "Amel", "Tarek", "Hiba",
                                 "Farouk", "Salma", "Nizar", "Rim", "Mehdi", "Dorra", "Wassim", "Ines"]
                    
                    last_names = ["BEN ALI", "TRABELSI", "MEZGHANI", "KARRAY", "BOUALI", "MAHJOUB",
                                "SALEM", "NEFZAOUI", "HAMDI", "ARFAOUI", "MAATALLAH", "CHAOUACHI",
                                "DRISSI", "HAKIM", "BELHAJ", "GHARBI", "MZALI", "REKIK"]
                    
                    for student_num in range(1, students_per_group + 1):
                        first_name = random.choice(first_names)
                        last_name = random.choice(last_names)
                        
                        # Create user for student
                        email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@student.university.tn"
                        user = await prisma.utilisateur.create({
                            "nom": last_name,
                            "prenom": first_name,
                            "email": email,
                            "role": "STUDENT",
                            "mdp_hash": hash_password("student123")
                        })
                        
                        # Create student
                        student = await prisma.etudiant.create({
                            "nom": last_name,
                            "prenom": first_name,
                            "email": email,
                            "id_groupe": group.id,
                            "id_specialite": specialty_id
                        })
                        
                        # Update user with student relation
                        await prisma.utilisateur.update({
                            "where": {"id": user.id},
                            "data": {"etudiant_id": student.id}
                        })
                        
                        all_students.append(student)
                    
                    print(f"       👨‍🎓 Created {students_per_group} students for {group_name}")
        
        # Create some sample schedules
        print("\n📅 Creating sample schedules...")
        
        # Get some subjects, groups, rooms, and teachers
        subjects = await prisma.matiere.find_many(take=20)
        groups = await prisma.groupe.find_many(take=10)
        teachers = await prisma.enseignant.find_many(take=15)
        
        # Create schedules for the current week
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        time_slots = [
            {"start": "08:30", "end": "10:00"},
            {"start": "10:10", "end": "11:40"},
            {"start": "11:50", "end": "13:20"},
            {"start": "14:30", "end": "16:00"},
            {"start": "16:10", "end": "17:40"}
        ]
        
        schedule_count = 0
        for day_offset in range(6):  # Monday to Saturday
            schedule_date = start_of_week + timedelta(days=day_offset)
            
            for time_slot in time_slots:
                # Create 3-5 schedules per time slot
                schedules_per_slot = random.randint(3, 5)
                
                for _ in range(schedules_per_slot):
                    if schedule_count >= len(subjects) or schedule_count >= len(groups):
                        break
                    
                    subject = subjects[schedule_count % len(subjects)]
                    group = groups[schedule_count % len(groups)]
                    room = random.choice(rooms)
                    teacher = random.choice(teachers)
                    
                    # Create datetime objects
                    start_datetime = datetime.combine(schedule_date, datetime.strptime(time_slot["start"], "%H:%M").time())
                    end_datetime = datetime.combine(schedule_date, datetime.strptime(time_slot["end"], "%H:%M").time())
                    
                    try:
                        await prisma.emploitemps.create({
                            "date": schedule_date,
                            "heure_debut": start_datetime,
                            "heure_fin": end_datetime,
                            "id_salle": room.id,
                            "id_matiere": subject.id,
                            "id_groupe": group.id,
                            "id_enseignant": teacher.id,
                            "status": "PLANNED"
                        })
                        schedule_count += 1
                    except Exception as e:
                        print(f"       ⚠️ Failed to create schedule: {str(e)}")
                        continue
        
        print(f"   ✅ Created {schedule_count} sample schedules")
        
        # Create some sample absences
        print("\n🚫 Creating sample absences...")
        
        recent_schedules = await prisma.emploitemps.find_many(
            where={"date": {"gte": start_of_week}},
            take=20
        )
        
        absence_count = 0
        for schedule in recent_schedules[:10]:  # Create absences for first 10 schedules
            # Get students from the group
            schedule_students = await prisma.etudiant.find_many(
                where={"id_groupe": schedule.id_groupe},
                take=5
            )
            
            # Create absences for 1-3 random students
            absent_students = random.sample(schedule_students, min(random.randint(1, 3), len(schedule_students)))
            
            for student in absent_students:
                try:
                    await prisma.absence.create({
                        "id_etudiant": student.id,
                        "id_emploitemps": schedule.id,
                        "motif": random.choice([
                            "Maladie",
                            "Retard transport",
                            "Absence non justifiée",
                            "Rendez-vous médical"
                        ]),
                        "statut": random.choice(["unjustified", "pending_review", "justified"])
                    })
                    absence_count += 1
                except Exception as e:
                    print(f"       ⚠️ Failed to create absence: {str(e)}")
                    continue
        
        print(f"   ✅ Created {absence_count} sample absences")
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 DATABASE SETUP COMPLETE!")
        print("="*60)
        
        # Count and display statistics
        dept_count = await prisma.departement.count()
        specialty_count = await prisma.specialite.count()
        level_count = await prisma.niveau.count()
        subject_count = await prisma.matiere.count()
        teacher_count = await prisma.enseignant.count()
        student_count = await prisma.etudiant.count()
        group_count = await prisma.groupe.count()
        room_count = await prisma.salle.count()
        schedule_count_final = await prisma.emploitemps.count()
        absence_count_final = await prisma.absence.count()
        
        print(f"📊 STATISTICS:")
        print(f"   🏛️  Departments: {dept_count}")
        print(f"   📋 Specialties: {specialty_count}")
        print(f"   📚 Levels: {level_count}")
        print(f"   📖 Subjects: {subject_count}")
        print(f"   👨‍🏫 Teachers: {teacher_count}")
        print(f"   👨‍🎓 Students: {student_count}")
        print(f"   👥 Groups: {group_count}")
        print(f"   🏢 Rooms: {room_count}")
        print(f"   📅 Schedules: {schedule_count_final}")
        print(f"   🚫 Absences: {absence_count_final}")
        
        print(f"\n🔐 LOGIN CREDENTIALS:")
        print(f"   🔑 Admin: admin@university.tn / admin123")
        print(f"   👥 Department Heads:")
        for head_data in dept_head_data:
            print(f"      - {head_data['email']} / password123 ({head_data['dept']})")
        print(f"   👨‍🏫 Teachers: [name]@[department].tn / teacher123")
        print(f"   👨‍🎓 Students: [name]@student.university.tn / student123")
        
        print("\n✅ Database is ready for use!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    print("🚀 Starting Complete Database Setup...")
    print("This will create a fresh database with sample data")
    print("⚠️  WARNING: This will delete all existing data!")
    
    confirm = input("\nDo you want to continue? (yes/no): ").lower()
    if confirm in ['yes', 'y', 'oui']:
        asyncio.run(create_complete_database())
    else:
        print("❌ Setup cancelled by user")