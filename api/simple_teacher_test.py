#!/usr/bin/env python3
"""
Simple test for teacher profile
"""

import asyncio
from prisma import Prisma

async def simple_teacher_test():
    """Simple test to check if teacher relationships work"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get the teacher user
        teacher_user = await prisma.utilisateur.find_first(
            where={"role": "TEACHER"},
            include={
                "enseignant": {
                    "include": {
                        "departement": True
                    }
                }
            }
        )
        
        if not teacher_user:
            print("❌ No teacher user found")
            return
            
        print(f"✅ Found teacher user: {teacher_user.email}")
        print(f"   Enseignant ID: {teacher_user.enseignant_id}")
        
        if teacher_user.enseignant:
            print(f"   Teacher record: {teacher_user.enseignant.nom} {teacher_user.enseignant.prenom}")
            print(f"   Department: {teacher_user.enseignant.departement.nom}")
        
        # Test the specific teacher profile query
        if teacher_user.enseignant_id:
            teacher = await prisma.enseignant.find_unique(
                where={"id": teacher_user.enseignant_id},
                include={
                    "departement": {
                        "include": {
                            "specialites": True
                        }
                    }
                }
            )
            
            if teacher:
                print(f"✅ Teacher profile query works!")
                print(f"   Department: {teacher.departement.nom}")
                print(f"   Specialties: {len(teacher.departement.specialites)}")
                
                # Test department head query separately
                dept_head = await prisma.chefdepartement.find_unique(
                    where={"id_departement": teacher.departement.id},
                    include={
                        "utilisateur": True
                    }
                )
                
                if dept_head:
                    print(f"   Department Head: {dept_head.utilisateur.nom} {dept_head.utilisateur.prenom}")
                else:
                    print("   No department head found")
            else:
                print("❌ Teacher profile query failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(simple_teacher_test())