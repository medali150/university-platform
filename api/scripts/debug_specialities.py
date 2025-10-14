#!/usr/bin/env python3
"""
Debug specialities endpoint specifically
"""
import asyncio
from prisma import Prisma

async def debug_specialities():
    """Debug the specialities endpoint issue"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get the department for the test user
        print("🔍 Getting department...")
        dept_head = await prisma.chefdepartement.find_first(
            where={
                "utilisateur": {
                    "email": "test.depthead@university.com"
                }
            },
            include={"departement": True}
        )
        
        if not dept_head:
            print("❌ Department head not found")
            return
            
        department = dept_head.departement
        print(f"✅ Department: {department.nom}")
        
        # Try the exact query from the endpoint
        print("\n🔍 Testing specialities query...")
        
        # First try without _count
        print("1️⃣ Without _count:")
        try:
            specialities_simple = await prisma.specialite.find_many(
                where={"id_departement": department.id},
                include={"departement": True},
                order=[{"nom": "asc"}]
            )
            print(f"✅ Simple query: {len(specialities_simple)} specialities")
            for spec in specialities_simple:
                print(f"   • {spec.nom}")
        except Exception as e:
            print(f"❌ Simple query failed: {e}")
        
        # Try with _count
        print("\n2️⃣ With _count:")
        try:
            specialities_with_count = await prisma.specialite.find_many(
                where={"id_departement": department.id},
                include={
                    "departement": True,
                    "_count": {
                        "select": {
                            "matieres": True,
                            "niveaux": True,
                            "etudiants": True
                        }
                    }
                },
                order=[{"nom": "asc"}]
            )
            print(f"✅ Count query: {len(specialities_with_count)} specialities")
            for spec in specialities_with_count:
                count_info = getattr(spec, '_count', {})
                print(f"   • {spec.nom} - Matières: {count_info.get('matieres', 0)}, Niveaux: {count_info.get('niveaux', 0)}, Étudiants: {count_info.get('etudiants', 0)}")
        except Exception as e:
            print(f"❌ Count query failed: {e}")
        
        # Try individual _count queries
        print("\n3️⃣ Testing individual counts:")
        try:
            for spec in specialities_simple[:3]:  # Test first 3
                matieres_count = await prisma.matiere.count(
                    where={"id_specialite": spec.id}
                )
                niveaux_count = await prisma.niveau.count(
                    where={"id_specialite": spec.id}
                )
                etudiants_count = await prisma.etudiant.count(
                    where={"id_specialite": spec.id}
                )
                print(f"   • {spec.nom}: M={matieres_count}, N={niveaux_count}, E={etudiants_count}")
        except Exception as e:
            print(f"❌ Individual counts failed: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_specialities())