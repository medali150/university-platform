#!/usr/bin/env python3
"""
Direct test of Prisma client model access
"""

import asyncio
import sys
from prisma import Prisma

async def test_department_head_access():
    """Test different ways to access DepartmentHead model"""
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("✅ Connected to database")
        
        # Test different possible attribute names
        possible_names = [
            'departmentHead',
            'department_head', 
            'departmenthead',
            'DepartmentHead'
        ]
        
        for name in possible_names:
            try:
                model = getattr(prisma, name, None)
                if model and hasattr(model, 'count'):
                    count = await model.count()
                    print(f"✅ SUCCESS: prisma.{name} works! Count: {count}")
                    return name
                else:
                    print(f"❌ No model found for: prisma.{name}")
            except Exception as e:
                print(f"❌ Error with prisma.{name}: {e}")
        
        # If none work, let's see what attributes are available
        print("\n🔍 Available Prisma client attributes:")
        attrs = [attr for attr in dir(prisma) if not attr.startswith('_') and not callable(getattr(prisma, attr))]
        for attr in sorted(attrs):
            obj = getattr(prisma, attr)
            if hasattr(obj, 'find_many'):
                print(f"   prisma.{attr} ✓ (has model methods)")
            else:
                print(f"   prisma.{attr}")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await prisma.disconnect()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_department_head_access())