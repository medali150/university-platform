#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import verify_password, hash_password
from prisma import Prisma

async def debug_login():
    print("=== LOGIN DEBUG TOOL ===")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Check if user exists
        login_to_check = "boubaked"
        password_to_check = "faddou"
        
        print(f"\n🔍 Searching for user with login: '{login_to_check}'")
        
        user = await prisma.user.find_unique(where={"login": login_to_check})
        
        if not user:
            print(f"❌ User '{login_to_check}' NOT FOUND in database")
            print("\n📋 Available users:")
            users = await prisma.user.find_many()
            for u in users:
                print(f"  - Login: {u.login} | Email: {u.email} | Role: {u.role}")
        else:
            print(f"✅ User found!")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.firstName} {user.lastName}")
            print(f"   Email: {user.email}")
            print(f"   Login: {user.login}")
            print(f"   Role: {user.role}")
            
            # Test password verification
            print(f"\n🔐 Testing password verification...")
            print(f"   Password to test: '{password_to_check}'")
            
            if user.passwordHash:
                password_match = verify_password(password_to_check, user.passwordHash)
                print(f"   Password Hash: {user.passwordHash[:50]}...")
                print(f"   Password matches: {'✅ YES' if password_match else '❌ NO'}")
                
                # Test with some common passwords
                test_passwords = ["admin", "password", "123456", "boubaked", "faddou", "admin123"]
                print(f"\n🧪 Testing common passwords:")
                for pwd in test_passwords:
                    match = verify_password(pwd, user.passwordHash)
                    if match:
                        print(f"   '{pwd}': ✅ MATCH!")
                    else:
                        print(f"   '{pwd}': ❌ no match")
            else:
                print("   ❌ NO PASSWORD HASH found for user!")
        
        # Show all users with their info
        print(f"\n📊 All users summary:")
        all_users = await prisma.user.find_many()
        for u in all_users:
            has_password = "✅" if u.passwordHash else "❌"
            print(f"   {u.login} ({u.role}) - Password: {has_password}")
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_login())