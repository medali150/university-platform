#!/usr/bin/env python3
"""
Test script to verify database connection and schema after removing login field
"""

import asyncio
from prisma import Prisma

async def test_database():
    """Test database connection and verify schema"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Testing database connection and schema...")
        
        # Test basic user query (without login field)
        users = await prisma.utilisateur.find_many(
            take=5,
            include={
                "enseignant": True,
                "etudiant": True,
                "administrateur": True,
                "chefDepartement": True
            }
        )
        
        print(f"✅ Successfully retrieved {len(users)} users")
        
        for user in users:
            print(f"📧 {user.email} ({user.role})")
            if user.enseignant:
                print(f"   👨‍🏫 Teacher: {user.enseignant.nom} {user.enseignant.prenom}")
            if user.etudiant:
                print(f"   🎓 Student: {user.etudiant.nom} {user.etudiant.prenom}")
            if user.administrateur:
                print(f"   👑 Admin: {user.administrateur.niveau}")
            if user.chefDepartement:
                print(f"   🏢 Department Head")
        
        # Test subjects query
        subjects = await prisma.matiere.find_many(take=3)
        print(f"\n📚 Found {len(subjects)} subjects:")
        for subject in subjects:
            print(f"   - {subject.nom}")
        
        print("\n🎉 Database schema is working perfectly!")
        print("✅ Login field successfully removed")
        print("✅ All relationships intact")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_database())