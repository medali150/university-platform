#!/usr/bin/env python3
"""
Quick test to verify correct Prisma model name for DepartmentHead
"""

import asyncio
from prisma import Prisma

async def test_model_names():
    """Test different possible model names for DepartmentHead"""
    prisma = Prisma()
    await prisma.connect()
    
    # Test possible model names
    possible_names = [
        "department_head",
        "departmenthead", 
        "departmentHead",
        "DepartmentHead"
    ]
    
    for name in possible_names:
        try:
            model = getattr(prisma, name, None)
            if model:
                print(f"✅ Found model: prisma.{name}")
                # Try to call count to verify it works
                count = await model.count()
                print(f"   Count: {count}")
            else:
                print(f"❌ Model not found: prisma.{name}")
        except AttributeError:
            print(f"❌ Attribute error for: prisma.{name}")
        except Exception as e:
            print(f"❌ Error for prisma.{name}: {e}")
    
    # Also print all available attributes
    print("\n📋 All prisma attributes:")
    attrs = [attr for attr in dir(prisma) if not attr.startswith('_')]
    for attr in sorted(attrs):
        if hasattr(getattr(prisma, attr), 'find_many'):
            print(f"   prisma.{attr} (model)")
        else:
            print(f"   prisma.{attr}")
    
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_model_names())