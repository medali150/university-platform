#!/usr/bin/env python3
"""
Simple script to manually update Matiere relationships for testing
"""
import asyncio
from prisma import Prisma

async def test_database_connection():
    """Test database connection and check current data"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Testing database connection...")
        
        # Check current matieres using Prisma models
        print("\n📋 Current Matiere records:")
        try:
            matieres = await prisma.matiere.find_many(
                include={
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            )
            
            for matiere in matieres:
                niveau_nom = matiere.niveau.nom if matiere.niveau else "N/A"
                specialite_nom = matiere.niveau.specialite.nom if matiere.niveau and matiere.niveau.specialite else "N/A"
                print(f"   • {matiere.nom} (niveau: {niveau_nom}, spécialité: {specialite_nom})")
        except Exception as e:
            print(f"   Error reading matieres: {e}")
            
            # Try using the old schema temporarily
            try:
                print("   Trying with raw query...")
                result = await prisma.query_raw("""
                    SELECT m.nom, m.id_niveau 
                    FROM "Subject" m 
                    LIMIT 5
                """)
                print(f"   Raw query result: {result}")
            except Exception as e2:
                print(f"   Raw query also failed: {e2}")
        
        print("\n📊 Specialities in database:")
        specialities = await prisma.specialite.find_many(
            include={"departement": True}
        )
        
        for spec in specialities:
            print(f"   • {spec.nom} (dept: {spec.departement.nom})")
            
        print("\n🏫 Departments:")
        departments = await prisma.departement.find_many()
        for dept in departments:
            print(f"   • {dept.nom}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_database_connection())