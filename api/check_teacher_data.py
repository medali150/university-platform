"""
Check which teachers have schedules and subjects
"""

import asyncio
from prisma import Prisma

async def check_teacher_data():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("="*80)
        print("CHECKING TEACHER DATA")
        print("="*80)
        
        # Get all teachers
        teachers = await prisma.enseignant.find_many()
        
        for teacher in teachers[:5]:  # Check first 5 teachers
            print(f"\n👨‍🏫 {teacher.prenom} {teacher.nom} ({teacher.email})")
            print(f"   ID: {teacher.id}")
            
            # Check subjects
            subjects = await prisma.matiere.find_many(
                where={"id_enseignant": teacher.id}
            )
            print(f"   Subjects: {len(subjects)}")
            for subject in subjects:
                print(f"     - {subject.nom}")
            
            # Check schedules
            schedules = await prisma.emploitemps.find_many(
                where={"id_enseignant": teacher.id}
            )
            print(f"   Schedules: {len(schedules)}")
            if schedules:
                for schedule in schedules[:3]:
                    print(f"     - {schedule.date} {schedule.heure_debut}")
        
        print("\n" + "="*80)
        
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_teacher_data())
