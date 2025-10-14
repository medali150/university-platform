#!/usr/bin/env python3
"""
Create/update test department head user with known credentials
"""
import asyncio
from prisma import Prisma
import bcrypt

async def create_test_department_head():
    """Create or update test department head user"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Hash password
        password = "test123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Get or create Informatique department
        informatique_dept = await prisma.departement.find_first(
            where={"nom": "Informatique"}
        )
        
        if not informatique_dept:
            print("❌ Informatique department not found")
            return
            
        # Create or update test user
        test_email = "test.depthead@university.com"
        
        existing_user = await prisma.utilisateur.find_first(
            where={"email": test_email}
        )
        
        if existing_user:
            # Update existing user
            user = await prisma.utilisateur.update(
                where={"id": existing_user.id},
                data={
                    "nom": "TestHead",
                    "prenom": "Department",
                    "role": "DEPARTMENT_HEAD",
                    "mdp_hash": password_hash
                }
            )
            print(f"✅ Updated existing user: {user.email}")
        else:
            # Create new user
            user = await prisma.utilisateur.create(
                data={
                    "nom": "TestHead",
                    "prenom": "Department", 
                    "email": test_email,
                    "role": "DEPARTMENT_HEAD",
                    "mdp_hash": password_hash
                }
            )
            print(f"✅ Created new user: {user.email}")
        
        # Check if ChefDepartement record exists for this department
        existing_chef_for_dept = await prisma.chefdepartement.find_first(
            where={"id_departement": informatique_dept.id}
        )
        
        if existing_chef_for_dept:
            # Update existing chef to use our test user
            chef = await prisma.chefdepartement.update(
                where={"id": existing_chef_for_dept.id},
                data={"id_utilisateur": user.id}
            )
            print(f"✅ Updated department head record for {informatique_dept.nom}")
        else:
            # Create new ChefDepartement record
            chef = await prisma.chefdepartement.create(
                data={
                    "id_utilisateur": user.id,
                    "id_departement": informatique_dept.id
                }
            )
            print(f"✅ Created department head record for {informatique_dept.nom}")
            
        print(f"\n🔐 Test Login Credentials:")
        print(f"   📧 Email: {test_email}")
        print(f"   🔑 Password: {password}")
        print(f"   🏫 Department: {informatique_dept.nom}")
        
        # Test data counts for this department
        groups_count = await prisma.groupe.count(
            where={
                "niveau": {
                    "specialite": {
                        "id_departement": informatique_dept.id
                    }
                }
            }
        )
        
        subjects_count = await prisma.matiere.count(
            where={
                "specialite": {
                    "id_departement": informatique_dept.id
                }
            }
        )
        
        specialities_count = await prisma.specialite.count(
            where={"id_departement": informatique_dept.id}
        )
        
        print(f"\n📊 Available data for this department:")
        print(f"   👥 Groups: {groups_count}")
        print(f"   📚 Subjects: {subjects_count}")
        print(f"   🎓 Specialities: {specialities_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_test_department_head())