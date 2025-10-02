#!/usr/bin/env python3
"""
Script to recreate sample data after removing login field from database
"""

import asyncio
import bcrypt
from prisma import Prisma

async def main():
    """Recreate all sample data with proper relationships"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🚀 Starting sample data recreation...")
        
        # Hash password for all users
        password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 1. Create Departments
        print("📁 Creating departments...")
        
        dept_info = await prisma.departement.create({
            "nom": "Informatique"
        })
        
        dept_math = await prisma.departement.create({
            "nom": "Mathématiques"
        })
        
        print(f"✅ Created departments: {dept_info.nom}, {dept_math.nom}")
        
        # 2. Create Specialties
        print("🎯 Creating specialties...")
        
        spec_info = await prisma.specialite.create({
            "nom": "Génie Logiciel",
            "id_departement": dept_info.id
        })
        
        spec_reseaux = await prisma.specialite.create({
            "nom": "Réseaux et Télécommunications", 
            "id_departement": dept_info.id
        })
        
        print(f"✅ Created specialties: {spec_info.nom}, {spec_reseaux.nom}")
        
        # 3. Create Levels
        print("📊 Creating levels...")
        
        niveau_l1 = await prisma.niveau.create({
            "nom": "Licence 1",
            "id_specialite": spec_info.id
        })
        
        niveau_l2 = await prisma.niveau.create({
            "nom": "Licence 2", 
            "id_specialite": spec_info.id
        })
        
        print(f"✅ Created levels: {niveau_l1.nom}, {niveau_l2.nom}")
        
        # 4. Create Groups
        print("👥 Creating groups...")
        
        groupe_a = await prisma.groupe.create({
            "nom": "Groupe A",
            "id_niveau": niveau_l1.id
        })
        
        groupe_b = await prisma.groupe.create({
            "nom": "Groupe B",
            "id_niveau": niveau_l2.id
        })
        
        print(f"✅ Created groups: {groupe_a.nom}, {groupe_b.nom}")
        
        # 5. Create Users with their role-specific records
        print("👤 Creating users and role-specific records...")
        
        # Admin user
        admin_user = await prisma.utilisateur.create({
            "nom": "Admin",
            "prenom": "Super", 
            "email": "admin@university.com",
            "role": "ADMIN",
            "mdp_hash": password_hash
        })
        
        admin_record = await prisma.administrateur.create({
            "id_utilisateur": admin_user.id,
            "niveau": "SUPER_ADMIN"
        })
        
        print(f"✅ Created admin: {admin_user.email}")
        
        # Department Head user
        dept_head_user = await prisma.utilisateur.create({
            "nom": "Boubaker",
            "prenom": "Chef",
            "email": "boubaker@university.com", 
            "role": "DEPARTMENT_HEAD",
            "mdp_hash": password_hash
        })
        
        dept_head_record = await prisma.chefdepartement.create({
            "id_utilisateur": dept_head_user.id,
            "id_departement": dept_info.id
        })
        
        print(f"✅ Created department head: {dept_head_user.email}")
        
        # Teacher user
        teacher_user = await prisma.utilisateur.create({
            "nom": "Martin",
            "prenom": "Jean",
            "email": "jean.martin@university.com",
            "role": "TEACHER", 
            "mdp_hash": password_hash
        })
        
        teacher_record = await prisma.enseignant.create({
            "nom": teacher_user.nom,
            "prenom": teacher_user.prenom,
            "email": teacher_user.email,
            "id_departement": dept_info.id
        })
        
        # Update user with teacher reference
        await prisma.utilisateur.update(
            where={"id": teacher_user.id},
            data={"enseignant_id": teacher_record.id}
        )
        
        print(f"✅ Created teacher: {teacher_user.email}")
        
        # Student users
        student1_user = await prisma.utilisateur.create({
            "nom": "Dupont",
            "prenom": "Alice",
            "email": "alice.dupont@university.com",
            "role": "STUDENT",
            "mdp_hash": password_hash
        })
        
        student1_record = await prisma.etudiant.create({
            "nom": student1_user.nom,
            "prenom": student1_user.prenom, 
            "email": student1_user.email,
            "id_groupe": groupe_a.id,
            "id_specialite": spec_info.id
        })
        
        # Update user with student reference
        await prisma.utilisateur.update(
            where={"id": student1_user.id},
            data={"etudiant_id": student1_record.id}
        )
        
        student2_user = await prisma.utilisateur.create({
            "nom": "Leclerc",
            "prenom": "Bob", 
            "email": "bob.leclerc@university.com",
            "role": "STUDENT",
            "mdp_hash": password_hash
        })
        
        student2_record = await prisma.etudiant.create({
            "nom": student2_user.nom,
            "prenom": student2_user.prenom,
            "email": student2_user.email, 
            "id_groupe": groupe_b.id,
            "id_specialite": spec_info.id
        })
        
        # Update user with student reference
        await prisma.utilisateur.update(
            where={"id": student2_user.id},
            data={"etudiant_id": student2_record.id}
        )
        
        print(f"✅ Created students: {student1_user.email}, {student2_user.email}")
        
        # 6. Create Subjects
        print("📚 Creating subjects...")
        
        subjects = [
            "Mathématiques Fondamentales",
            "Algorithmique et Structures de Données", 
            "Programmation Orientée Objet",
            "Bases de Données",
            "Réseaux Informatiques"
        ]
        
        for subject_name in subjects:
            await prisma.matiere.create({
                "nom": subject_name,
                "id_niveau": niveau_l1.id,
                "id_enseignant": teacher_record.id
            })
        
        print(f"✅ Created {len(subjects)} subjects")
        
        # 7. Create Rooms
        print("🏫 Creating rooms...")
        
        room_codes = ["A101", "A102", "B201", "LAB1", "LAB2"]
        for code in room_codes:
            await prisma.salle.create({
                "code": code,
                "type": "LAB" if "LAB" in code else "LECTURE",
                "capacite": 30
            })
        
        print(f"✅ Created {len(room_codes)} rooms")
        
        # Verify data creation
        print("\n📈 Verification:")
        user_count = await prisma.utilisateur.count()
        student_count = await prisma.etudiant.count()
        teacher_count = await prisma.enseignant.count()
        admin_count = await prisma.administrateur.count()
        dept_head_count = await prisma.chefdepartement.count()
        subject_count = await prisma.matiere.count()
        
        print(f"👥 Users: {user_count}")
        print(f"🎓 Students: {student_count}")
        print(f"👨‍🏫 Teachers: {teacher_count}")
        print(f"👑 Admins: {admin_count}")
        print(f"🏢 Dept Heads: {dept_head_count}")
        print(f"📚 Subjects: {subject_count}")
        
        print("\n🎉 Sample data recreation completed successfully!")
        print("\nTest accounts (all use password: password123):")
        print("📧 admin@university.com (Admin)")
        print("📧 boubaker@university.com (Department Head)")
        print("📧 jean.martin@university.com (Teacher)")
        print("📧 alice.dupont@university.com (Student)")
        print("📧 bob.leclerc@university.com (Student)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())