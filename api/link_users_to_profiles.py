"""
Link existing user accounts to their teacher/student profiles.
This script updates the enseignant_id and etudiant_id fields in the Utilisateur table.
"""

import asyncio
import os
from prisma import Prisma

# Set the database URL
os.environ['DATABASE_URL'] = "postgresql://postgres:dali2004@localhost:5432/universety_db"

async def link_users_to_profiles():
    prisma = Prisma()
    await prisma.connect()
    
    print("=" * 80)
    print("LINKING USER ACCOUNTS TO PROFILES")
    print("=" * 80)
    
    try:
        # 1. Link Teachers
        print("\n👨‍🏫 Linking Teachers...")
        teachers_count = 0
        
        # Get all teachers
        teachers = await prisma.enseignant.find_many()
        
        for teacher in teachers:
            # Find the user with matching email
            user = await prisma.utilisateur.find_unique(
                where={"email": teacher.email}
            )
            
            if user and not user.enseignant_id:
                # Update the user to link to this teacher
                await prisma.utilisateur.update(
                    where={"id": user.id},
                    data={"enseignant_id": teacher.id}
                )
                print(f"  ✅ Linked: {teacher.prenom} {teacher.nom} ({teacher.email})")
                teachers_count += 1
            elif user and user.enseignant_id:
                print(f"  ✓ Already linked: {teacher.prenom} {teacher.nom}")
        
        print(f"\n✅ Linked {teachers_count} teacher accounts")
        
        # 2. Link Students
        print("\n👨‍🎓 Linking Students...")
        students_count = 0
        
        # Get all students
        students = await prisma.etudiant.find_many()
        
        for student in students:
            # Find the user with matching email
            user = await prisma.utilisateur.find_unique(
                where={"email": student.email}
            )
            
            if user and not user.etudiant_id:
                # Update the user to link to this student
                await prisma.utilisateur.update(
                    where={"id": user.id},
                    data={"etudiant_id": student.id}
                )
                students_count += 1
                if students_count <= 10:  # Only print first 10 to avoid clutter
                    print(f"  ✅ Linked: {student.prenom} {student.nom} ({student.email})")
            elif user and user.etudiant_id:
                if students_count == 0:  # Only print first one
                    print(f"  ✓ Already linked: {student.prenom} {student.nom}")
        
        if students_count > 10:
            print(f"  ✅ ... and {students_count - 10} more students")
        
        print(f"\n✅ Linked {students_count} student accounts")
        
        print("\n" + "=" * 80)
        print("LINKING COMPLETE!")
        print("=" * 80)
        print(f"\n📊 SUMMARY:")
        print(f"  👨‍🏫 Teachers linked: {teachers_count}")
        print(f"  👨‍🎓 Students linked: {students_count}")
        print(f"  Total: {teachers_count + students_count}")
        print("\n✅ All user accounts are now properly linked to their profiles!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(link_users_to_profiles())
