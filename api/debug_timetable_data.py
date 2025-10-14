"""
Debug and check the database structure for timetable
"""
import asyncio
from prisma import Prisma

async def debug_timetable_data():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== Checking EmploiTemps (Schedule) records ===")
        schedules = await prisma.emploitemps.find_many(
            include={
                "matiere": True,
                "enseignant": {
                    "include": {"utilisateur": True}
                },
                "salle": True,
                "groupe": True
            }
        )
        
        print(f"Found {len(schedules)} schedule entries")
        
        if schedules:
            for i, schedule in enumerate(schedules[:3]):  # Show first 3
                print(f"\nSchedule {i+1}:")
                print(f"  ID: {schedule.id}")
                print(f"  Date: {schedule.date}")
                print(f"  Day: {schedule.date.isoweekday() if schedule.date else 'None'}")
                print(f"  Start: {schedule.heure_debut}")
                print(f"  End: {schedule.heure_fin}")
                print(f"  Subject: {schedule.matiere.nom if schedule.matiere else 'None'}")
                print(f"  Teacher: {schedule.enseignant.utilisateur.nom if schedule.enseignant and schedule.enseignant.utilisateur else 'None'}")
                print(f"  Room: {schedule.salle.code if schedule.salle else 'None'}")
                print(f"  Group: {schedule.groupe.nom if schedule.groupe else 'None'}")
        
        print("\n=== Checking wahid's teacher profile ===")
        
        # Get wahid's user info
        wahid_user = await prisma.utilisateur.find_unique(
            where={"email": "wahid@gmail.com"}
        )
        
        if wahid_user:
            print(f"Wahid User ID: {wahid_user.id}")
            print(f"Wahid Role: {wahid_user.role}")
            print(f"Wahid enseignant_id: {wahid_user.enseignant_id}")
            
            if wahid_user.enseignant_id:
                teacher = await prisma.enseignant.find_unique(
                    where={"id": wahid_user.enseignant_id}
                )
                print(f"Teacher found: {teacher.nom if teacher else 'None'}")
                
                # Get schedules for this teacher
                teacher_schedules = await prisma.emploitemps.find_many(
                    where={"id_enseignant": wahid_user.enseignant_id}
                )
                print(f"Teacher has {len(teacher_schedules)} scheduled classes")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_timetable_data())