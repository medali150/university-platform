"""
Check database for existing absences and create test data
"""
import asyncio
from prisma import Prisma

async def check_absences():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Check if we have any absences
        absences = await prisma.absence.find_many(
            include={
                "etudiant": {
                    "include": {"utilisateur": True}
                },
                "emploitemps": {
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {"utilisateur": True}
                        },
                        "groupe": True
                    }
                }
            }
        )
        
        print(f"Found {len(absences)} absences in database")
        
        for absence in absences[:3]:  # Show first 3
            student = absence.etudiant.utilisateur
            teacher = absence.emploitemps.enseignant.utilisateur
            subject = absence.emploitemps.matiere.nom
            
            print(f"\nAbsence ID: {absence.id}")
            print(f"Student: {student.prenom} {student.nom}")
            print(f"Teacher: {teacher.prenom} {teacher.nom}")
            print(f"Subject: {subject}")
            print(f"Status: {absence.statut}")
            print(f"Date: {absence.emploitemps.date}")
            print(f"Time: {absence.emploitemps.heure_debut}-{absence.emploitemps.heure_fin}")
        
        # If no absences, create one for testing
        if len(absences) == 0:
            print("\nNo absences found. Let's check if we can create test data...")
            
            # Find a student and schedule to create test absence
            students = await prisma.etudiant.find_many(
                include={"utilisateur": True}
            )
            
            schedules = await prisma.emploitemps.find_many(
                include={
                    "matiere": True,
                    "enseignant": True,
                    "groupe": True
                }
            )
            
            if students and schedules:
                student = students[0]
                schedule = schedules[0]
                
                print(f"Creating test absence for {student.utilisateur.prenom} {student.utilisateur.nom}")
                
                new_absence = await prisma.absence.create(
                    data={
                        "id_etudiant": student.id,
                        "id_emploitemps": schedule.id,
                        "motif": "Test absence for API testing",
                        "statut": "pending_review"
                    }
                )
                
                print(f"Created test absence with ID: {new_absence.id}")
            else:
                print("No students or schedules found to create test data")
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_absences())