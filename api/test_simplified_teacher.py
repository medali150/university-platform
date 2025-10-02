#!/usr/bin/env python3
"""
Test the simplified teacher profile queries
"""

import asyncio
from prisma import Prisma

async def test_simplified_queries():
    """Test the simplified database queries"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Testing simplified teacher profile queries...")
        
        # Get the teacher user first
        teacher_user = await prisma.utilisateur.find_first(
            where={"role": "TEACHER"}
        )
        
        if not teacher_user:
            print("❌ No teacher user found")
            return
            
        print(f"✅ Found teacher user: {teacher_user.email}")
        print(f"   Enseignant ID: {teacher_user.enseignant_id}")
        
        # Test the teacher profile query (simplified)
        if teacher_user.enseignant_id:
            teacher = await prisma.enseignant.find_unique(
                where={"id": teacher_user.enseignant_id},
                include={
                    "departement": {
                        "include": {
                            "specialites": {
                                "include": {
                                    "niveaux": True
                                }
                            }
                        }
                    }
                }
            )
            
            if teacher:
                print(f"✅ Teacher record found: {teacher.nom} {teacher.prenom}")
                print(f"   Department: {teacher.departement.nom}")
                print(f"   Specialties: {len(teacher.departement.specialites)}")
                
                # Test department head query (simplified)
                dept_head_record = await prisma.chefdepartement.find_unique(
                    where={"id_departement": teacher.departement.id}
                )
                
                if dept_head_record:
                    print(f"✅ Department head record found: {dept_head_record.id}")
                    
                    # Get the user info
                    dept_head_user = await prisma.utilisateur.find_unique(
                        where={"id": dept_head_record.id_utilisateur}
                    )
                    
                    if dept_head_user:
                        print(f"✅ Department head user: {dept_head_user.nom} {dept_head_user.prenom}")
                    else:
                        print("❌ Department head user not found")
                else:
                    print("❌ No department head record found")
                
                # Test subjects query
                subjects = await prisma.matiere.find_many(
                    where={"id_enseignant": teacher.id},
                    include={
                        "niveau": {
                            "include": {
                                "specialite": True
                            }
                        }
                    }
                )
                
                print(f"✅ Found {len(subjects)} subjects taught by teacher")
                for subject in subjects:
                    print(f"   - {subject.nom} (Level: {subject.niveau.nom})")
                
            else:
                print("❌ Teacher record not found")
        
        print("\n🎉 All simplified queries working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_simplified_queries())