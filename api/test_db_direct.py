#!/usr/bin/env python3
"""
Simple database connection and table test
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_database():
    """Test database connection and basic queries"""
    print("🔍 Testing database connection...")
    
    try:
        # Import after adding to path
        from prisma import Prisma
        
        # Create prisma client
        prisma = Prisma()
        
        # Connect to database
        print("🔌 Connecting to database...")
        await prisma.connect()
        print("✅ Database connected!")
        
        # Test basic queries
        print("\n🧪 Testing basic queries...")
        
        # Test departments table
        try:
            dept_count = await prisma.departement.count()
            print(f"📊 Departments count: {dept_count}")
            
            if dept_count == 0:
                print("➕ Creating test department...")
                test_dept = await prisma.departement.create(
                    data={"nom": "Informatique"}
                )
                print(f"✅ Created department: {test_dept.nom} (ID: {test_dept.id})")
            else:
                # Get first few departments
                departments = await prisma.departement.find_many(take=3)
                print("📋 Existing departments:")
                for dept in departments:
                    print(f"  - {dept.nom} (ID: {dept.id})")
        except Exception as e:
            print(f"❌ Error with departments table: {e}")
        
        # Test users table
        try:
            user_count = await prisma.utilisateur.count()
            print(f"👥 Users count: {user_count}")
        except Exception as e:
            print(f"❌ Error with users table: {e}")
        
        # Test department heads table
        try:
            head_count = await prisma.chefdepartement.count()
            print(f"👔 Department heads count: {head_count}")
        except Exception as e:
            print(f"❌ Error with department heads table: {e}")
        
        # Disconnect
        await prisma.disconnect()
        print("\n✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())