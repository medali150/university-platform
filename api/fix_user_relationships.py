"""
Script to fix the database relationships between Utilisateur and role-specific tables.
This script will create the corresponding role-specific records for existing users.
"""

import asyncio
from prisma import Prisma
import sys
import os

# Add the parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def fix_user_relationships():
    """Create role-specific records for existing users."""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Checking existing users...")
        
        # Get all users
        users = await prisma.utilisateur.find_many()
        print(f"Found {len(users)} users")
        
        # Get existing departments for assignment
        departments = await prisma.departement.find_many()
        if not departments:
            print("⚠️  No departments found. Creating default department...")
            default_dept = await prisma.departement.create({
                "nom": "Département Informatique"
            })
            departments = [default_dept]
        
        # Get existing specialties and groups
        specialites = await prisma.specialite.find_many(include={"niveaux": {"include": {"groupes": True}}})
        if not specialites:
            print("⚠️  No specialties found. Creating default specialty and group...")
            default_specialite = await prisma.specialite.create({
                "nom": "Informatique Générale",
                "id_departement": departments[0].id
            })
            
            default_niveau = await prisma.niveau.create({
                "nom": "Licence 1",
                "id_specialite": default_specialite.id
            })
            
            default_groupe = await prisma.groupe.create({
                "nom": "Groupe A",
                "id_niveau": default_niveau.id
            })
            
            # Refresh specialites with the new data
            specialites = await prisma.specialite.find_many(include={"niveaux": {"include": {"groupes": True}}})
        
        fixed_count = 0
        
        for user in users:
            print(f"\n👤 Processing user: {user.prenom} {user.nom} ({user.role})")
            
            if user.role == "STUDENT":
                # Check if student record exists
                existing_student = await prisma.etudiant.find_first(
                    where={"email": user.email}
                )
                
                if not existing_student:
                    # Create student record
                    group = specialites[0].niveaux[0].groupes[0] if specialites[0].niveaux and specialites[0].niveaux[0].groupes else None
                    if group:
                        student = await prisma.etudiant.create({
                            "nom": user.nom,
                            "prenom": user.prenom,
                            "email": user.email,
                            "id_groupe": group.id,
                            "id_specialite": specialites[0].id
                        })
                        
                        # Update user with student reference
                        await prisma.utilisateur.update(
                            where={"id": user.id},
                            data={"etudiant_id": student.id}
                        )
                        print(f"✅ Created student record for {user.prenom} {user.nom}")
                        fixed_count += 1
                    else:
                        print(f"❌ No group available for student {user.prenom} {user.nom}")
                else:
                    print(f"ℹ️  Student record already exists for {user.prenom} {user.nom}")
            
            elif user.role == "TEACHER":
                # Check if teacher record exists
                existing_teacher = await prisma.enseignant.find_first(
                    where={"email": user.email}
                )
                
                if not existing_teacher:
                    # Create teacher record
                    teacher = await prisma.enseignant.create({
                        "nom": user.nom,
                        "prenom": user.prenom,
                        "email": user.email,
                        "id_departement": departments[0].id
                    })
                    
                    # Update user with teacher reference
                    await prisma.utilisateur.update(
                        where={"id": user.id},
                        data={"enseignant_id": teacher.id}
                    )
                    print(f"✅ Created teacher record for {user.prenom} {user.nom}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  Teacher record already exists for {user.prenom} {user.nom}")
            
            elif user.role == "DEPARTMENT_HEAD":
                # Check if department head record exists
                existing_dept_head = await prisma.chefdepartement.find_first(
                    where={"id_utilisateur": user.id}
                )
                
                if not existing_dept_head:
                    # Create department head record
                    dept_head = await prisma.chefdepartement.create({
                        "id_utilisateur": user.id,
                        "id_departement": departments[0].id
                    })
                    print(f"✅ Created department head record for {user.prenom} {user.nom}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  Department head record already exists for {user.prenom} {user.nom}")
            
            elif user.role == "ADMIN":
                # Check if admin record exists
                existing_admin = await prisma.administrateur.find_first(
                    where={"id_utilisateur": user.id}
                )
                
                if not existing_admin:
                    # Create admin record
                    admin = await prisma.administrateur.create({
                        "id_utilisateur": user.id,
                        "niveau": "ADMIN"
                    })
                    print(f"✅ Created admin record for {user.prenom} {user.nom}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  Admin record already exists for {user.prenom} {user.nom}")
        
        print(f"\n🎉 Fixed {fixed_count} user relationships!")
        
        # Verify the fix
        print("\n🔍 Verification:")
        students = await prisma.etudiant.count()
        teachers = await prisma.enseignant.count()
        dept_heads = await prisma.chefdepartement.count()
        admins = await prisma.administrateur.count()
        
        print(f"📊 Role-specific records:")
        print(f"   - Students: {students}")
        print(f"   - Teachers: {teachers}")
        print(f"   - Department Heads: {dept_heads}")
        print(f"   - Admins: {admins}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_user_relationships())