#!/usr/bin/env python3
"""
Migration script to update Matiere relationship from Niveau to Specialite
"""
import asyncio
from prisma import Prisma

async def migrate_matiere_relationships():
    """Migrate Matiere records from niveau-based to specialite-based relationships"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Fetching existing Matiere records...")
        
        # Get all existing matieres with their niveau information
        matieres = await prisma.matiere.find_many(
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                }
            }
        )
        
        print(f"📋 Found {len(matieres)} Matiere records to migrate")
        
        # Step 1: Add the id_specialite column as nullable first
        print("🔧 Adding id_specialite column...")
        await prisma.execute_raw("""
            ALTER TABLE "Subject" ADD COLUMN IF NOT EXISTS "id_specialite" TEXT;
        """)
        
        # Step 2: Update each matiere with the correct specialite_id
        print("📝 Updating Matiere records with specialite relationships...")
        for matiere in matieres:
            if matiere.niveau and matiere.niveau.specialite:
                specialite_id = matiere.niveau.specialite.id
                print(f"   • Updating {matiere.nom} -> {matiere.niveau.specialite.nom}")
                
                await prisma.execute_raw("""
                    UPDATE "Subject" 
                    SET "id_specialite" = $1 
                    WHERE "id" = $2
                """, specialite_id, matiere.id)
        
        # Step 3: Make id_specialite NOT NULL and add foreign key constraint
        print("🔒 Making id_specialite required and adding constraints...")
        await prisma.execute_raw("""
            ALTER TABLE "Subject" 
            ALTER COLUMN "id_specialite" SET NOT NULL;
        """)
        
        await prisma.execute_raw("""
            ALTER TABLE "Subject" 
            ADD CONSTRAINT "Subject_id_specialite_fkey" 
            FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;
        """)
        
        # Step 4: Create index for performance
        await prisma.execute_raw("""
            CREATE INDEX IF NOT EXISTS "Subject_id_specialite_idx" ON "Subject"("id_specialite");
        """)
        
        # Step 5: Drop the old niveau relationship
        print("🗑️ Removing old niveau relationship...")
        await prisma.execute_raw("""
            ALTER TABLE "Subject" DROP CONSTRAINT IF EXISTS "Subject_id_niveau_fkey";
        """)
        
        await prisma.execute_raw("""
            DROP INDEX IF EXISTS "Subject_id_niveau_idx";
        """)
        
        await prisma.execute_raw("""
            ALTER TABLE "Subject" DROP COLUMN IF EXISTS "id_niveau";
        """)
        
        print("✅ Migration completed successfully!")
        
        # Verify the migration
        print("🔍 Verifying migration...")
        updated_matieres = await prisma.matiere.find_many(
            include={
                "specialite": {
                    "include": {
                        "departement": True
                    }
                }
            }
        )
        
        print(f"📊 Verification: {len(updated_matieres)} Matiere records now linked to specialites:")
        for matiere in updated_matieres:
            if matiere.specialite:
                print(f"   • {matiere.nom} -> {matiere.specialite.nom} ({matiere.specialite.departement.nom})")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(migrate_matiere_relationships())