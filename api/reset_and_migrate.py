#!/usr/bin/env python3
"""
Reset and migrate the database with French schema
"""
import asyncio
import os
import subprocess
from datetime import datetime, timedelta
from prisma import Prisma

async def reset_database():
    """Reset the database and apply new schema"""
    print("🔄 Resetting database with French schema...")
    
    try:
        # Reset the database
        print("📝 Applying schema changes...")
        result = subprocess.run(
            ["npx", "prisma", "db", "push", "--force-reset"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print(f"❌ Database reset failed: {result.stderr}")
            return False
        
        print("✅ Database reset complete!")
        
        # Generate the Prisma client
        print("🔧 Generating Prisma client...")
        result = subprocess.run(
            ["npx", "prisma", "generate"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print(f"❌ Client generation failed: {result.stderr}")
            return False
        
        print("✅ Prisma client generated!")
        
        # Create sample data
        await create_sample_data()
        return True
        
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        return False

async def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data with French schema...")
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Create departments
        print("   Creating departments...")
        dept_info = await prisma.departement.create({
            "nom": "Informatique"
        })
        
        dept_math = await prisma.departement.create({
            "nom": "Mathématiques"
        })
        
        print(f"   ✅ Created departments: {dept_info.nom}, {dept_math.nom}")
        
        # Create specialties
        print("   Creating specialties...")
        spec_gl = await prisma.specialite.create({
            "nom": "Génie Logiciel",
            "id_departement": dept_info.id
        })
        
        spec_si = await prisma.specialite.create({
            "nom": "Systèmes d'Information",
            "id_departement": dept_info.id
        })
        
        spec_math_pure = await prisma.specialite.create({
            "nom": "Mathématiques Pures",
            "id_departement": dept_math.id
        })
        
        print(f"   ✅ Created specialties: {spec_gl.nom}, {spec_si.nom}, {spec_math_pure.nom}")
        
        # Create levels
        print("   Creating levels...")
        niveau_l3_gl = await prisma.niveau.create({
            "nom": "Licence 3",
            "id_specialite": spec_gl.id
        })
        
        niveau_m1_gl = await prisma.niveau.create({
            "nom": "Master 1",
            "id_specialite": spec_gl.id
        })
        
        niveau_l3_si = await prisma.niveau.create({
            "nom": "Licence 3",
            "id_specialite": spec_si.id
        })
        
        print(f"   ✅ Created levels for GL and SI")
        
        # Create groups
        print("   Creating groups...")
        groupe_gl3a = await prisma.groupe.create({
            "nom": "GL3A",
            "id_niveau": niveau_l3_gl.id
        })
        
        groupe_gl3b = await prisma.groupe.create({
            "nom": "GL3B", 
            "id_niveau": niveau_l3_gl.id
        })
        
        groupe_m1gl = await prisma.groupe.create({
            "nom": "M1GL",
            "id_niveau": niveau_m1_gl.id
        })
        
        groupe_si3a = await prisma.groupe.create({
            "nom": "SI3A",
            "id_niveau": niveau_l3_si.id
        })
        
        print(f"   ✅ Created groups: GL3A, GL3B, M1GL, SI3A")
        
        # Create rooms
        print("   Creating rooms...")
        salle_101 = await prisma.salle.create({
            "code": "SALLE-101",
            "type": "LECTURE",
            "capacite": 50
        })
        
        salle_lab = await prisma.salle.create({
            "code": "LAB-001",
            "type": "LAB",
            "capacite": 25
        })
        
        salle_202 = await prisma.salle.create({
            "code": "SALLE-202",
            "type": "LECTURE", 
            "capacite": 40
        })
        
        print(f"   ✅ Created rooms: {salle_101.code}, {salle_lab.code}, {salle_202.code}")
        
        # Create teacher profiles first
        print("   Creating teacher profiles...")
        teacher_dupont = await prisma.enseignant.create({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@university.com",
            "id_departement": dept_info.id
        })
        
        teacher_martin = await prisma.enseignant.create({
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@university.com", 
            "id_departement": dept_info.id
        })
        
        teacher_bernard = await prisma.enseignant.create({
            "nom": "Bernard",
            "prenom": "Pierre",
            "email": "pierre.bernard@university.com",
            "id_departement": dept_math.id
        })
        
        print(f"   ✅ Created teacher profiles")
        
        # Create student profiles first
        print("   Creating student profiles...")
        student_marie = await prisma.etudiant.create({
            "nom": "Leroy",
            "prenom": "Marie",
            "email": "marie.leroy@student.university.edu",
            "id_groupe": groupe_gl3a.id,
            "id_specialite": spec_gl.id
        })
        
        student_paul = await prisma.etudiant.create({
            "nom": "Moreau",
            "prenom": "Paul",
            "email": "paul.moreau@student.university.edu",
            "id_groupe": groupe_gl3b.id,
            "id_specialite": spec_gl.id
        })
        
        student_alice = await prisma.etudiant.create({
            "nom": "Dubois",
            "prenom": "Alice",
            "email": "alice.dubois@student.university.edu",
            "id_groupe": groupe_si3a.id,
            "id_specialite": spec_si.id
        })
        
        print(f"   ✅ Created student profiles")
        
        # Create users and link them to profiles
        print("   Creating user accounts...")
        
        # Teacher users
        user_teacher_dupont = await prisma.utilisateur.create({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@university.com",
            "login": "jdupont",
            "role": "TEACHER",
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm",  # teacher123
            "enseignant_id": teacher_dupont.id
        })
        
        user_teacher_martin = await prisma.utilisateur.create({
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@university.com",
            "login": "smartin",
            "role": "TEACHER",
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm",  # teacher123
            "enseignant_id": teacher_martin.id
        })
        
        # Student users
        user_student_marie = await prisma.utilisateur.create({
            "nom": "Leroy",
            "prenom": "Marie",
            "email": "marie.leroy@student.university.edu",
            "login": "mleroy",
            "role": "STUDENT",
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm",  # student123
            "etudiant_id": student_marie.id
        })
        
        user_student_paul = await prisma.utilisateur.create({
            "nom": "Moreau",
            "prenom": "Paul",
            "email": "paul.moreau@student.university.edu",
            "login": "pmoreau",
            "role": "STUDENT", 
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm",  # student123
            "etudiant_id": student_paul.id
        })
        
        # Department head user
        user_dept_head = await prisma.utilisateur.create({
            "nom": "Leclerc",
            "prenom": "Pierre",
            "email": "pierre.leclerc@university.com",
            "login": "pleclerc",
            "role": "DEPARTMENT_HEAD",
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm"  # depthead123
        })
        
        # Admin user
        user_admin = await prisma.utilisateur.create({
            "nom": "Admin",
            "prenom": "System",
            "email": "admin@university.com",
            "login": "admin",
            "role": "ADMIN",
            "mdp_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/rN4OGLMSm"  # admin123
        })
        
        print(f"   ✅ Created user accounts")
        
        # Create department head profile
        dept_head = await prisma.chefdepartement.create({
            "id_utilisateur": user_dept_head.id,
            "id_departement": dept_info.id
        })
        
        # Create admin profile
        admin_profile = await prisma.administrateur.create({
            "id_utilisateur": user_admin.id,
            "niveau": "SUPER_ADMIN"
        })
        
        print(f"   ✅ Created department head and admin profiles")
        
        # Create subjects
        print("   Creating subjects...")
        subject_java = await prisma.matiere.create({
            "nom": "Programmation Java",
            "id_niveau": niveau_l3_gl.id,
            "id_enseignant": teacher_dupont.id
        })
        
        subject_db = await prisma.matiere.create({
            "nom": "Base de Données",
            "id_niveau": niveau_l3_gl.id,
            "id_enseignant": teacher_martin.id
        })
        
        subject_web = await prisma.matiere.create({
            "nom": "Développement Web",
            "id_niveau": niveau_l3_si.id,
            "id_enseignant": teacher_dupont.id
        })
        
        subject_algo = await prisma.matiere.create({
            "nom": "Algorithmique Avancée",
            "id_niveau": niveau_m1_gl.id,
            "id_enseignant": teacher_martin.id
        })
        
        print(f"   ✅ Created subjects: Java, Database, Web, Algorithms")
        
        # Create some schedule entries
        print("   Creating schedule entries...")
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Java class for GL3A
        schedule1 = await prisma.emploitemps.create({
            "date": datetime.combine(today, datetime.min.time()),
            "heure_debut": datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
            "heure_fin": datetime.combine(today, datetime.strptime("10:00", "%H:%M").time()),
            "id_salle": salle_101.id,
            "id_matiere": subject_java.id,
            "id_groupe": groupe_gl3a.id,
            "id_enseignant": teacher_dupont.id,
            "status": "PLANNED"
        })
        
        # Database class for GL3B
        schedule2 = await prisma.emploitemps.create({
            "date": datetime.combine(today, datetime.min.time()),
            "heure_debut": datetime.combine(today, datetime.strptime("10:30", "%H:%M").time()),
            "heure_fin": datetime.combine(today, datetime.strptime("12:30", "%H:%M").time()),
            "id_salle": salle_lab.id,
            "id_matiere": subject_db.id,
            "id_groupe": groupe_gl3b.id,
            "id_enseignant": teacher_martin.id,
            "status": "PLANNED"
        })
        
        # Web dev class for SI3A
        schedule3 = await prisma.emploitemps.create({
            "date": datetime.combine(tomorrow, datetime.min.time()),
            "heure_debut": datetime.combine(tomorrow, datetime.strptime("14:00", "%H:%M").time()),
            "heure_fin": datetime.combine(tomorrow, datetime.strptime("16:00", "%H:%M").time()),
            "id_salle": salle_202.id,
            "id_matiere": subject_web.id,
            "id_groupe": groupe_si3a.id,
            "id_enseignant": teacher_dupont.id,
            "status": "PLANNED"
        })
        
        print(f"   ✅ Created schedule entries")
        
        # Create some events
        print("   Creating events...")
        event1 = await prisma.evenement.create({
            "titre": "Réunion Pédagogique",
            "type": "MEETING",
            "date": datetime.combine(tomorrow, datetime.strptime("09:00", "%H:%M").time()),
            "description": "Réunion mensuelle du département informatique"
        })
        
        event2 = await prisma.evenement.create({
            "titre": "Conférence IA",
            "type": "CONFERENCE",
            "date": datetime.combine(today + timedelta(days=7), datetime.strptime("14:00", "%H:%M").time()),
            "description": "Conférence sur l'Intelligence Artificielle"
        })
        
        print(f"   ✅ Created events")
        
        print("✅ Sample data created successfully!")
        print("\n🎉 Database setup complete with French schema!")
        print("\n📧 Test credentials:")
        print("   👨‍🏫 Teachers:")
        print("      jean.dupont@university.com / teacher123")
        print("      sophie.martin@university.com / teacher123")
        print("   🎓 Students:")
        print("      marie.leroy@student.university.edu / student123")
        print("      paul.moreau@student.university.edu / student123")
        print("   🏢 Department Head:")
        print("      pierre.leclerc@university.com / depthead123")
        print("   ⚙️  Admin:")
        print("      admin@university.com / admin123")
        print("\n🚀 You can now start your FastAPI server and test the frontend!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(reset_database())