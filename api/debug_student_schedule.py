#!/usr/bin/env python3
"""
Debug student schedule endpoint by checking database schema
"""
import asyncio
from prisma import Prisma

async def debug_student_schedule():
    """Check student and related table schemas"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get our test student
        student = await prisma.etudiant.find_first(
            where={"email": "ahmed.student@university.edu"}
        )
        
        if student:
            print(f"✅ Found student: {student.nom} {student.prenom}")
            print(f"   Student ID: {student.id}")
            print(f"   Group ID: {student.id_groupe}")
            
            # Check if student has a group
            if student.id_groupe:
                group = await prisma.groupe.find_unique(
                    where={"id": student.id_groupe}
                )
                if group:
                    print(f"✅ Student belongs to group: {group.nom}")
                else:
                    print("❌ Group not found")
            else:
                print("❌ Student has no group assigned")
            
            # Check schedules for this group
            if student.id_groupe:
                schedules = await prisma.emploitemps.find_many(
                    where={"id_groupe": student.id_groupe},
                    take=5  # Just first 5
                )
                print(f"📅 Found {len(schedules)} schedules for this group")
                
                if schedules:
                    schedule = schedules[0]
                    print(f"   Sample schedule fields:")
                    print(f"   - id: {schedule.id}")
                    print(f"   - date: {schedule.date}")
                    print(f"   - heure_debut: {schedule.heure_debut}")
                    print(f"   - heure_fin: {schedule.heure_fin}")
                    print(f"   - id_matiere: {schedule.id_matiere}")
                    print(f"   - id_enseignant: {schedule.id_enseignant}")
                    print(f"   - id_salle: {schedule.id_salle}")
        else:
            print("❌ Test student not found")
            
            # Check if any students exist
            all_students = await prisma.etudiant.find_many(take=3)
            print(f"📊 Found {len(all_students)} total students in database")
            for s in all_students:
                print(f"   - {s.nom} {s.prenom} ({s.email})")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_student_schedule())