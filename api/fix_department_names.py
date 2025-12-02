"""
Update department names to correct French spelling
"""
import asyncio
from prisma import Prisma

async def fix_departments():
    db = Prisma()
    await db.connect()
    
    print("="*60)
    print("🔧 FIXING DEPARTMENT NAMES")
    print("="*60)
    
    try:
        # Get current departments
        departments = await db.departement.find_many()
        
        print(f"\n📋 Current Departments ({len(departments)}):")
        for dept in departments:
            print(f"  - {dept.nom}")
        
        # Mapping of incorrect to correct names
        corrections = {
            "technologie d'Informatique": "Informatique",
            "génie mécanique": "Génie Mécanique",
            "génie électrique": "Génie Électrique",
            "génie cevil": "Génie Civil"
        }
        
        print(f"\n🔄 Applying corrections...")
        updated = 0
        
        for dept in departments:
            if dept.nom in corrections:
                new_name = corrections[dept.nom]
                await db.departement.update(
                    where={'id': dept.id},
                    data={'nom': new_name}
                )
                print(f"  ✅ {dept.nom} → {new_name}")
                updated += 1
            else:
                print(f"  ⏭️  {dept.nom} (no change needed)")
        
        print(f"\n📊 Summary:")
        print(f"  - Total departments: {len(departments)}")
        print(f"  - Updated: {updated}")
        print(f"  - Unchanged: {len(departments) - updated}")
        
        # Show final state
        print(f"\n✅ Final Department Names:")
        departments = await db.departement.find_many()
        for dept in departments:
            print(f"  - {dept.nom}")
        
        print("\n" + "="*60)
        print("✅ DEPARTMENT NAMES UPDATED!")
        print("="*60)
        print("\n💡 Next Steps:")
        print("  1. Regenerate Excel templates: python create_excel_templates.py")
        print("  2. Use the new templates for bulk import")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_departments())
