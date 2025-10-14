"""
Database migration script to add coefficient field to Matiere table
"""
import asyncio
from prisma import Prisma

async def migrate_add_coefficient():
    """Add coefficient field to existing matiere records"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔄 Starting migration: Adding coefficient to Matiere table...")
        
        # Get all existing subjects without coefficient
        subjects = await prisma.matiere.find_many()
        
        print(f"📊 Found {len(subjects)} subjects to update")
        
        # Update each subject to have default coefficient of 1.0
        updated_count = 0
        for subject in subjects:
            await prisma.matiere.update(
                where={"id": subject.id},
                data={"coefficient": 1.0}
            )
            updated_count += 1
            print(f"✅ Updated subject '{subject.nom}' with coefficient 1.0")
        
        print(f"🎉 Migration completed! Updated {updated_count} subjects")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(migrate_add_coefficient())