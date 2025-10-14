"""
Check if user accounts are properly linked to profiles
"""

import asyncio
from prisma import Prisma

async def check_links():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("="*80)
        print("CHECKING USER PROFILE LINKS")
        print("="*80)
        
        # Check a few teacher accounts
        print("\n👨‍🏫 Checking Teacher Accounts...")
        for i in range(1, 4):
            email = f"teacher{i}@university.tn"
            user = await prisma.utilisateur.find_unique(
                where={"email": email}
            )
            
            if user:
                print(f"\n  Email: {email}")
                print(f"  User ID: {user.id}")
                print(f"  Role: {user.role}")
                print(f"  enseignant_id: {user.enseignant_id}")
                print(f"  etudiant_id: {user.etudiant_id}")
                
                if user.enseignant_id:
                    teacher = await prisma.enseignant.find_unique(
                        where={"id": user.enseignant_id}
                    )
                    if teacher:
                        print(f"  ✅ Linked to teacher: {teacher.prenom} {teacher.nom}")
                    else:
                        print(f"  ❌ enseignant_id points to non-existent teacher!")
                else:
                    # Check if teacher profile exists
                    teacher = await prisma.enseignant.find_unique(
                        where={"email": email}
                    )
                    if teacher:
                        print(f"  ⚠️ Teacher profile exists but NOT linked!")
                        print(f"     Teacher ID: {teacher.id}")
                    else:
                        print(f"  ❌ No teacher profile found")
        
        # Check a few student accounts
        print("\n\n👨‍🎓 Checking Student Accounts...")
        for i in range(1, 4):
            email = f"student{i}@university.tn"
            user = await prisma.utilisateur.find_unique(
                where={"email": email}
            )
            
            if user:
                print(f"\n  Email: {email}")
                print(f"  User ID: {user.id}")
                print(f"  Role: {user.role}")
                print(f"  enseignant_id: {user.enseignant_id}")
                print(f"  etudiant_id: {user.etudiant_id}")
                
                if user.etudiant_id:
                    student = await prisma.etudiant.find_unique(
                        where={"id": user.etudiant_id}
                    )
                    if student:
                        print(f"  ✅ Linked to student: {student.prenom} {student.nom}")
                    else:
                        print(f"  ❌ etudiant_id points to non-existent student!")
                else:
                    # Check if student profile exists
                    student = await prisma.etudiant.find_unique(
                        where={"email": email}
                    )
                    if student:
                        print(f"  ⚠️ Student profile exists but NOT linked!")
                        print(f"     Student ID: {student.id}")
                    else:
                        print(f"  ❌ No student profile found")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_links())
