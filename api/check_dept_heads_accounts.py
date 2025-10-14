#!/usr/bin/env python3

import asyncio
from prisma import Prisma

async def check_department_heads():
    """Check available department head accounts"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Checking available department head accounts...")
        
        # Get all users with DEPARTMENT_HEAD role
        dept_head_users = await prisma.utilisateur.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "chefDepartement": {
                    "include": {
                        "departement": True
                    }
                }
            }
        )
        
        print(f"\n📊 Found {len(dept_head_users)} department head users:")
        
        for user in dept_head_users:
            print(f"\n👤 User: {user.prenom} {user.nom}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            
            if user.chefDepartement:
                dept = user.chefDepartement.departement
                print(f"   Department: {dept.nom}")
                
                # Check subjects in this department
                subjects_count = await prisma.matiere.count(
                    where={
                        "specialite": {
                            "id_departement": dept.id
                        }
                    }
                )
                print(f"   Subjects in department: {subjects_count}")
            else:
                print("   ⚠️ No department head record found!")
        
        # Also check plain admin users that could be used for testing
        print("\n\n🔍 Checking admin users for reference...")
        admin_users = await prisma.utilisateur.find_many(
            where={"role": "ADMIN"},
            take=2
        )
        
        for user in admin_users:
            print(f"👑 Admin: {user.prenom} {user.nom} ({user.email})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_department_heads())