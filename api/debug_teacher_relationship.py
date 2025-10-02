#!/usr/bin/env python3
"""
Debug teacher relationships
"""

import asyncio
from prisma import Prisma

async def debug_teacher_relationships():
    """Debug teacher user relationships"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Debugging teacher relationships...")
        
        # Find user by email
        user = await prisma.utilisateur.find_unique(
            where={"email": "jean.martin@university.com"},
            include={
                "enseignant": True
            }
        )
        
        if user:
            print(f"✅ Found user: {user.email} (role: {user.role})")
            print(f"   User ID: {user.id}")
            print(f"   Enseignant ID: {user.enseignant_id}")
            if user.enseignant:
                print(f"   Teacher record: {user.enseignant.nom} {user.enseignant.prenom}")
            else:
                print("   ❌ No teacher record linked!")
        else:
            print("❌ User not found!")
            return
        
        # Find teacher by email directly
        teacher = await prisma.enseignant.find_unique(
            where={"email": "jean.martin@university.com"}
        )
        
        if teacher:
            print(f"✅ Found teacher record: {teacher.nom} {teacher.prenom}")
            print(f"   Teacher ID: {teacher.id}")
            print(f"   Department ID: {teacher.id_departement}")
        else:
            print("❌ Teacher record not found!")
            return
        
        # Check if user.enseignant_id matches teacher.id
        if user.enseignant_id == teacher.id:
            print("✅ User-Teacher relationship is correct")
        else:
            print(f"❌ User-Teacher relationship broken!")
            print(f"   User.enseignant_id: {user.enseignant_id}")
            print(f"   Teacher.id: {teacher.id}")
            
            # Fix the relationship
            print("🔧 Fixing relationship...")
            await prisma.utilisateur.update(
                where={"id": user.id},
                data={"enseignant_id": teacher.id}
            )
            print("✅ Relationship fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_teacher_relationships())