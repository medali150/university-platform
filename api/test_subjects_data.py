"""
Test script to check subject data structure returned from API
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.db.prisma_client import get_prisma_instance

async def test_subjects_data():
    """Check the structure of subjects data"""
    prisma = get_prisma_instance()
    
    try:
        await prisma.connect()
        print("✅ Connected to database\n")
        
        # Get subjects with specialite relationship
        subjects = await prisma.matiere.find_many(
            include={
                "specialite": {
                    "include": {"departement": True}
                },
                "enseignant": True
            },
            order=[{"nom": "asc"}],
            take=5  # Just get first 5 for testing
        )
        
        print(f"📚 Found {len(subjects)} subjects\n")
        
        for subject in subjects:
            print(f"Subject: {subject.nom}")
            print(f"  ID: {subject.id}")
            print(f"  ID Type: {type(subject.id).__name__}")
            
            if subject.specialite:
                print(f"  Specialite ID: {subject.specialite.id}")
                print(f"  Specialite ID Type: {type(subject.specialite.id).__name__}")
                print(f"  Specialite Name: {subject.specialite.nom}")
                
                if subject.specialite.departement:
                    print(f"  Department: {subject.specialite.departement.nom}")
            else:
                print("  ⚠️ NO SPECIALITE DATA")
            
            if subject.enseignant:
                print(f"  Teacher: {subject.enseignant.prenom} {subject.enseignant.nom}")
            else:
                print("  ⚠️ NO TEACHER DATA")
            
            print()
        
        # Check specialites
        print("\n🎓 Checking Specialities:")
        specialites = await prisma.specialite.find_many(
            include={"departement": True},
            take=3
        )
        
        for spec in specialites:
            print(f"Speciality: {spec.nom}")
            print(f"  ID: {spec.id}")
            print(f"  ID Type: {type(spec.id).__name__}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()
        print("✅ Disconnected from database")

if __name__ == "__main__":
    asyncio.run(test_subjects_data())
