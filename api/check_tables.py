"""
Check what tables exist in the database
"""
import asyncio
import os
from prisma import Prisma

os.environ['DATABASE_URL'] = "postgresql://postgres:dali2004@localhost:5432/universety_db"

async def check_tables():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Try to query different tables
        print("Checking tables...")
        
        # Try User table
        try:
            users = await prisma.query_raw('SELECT COUNT(*) FROM "User"')
            print(f"✅ User table exists: {users}")
        except Exception as e:
            print(f"❌ User table: {e}")
        
        # Try Utilisateur table
        try:
            users = await prisma.query_raw('SELECT COUNT(*) FROM "Utilisateur"')
            print(f"✅ Utilisateur table exists: {users}")
        except Exception as e:
            print(f"❌ Utilisateur table: {e}")
            
        # Try Teacher table
        try:
            teachers = await prisma.query_raw('SELECT COUNT(*) FROM "Teacher"')
            print(f"✅ Teacher table exists: {teachers}")
        except Exception as e:
            print(f"❌ Teacher table: {e}")
            
        # Try Enseignant table
        try:
            teachers = await prisma.query_raw('SELECT COUNT(*) FROM "Enseignant"')
            print(f"✅ Enseignant table exists: {teachers}")
        except Exception as e:
            print(f"❌ Enseignant table: {e}")
            
        # List all tables
        print("\n📋 All tables in database:")
        tables = await prisma.query_raw("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        for table in tables:
            print(f"  - {table}")
            
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_tables())
