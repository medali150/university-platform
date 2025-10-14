"""
Script to add students for Technologie d'Informatique department
Creates sample students with proper department, specialty, level, and group assignments
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.db.prisma_client import get_prisma_instance
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def add_students_ti():
    """Add students for Technologie d'Informatique department"""
    prisma = get_prisma_instance()
    
    try:
        await prisma.connect()
        print("✅ Connected to database\n")
        
        # Find Technologie d'Informatique department
        ti_dept = await prisma.departement.find_first(
            where={
                "OR": [
                    {"nom": {"contains": "Informatique", "mode": "insensitive"}},
                    {"nom": {"contains": "Technologies", "mode": "insensitive"}},
                    {"nom": {"contains": "Technologie", "mode": "insensitive"}}
                ]
            }
        )
        
        if not ti_dept:
            print("❌ Technologie d'Informatique department not found!")
            print("\n📋 Available departments:")
            all_depts = await prisma.departement.find_many()
            for dept in all_depts:
                print(f"  - {dept.nom} (ID: {dept.id})")
            return
        
        print(f"🎓 Found department: {ti_dept.nom} (ID: {ti_dept.id})\n")
        
        # Get specialties in this department
        specialties = await prisma.specialite.find_many(
            where={"id_departement": ti_dept.id},
            include={"niveaux": True}
        )
        
        if not specialties:
            print(f"❌ No specialties found in {ti_dept.nom}")
            return
        
        print(f"📚 Found {len(specialties)} specialties:")
        for spec in specialties:
            print(f"  - {spec.nom} (ID: {spec.id}) - {len(spec.niveaux)} levels")
        
        # Get groups in this department
        groups = await prisma.groupe.find_many(
            where={
                "niveau": {
                    "specialite": {
                        "id_departement": ti_dept.id
                    }
                }
            },
            include={
                "niveau": {
                    "include": {"specialite": True}
                }
            }
        )
        
        print(f"\n👥 Found {len(groups)} groups:")
        for group in groups:
            print(f"  - {group.nom} (Level: {group.niveau.nom}, Specialty: {group.niveau.specialite.nom})")
        
        if not groups:
            print("❌ No groups found! Please create groups first.")
            return
        
        # Sample students to create
        students_data = [
            {"nom": "Benali", "prenom": "Ahmed", "email": "ahmed.benali@student.tn"},
            {"nom": "Trabelsi", "prenom": "Fatma", "email": "fatma.trabelsi@student.tn"},
            {"nom": "Gharbi", "prenom": "Mohamed", "email": "mohamed.gharbi@student.tn"},
            {"nom": "Sassi", "prenom": "Leila", "email": "leila.sassi@student.tn"},
            {"nom": "Kacem", "prenom": "Youssef", "email": "youssef.kacem@student.tn"},
            {"nom": "Mezghani", "prenom": "Sara", "email": "sara.mezghani@student.tn"},
            {"nom": "Hammami", "prenom": "Karim", "email": "karim.hammami@student.tn"},
            {"nom": "Jebali", "prenom": "Amira", "email": "amira.jebali@student.tn"},
            {"nom": "Mansouri", "prenom": "Rami", "email": "rami.mansouri@student.tn"},
            {"nom": "Baklouti", "prenom": "Nour", "email": "nour.baklouti@student.tn"},
            {"nom": "Agrebi", "prenom": "Amine", "email": "amine.agrebi@student.tn"},
            {"nom": "Toumi", "prenom": "Yasmine", "email": "yasmine.toumi@student.tn"},
            {"nom": "Chebbi", "prenom": "Omar", "email": "omar.chebbi@student.tn"},
            {"nom": "Slimani", "prenom": "Salma", "email": "salma.slimani@student.tn"},
            {"nom": "Dridi", "prenom": "Fares", "email": "fares.dridi@student.tn"},
            {"nom": "Bouaziz", "prenom": "Ines", "email": "ines.bouaziz@student.tn"},
            {"nom": "Tlili", "prenom": "Mehdi", "email": "mehdi.tlili@student.tn"},
            {"nom": "Kouki", "prenom": "Rim", "email": "rim.kouki@student.tn"},
            {"nom": "Hamdi", "prenom": "Sami", "email": "sami.hamdi@student.tn"},
            {"nom": "Zaidi", "prenom": "Marwa", "email": "marwa.zaidi@student.tn"}
        ]
        
        # Default password
        default_password = "Student@2024"
        hashed_password = pwd_context.hash(default_password)
        
        print(f"\n🔐 Using default password: {default_password}")
        print(f"\n👨‍🎓 Creating {len(students_data)} students...\n")
        
        created_count = 0
        skipped_count = 0
        
        # Distribute students across groups
        group_index = 0
        
        for i, student_data in enumerate(students_data):
            # Check if user already exists
            existing_user = await prisma.utilisateur.find_unique(
                where={"email": student_data["email"]}
            )
            
            if existing_user:
                print(f"⚠️  Skipped: {student_data['prenom']} {student_data['nom']} - Email already exists")
                skipped_count += 1
                continue
            
            # Select group (round-robin distribution)
            selected_group = groups[group_index % len(groups)]
            group_index += 1
            
            try:
                # Create user account
                user = await prisma.utilisateur.create(
                    data={
                        "email": student_data["email"],
                        "nom": student_data["nom"],
                        "prenom": student_data["prenom"],
                        "mot_de_passe": hashed_password,
                        "role": "STUDENT",
                        "is_active": True
                    }
                )
                
                # Create student record
                student = await prisma.etudiant.create(
                    data={
                        "id_utilisateur": user.id,
                        "nom": student_data["nom"],
                        "prenom": student_data["prenom"],
                        "email": student_data["email"],
                        "id_groupe": selected_group.id
                    }
                )
                
                created_count += 1
                print(f"✅ Created: {student.prenom} {student.nom}")
                print(f"   Email: {student.email}")
                print(f"   Group: {selected_group.nom}")
                print(f"   Level: {selected_group.niveau.nom}")
                print(f"   Specialty: {selected_group.niveau.specialite.nom}")
                print()
                
            except Exception as e:
                print(f"❌ Error creating {student_data['prenom']} {student_data['nom']}: {e}")
                continue
        
        print("\n" + "="*60)
        print(f"📊 Summary:")
        print(f"   ✅ Created: {created_count} students")
        print(f"   ⚠️  Skipped: {skipped_count} students (already exist)")
        print(f"   🎓 Department: {ti_dept.nom}")
        print(f"   👥 Distributed across {len(groups)} groups")
        print("="*60)
        
        # Show distribution
        print(f"\n📈 Student distribution by group:")
        for group in groups:
            student_count = await prisma.etudiant.count(
                where={"id_groupe": group.id}
            )
            print(f"   {group.nom}: {student_count} students")
        
        print(f"\n🔐 Login credentials:")
        print(f"   Email: <student_email>")
        print(f"   Password: {default_password}")
        print(f"\n   Example: ahmed.benali@student.tn / {default_password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()
        print("\n✅ Disconnected from database")

if __name__ == "__main__":
    print("="*60)
    print("🎓 Adding Students to Technologie d'Informatique")
    print("="*60)
    print()
    asyncio.run(add_students_ti())
