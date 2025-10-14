"""
Test Prisma import and create basic university data
"""
import sys
import os

print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTrying to import Prisma...")

try:
    from prisma import Prisma
    print("✅ Prisma imported successfully!")
    
    async def test_connection():
        db = Prisma()
        await db.connect()
        print("✅ Database connected successfully!")
        
        # Test creating a department
        dept = await db.departement.create(data={
            "nom": "Test Department"
        })
        print(f"✅ Created test department: {dept.nom}")
        
        # Clean up
        await db.departement.delete(where={"id": dept.id})
        print("✅ Test department deleted")
        
        await db.disconnect()
        print("✅ Database disconnected")
    
    import asyncio
    asyncio.run(test_connection())
    
except ImportError as e:
    print(f"❌ Could not import Prisma: {e}")
    
    # Try to find where prisma is installed
    try:
        import prisma as prisma_module
        print(f"Prisma module location: {prisma_module.__file__}")
        print(f"Prisma module contents: {dir(prisma_module)}")
    except Exception as e2:
        print(f"Could not even import prisma module: {e2}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()