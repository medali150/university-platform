#!/usr/bin/env python3
"""
Fix password for existing department head user
"""
import asyncio
import bcrypt
from prisma import Prisma

async def fix_user_password():
    """Fix the password for the existing user"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== FIXING USER PASSWORD ===\n")
        
        # Find the user
        user = await prisma.user.find_unique(
            where={"email": "hathemhafsi@gmail.com"},
            include={
                "departmentHead": {"include": {"department": True}}
            }
        )
        
        if not user:
            print("❌ User not found!")
            return False
        
        print(f"👤 Found user: {user.firstName} {user.lastName}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Login: {user.login}")
        
        # Hash the new password
        new_password = "dslighgh15"
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update the password
        await prisma.user.update(
            where={"id": user.id},
            data={"passwordHash": password_hash}
        )
        
        print(f"✅ Password updated successfully!")
        print(f"🔒 New password: {new_password}")
        
        if user.departmentHead:
            print(f"🏢 Department: {user.departmentHead.department.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await prisma.disconnect()

async def main():
    success = await fix_user_password()
    
    if success:
        print(f"\n🎯 READY TO USE IN SWAGGER:")
        print(f'{{')
        print(f'  "login": "hathemhafsi@gmail.com",')
        print(f'  "password": "dslighgh15"')
        print(f'}}')

if __name__ == "__main__":
    asyncio.run(main())