#!/usr/bin/env python3
"""
Manual database update to migrate matiere relationships
"""
import asyncio
from prisma import Prisma

async def manual_database_update():
    """Manually update the database structure"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔧 Performing manual database updates...")
        
        # Step 1: Get the mapping from niveau to specialite
        print("\n1️⃣ Getting niveau to specialite mapping...")
        niveau_mapping = await prisma.query_raw("""
            SELECT n.id as niveau_id, n.id_specialite as specialite_id, s.nom as specialite_nom
            FROM "Level" n
            JOIN "Specialty" s ON n.id_specialite = s.id
        """)
        
        print("   Mapping found:")
        for mapping in niveau_mapping:
            print(f"   • Niveau {mapping['niveau_id']} -> Spécialité {mapping['specialite_nom']}")
        
        # Step 2: Add id_specialite column if it doesn't exist
        print("\n2️⃣ Adding id_specialite column...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" ADD COLUMN IF NOT EXISTS "id_specialite" TEXT;
            """)
            print("   ✅ Column added successfully")
        except Exception as e:
            print(f"   ⚠️ Column might already exist: {e}")
        
        # Step 3: Update each matiere with the correct specialite_id
        print("\n3️⃣ Updating matiere records...")
        for mapping in niveau_mapping:
            niveau_id = mapping['niveau_id']
            specialite_id = mapping['specialite_id']
            
            result = await prisma.execute_raw("""
                UPDATE "Subject" 
                SET "id_specialite" = $1 
                WHERE "id_niveau" = $2
            """, specialite_id, niveau_id)
            
            print(f"   ✅ Updated matieres from niveau {niveau_id[:8]}...")
        
        # Step 4: Verify the updates
        print("\n4️⃣ Verifying updates...")
        updated_count = await prisma.query_raw("""
            SELECT COUNT(*) as count 
            FROM "Subject" 
            WHERE "id_specialite" IS NOT NULL
        """)
        
        print(f"   ✅ {updated_count[0]['count']} matiere records now have specialite relationships")
        
        # Step 5: Create index for performance
        print("\n5️⃣ Creating index...")
        try:
            await prisma.execute_raw("""
                CREATE INDEX IF NOT EXISTS "Subject_id_specialite_idx" ON "Subject"("id_specialite");
            """)
            print("   ✅ Index created successfully")
        except Exception as e:
            print(f"   ⚠️ Index might already exist: {e}")
        
        # Step 6: Add foreign key constraint
        print("\n6️⃣ Adding foreign key constraint...")
        try:
            await prisma.execute_raw("""
                ALTER TABLE "Subject" 
                ADD CONSTRAINT "Subject_id_specialite_fkey" 
                FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;
            """)
            print("   ✅ Foreign key constraint added successfully")
        except Exception as e:
            print(f"   ⚠️ Constraint might already exist: {e}")
        
        print("\n✅ Manual database update completed successfully!")
        
        # Verification query
        print("\n🔍 Final verification:")
        verification = await prisma.query_raw("""
            SELECT m.nom as matiere_nom, s.nom as specialite_nom, d.nom as departement_nom
            FROM "Subject" m
            JOIN "Specialty" s ON m.id_specialite = s.id
            JOIN "Department" d ON s.id_departement = d.id
            ORDER BY d.nom, s.nom, m.nom
        """)
        
        current_dept = None
        current_spec = None
        for row in verification:
            if row['departement_nom'] != current_dept:
                current_dept = row['departement_nom']
                print(f"\n🏫 {current_dept}:")
            if row['specialite_nom'] != current_spec:
                current_spec = row['specialite_nom']
                print(f"   📚 {current_spec}:")
            print(f"      • {row['matiere_nom']}")
            
    except Exception as e:
        print(f"❌ Error during manual update: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(manual_database_update())