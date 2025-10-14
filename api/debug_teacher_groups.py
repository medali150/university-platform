#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager

async def debug_teacher_groups():
    """Debug the teacher groups query to see what's wrong"""
    print("=== DEBUGGING TEACHER GROUPS QUERY ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Get wahid's teacher ID
        user_wahid = await prisma.utilisateur.find_unique(
            where={"email": "wahid@gmail.com"},
            include={"enseignant": True}
        )
        
        if not user_wahid or not user_wahid.enseignant:
            print("❌ Wahid teacher not found")
            return
        
        teacher_id = user_wahid.enseignant.id
        print(f"✅ Teacher ID: {teacher_id}")
        
        # Get subjects taught by teacher
        print("\n📚 Getting subjects...")
        subjects = await prisma.matiere.find_many(
            where={"id_enseignant": teacher_id}
        )
        print(f"✅ Found {len(subjects)} subjects")
        for subject in subjects:
            print(f"   - {subject.nom} (ID: {subject.id})")
        
        # Get groups through subjects
        print("\n👥 Getting groups through subjects...")
        for subject in subjects:
            print(f"\n   Subject: {subject.nom}")
            
            # Get the specialty for this subject
            specialty = await prisma.specialite.find_unique(
                where={"id": subject.id_specialite},
                include={
                    "niveaux": {
                        "include": {
                            "groupes": {
                                "include": {
                                    "etudiants": True
                                }
                            }
                        }
                    }
                }
            )
            
            if specialty:
                print(f"   Specialty: {specialty.nom}")
                for level in specialty.niveaux:
                    print(f"     Level: {level.nom}")
                    for group in level.groupes:
                        print(f"       Group: {group.nom} ({len(group.etudiants)} students)")
        
        # Alternative approach - get groups through schedule
        print("\n📅 Getting groups through schedule...")
        schedules = await prisma.emploitemps.find_many(
            where={"id_enseignant": teacher_id},
            include={
                "groupe": {
                    "include": {
                        "niveau": {
                            "include": {
                                "specialite": True
                            }
                        }
                    }
                },
                "matiere": True
            }
        )
        
        print(f"✅ Found {len(schedules)} schedule items")
        unique_groups = {}
        for schedule in schedules:
            group_id = schedule.groupe.id
            if group_id not in unique_groups:
                unique_groups[group_id] = {
                    "id": schedule.groupe.id,
                    "nom": schedule.groupe.nom,
                    "niveau": schedule.groupe.niveau.nom,
                    "specialite": schedule.groupe.niveau.specialite.nom
                }
        
        print(f"✅ Unique groups from schedule: {len(unique_groups)}")
        for group in unique_groups.values():
            print(f"   - {group['nom']} ({group['niveau']} - {group['specialite']})")
        
        # Get students count for each group
        print("\n👨‍🎓 Getting student counts...")
        for group_id in unique_groups.keys():
            students = await prisma.etudiant.find_many(
                where={"id_groupe": group_id}
            )
            print(f"   Group {unique_groups[group_id]['nom']}: {len(students)} students")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_teacher_groups())