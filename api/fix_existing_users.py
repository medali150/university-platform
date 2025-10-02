#!/usr/bin/env python3
"""
Fix existing users by creating their missing role-specific records.
This script will check all users in the Utilisateur table and create 
corresponding records in role-specific tables if they don't exist.
"""

import asyncio
from prisma import Prisma

async def fix_existing_users():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Checking existing users and their role-specific records...")
        
        # Get all users
        users = await prisma.utilisateur.find_many()
        print(f"Found {len(users)} users in total")
        
        # Get default data for role-specific tables
        default_department = await prisma.departement.find_first()
        default_specialty = await prisma.specialite.find_first()
        default_group = await prisma.groupe.find_first()
        
        if not default_department or not default_specialty or not default_group:
            print("❌ Error: Default department, specialty, or group not found!")
            return
        
        print(f"📋 Using defaults:")
        print(f"   Department: {default_department.nom}")
        print(f"   Specialty: {default_specialty.nom}")
        print(f"   Group: {default_group.nom}")
        print()
        
        fixed_count = 0
        
        for user in users:
            print(f"👤 Processing user: {user.prenom} {user.nom} ({user.role})")
            
            if user.role == "STUDENT":
                # Check if student record exists
                existing_student = None
                if user.etudiant_id:
                    existing_student = await prisma.etudiant.find_unique(
                        where={"id": user.etudiant_id}
                    )
                
                if not existing_student:
                    # Create student record
                    student = await prisma.etudiant.create(
                        data={
                            "nom": user.nom,
                            "prenom": user.prenom,
                            "email": user.email,
                            "id_groupe": default_group.id,
                            "id_specialite": default_specialty.id
                        }
                    )
                    # Update user with student relation
                    await prisma.utilisateur.update(
                        where={"id": user.id},
                        data={"etudiant_id": student.id}
                    )
                    print(f"   ✅ Created student record")
                    fixed_count += 1
                else:
                    print(f"   ✓ Student record already exists")
                    
            elif user.role == "TEACHER":
                # Check if teacher record exists
                existing_teacher = None
                if user.enseignant_id:
                    existing_teacher = await prisma.enseignant.find_unique(
                        where={"id": user.enseignant_id}
                    )
                
                if not existing_teacher:
                    # Create teacher record
                    teacher = await prisma.enseignant.create(
                        data={
                            "nom": user.nom,
                            "prenom": user.prenom,
                            "email": user.email,
                            "id_departement": default_department.id
                        }
                    )
                    # Update user with teacher relation
                    await prisma.utilisateur.update(
                        where={"id": user.id},
                        data={"enseignant_id": teacher.id}
                    )
                    print(f"   ✅ Created teacher record")
                    fixed_count += 1
                else:
                    print(f"   ✓ Teacher record already exists")
                    
            elif user.role == "DEPARTMENT_HEAD":
                # Check if department head record exists
                existing_dept_head = await prisma.chefdepartement.find_unique(
                    where={"id_utilisateur": user.id}
                )
                
                if not existing_dept_head:
                    # Create department head record
                    await prisma.chefdepartement.create(
                        data={
                            "id_utilisateur": user.id,
                            "id_departement": default_department.id
                        }
                    )
                    print(f"   ✅ Created department head record")
                    fixed_count += 1
                else:
                    print(f"   ✓ Department head record already exists")
                    
            elif user.role == "ADMIN":
                # Check if admin record exists
                existing_admin = await prisma.administrateur.find_unique(
                    where={"id_utilisateur": user.id}
                )
                
                if not existing_admin:
                    # Create admin record
                    await prisma.administrateur.create(
                        data={
                            "id_utilisateur": user.id,
                            "niveau": "ADMIN"
                        }
                    )
                    print(f"   ✅ Created admin record")
                    fixed_count += 1
                else:
                    print(f"   ✓ Admin record already exists")
            
            print()
        
        print(f"🎉 Fixed {fixed_count} users with missing role-specific records")
        
        # Verify the fix
        print("\n📊 Final verification:")
        students = await prisma.etudiant.count()
        teachers = await prisma.enseignant.count()
        dept_heads = await prisma.chefdepartement.count()
        admins = await prisma.administrateur.count()
        
        print(f"   Students: {students}")
        print(f"   Teachers: {teachers}")
        print(f"   Department Heads: {dept_heads}")
        print(f"   Admins: {admins}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_existing_users())