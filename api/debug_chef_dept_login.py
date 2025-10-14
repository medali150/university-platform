"""
Debug chef de département login issue
"""

import asyncio
from prisma import Prisma
import bcrypt

async def debug_chef_dept_login():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("="*80)
        print("DEBUGGING CHEF DE DÉPARTEMENT LOGIN")
        print("="*80)
        
        # Check chef de département users
        chef_emails = [
            "chef.dept1@university.tn",
            "chef.dept2@university.tn",
            "chef.dept3@university.tn"
        ]
        
        for email in chef_emails:
            print(f"\n📧 Checking: {email}")
            
            # Find user
            user = await prisma.utilisateur.find_unique(
                where={"email": email}
            )
            
            if not user:
                print(f"   ❌ User NOT found!")
                continue
            
            print(f"   ✅ User found")
            print(f"   ID: {user.id}")
            print(f"   Role: {user.role}")
            print(f"   Name: {user.prenom} {user.nom}")
            print(f"   enseignant_id: {user.enseignant_id}")
            print(f"   etudiant_id: {user.etudiant_id}")
            
            # Check ChefDepartement record
            chef_dept = await prisma.chefdepartement.find_first(
                where={"id_utilisateur": user.id},
                include={"departement": True}
            )
            
            if chef_dept:
                print(f"   ✅ ChefDepartement record found")
                print(f"   Department: {chef_dept.departement.nom}")
            else:
                print(f"   ❌ ChefDepartement record NOT found!")
                print(f"   This user has DEPARTMENT_HEAD role but no ChefDepartement link!")
            
            # Test password
            test_password = "Test123!"
            password_match = bcrypt.checkpw(
                test_password.encode('utf-8'),
                user.mdp_hash.encode('utf-8')
            )
            print(f"   Password check: {'✅ CORRECT' if password_match else '❌ WRONG'}")
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        # Count all department heads
        all_dept_heads = await prisma.utilisateur.find_many(
            where={"role": "DEPARTMENT_HEAD"}
        )
        print(f"\nTotal DEPARTMENT_HEAD users: {len(all_dept_heads)}")
        
        # Count ChefDepartement records
        all_chef_dept_records = await prisma.chefdepartement.find_many()
        print(f"Total ChefDepartement records: {len(all_chef_dept_records)}")
        
        # Check for mismatches
        if len(all_dept_heads) != len(all_chef_dept_records):
            print(f"\n⚠️ MISMATCH: {len(all_dept_heads)} users with DEPARTMENT_HEAD role but {len(all_chef_dept_records)} ChefDepartement records")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_chef_dept_login())
