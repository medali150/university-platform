#!/usr/bin/env python3
"""
Complete the migration by removing old id_niveau constraint and column
"""
import asyncio
from prisma import Prisma

async def complete_migration():
    """Complete the migration by cleaning up old schema"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔧 Completing the database migration...")
        
        # Step 1: Make id_niveau nullable first
        print("\n1️⃣ Making id_niveau nullable...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" ALTER COLUMN "id_niveau" DROP NOT NULL;
            """)
            print("   ✅ id_niveau is now nullable")
        except Exception as e:
            print(f"   ⚠️ Column might already be nullable: {e}")
        
        # Step 2: Drop the foreign key constraint first
        print("\n2️⃣ Dropping old foreign key constraint...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" DROP CONSTRAINT IF EXISTS "Subject_id_niveau_fkey";
            """)
            print("   ✅ Foreign key constraint dropped")
        except Exception as e:
            print(f"   ⚠️ Constraint might not exist: {e}")
        
        # Step 3: Drop the index
        print("\n3️⃣ Dropping old index...")
        try:
            await prisma.execute_raw("""
                DROP INDEX IF EXISTS "Subject_id_niveau_idx";
            """)
            print("   ✅ Index dropped")
        except Exception as e:
            print(f"   ⚠️ Index might not exist: {e}")
        
        # Step 4: Finally drop the column
        print("\n4️⃣ Dropping id_niveau column...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" DROP COLUMN IF EXISTS "id_niveau";
            """)
            print("   ✅ Column dropped successfully")
        except Exception as e:
            print(f"   ❌ Error dropping column: {e}")
        
        # Step 5: Ensure id_specialite is NOT NULL
        print("\n5️⃣ Ensuring id_specialite is required...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" ALTER COLUMN "id_specialite" SET NOT NULL;
            """)
            print("   ✅ id_specialite is now required")
        except Exception as e:
            print(f"   ⚠️ Column might already be NOT NULL: {e}")
        
        # Step 6: Verify the table structure
        print("\n6️⃣ Verifying table structure...")
        columns = await prisma.query_raw("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'Subject' 
            ORDER BY ordinal_position;
        """)
        
        print("   Current Subject table columns:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   • {col['column_name']} ({col['data_type']}) {nullable}")
        
        # Step 7: Test creating a subject
        print("\n7️⃣ Testing subject creation...")
        
        # Get a speciality to test with
        speciality = await prisma.specialite.find_first()
        if not speciality:
            print("   ❌ No speciality found for testing")
            return
        
        # Get a teacher to test with
        teacher = await prisma.enseignant.find_first()
        if not teacher:
            print("   ❌ No teacher found for testing")
            return
        
        # Try to create a test subject
        try:
            test_subject = await prisma.matiere.create(
                data={
                    "nom": "Test Subject - Migration",
                    "id_specialite": speciality.id,
                    "id_enseignant": teacher.id
                }
            )
            print(f"   ✅ Successfully created test subject: {test_subject.nom}")
            
            # Clean up test subject
            await prisma.matiere.delete(where={"id": test_subject.id})
            print("   ✅ Test subject cleaned up")
            
        except Exception as e:
            print(f"   ❌ Error creating test subject: {e}")
            return
        
        print("\n✅ Migration completed successfully!")
        print("   You can now create subjects with the new schema.")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(complete_migration())