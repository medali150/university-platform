"""
Check available groups in the database
"""
import asyncio
from prisma import Prisma

async def check_groups():
    db = Prisma()
    await db.connect()
    
    print("\n📋 Available Groups in Database:")
    print("="*60)
    
    try:
        groups = await db.groupe.find_many(
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                }
            }
        )
        
        if not groups:
            print("❌ No groups found in the database!")
        else:
            for group in groups:
                specialite_nom = group.niveau.specialite.nom if group.niveau and group.niveau.specialite else "N/A"
                niveau_nom = group.niveau.nom if group.niveau else "N/A"
                print(f"\n  Group: {group.nom}")
                print(f"    - ID: {group.id}")
                print(f"    - Niveau: {niveau_nom}")
                print(f"    - Spécialité: {specialite_nom}")
        
        print("\n" + "="*60)
        print(f"Total Groups: {len(groups)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_groups())
