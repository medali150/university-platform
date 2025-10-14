#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import verify_password, hash_password

async def debug_login():
    print("=== LOGIN DEBUG TOOL - UNIVERSITY VERSION ===")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Check if admin user exists
        email_to_check = "admin@university.com"
        password_to_check = "admin123"
        
        print(f"\n🔍 Searching for admin user with email: '{email_to_check}'")
        
        user = await prisma.utilisateur.find_unique(where={"email": email_to_check})
        
        if not user:
            print(f"❌ User '{email_to_check}' NOT FOUND in database")
            print("\n📋 Available users:")
            users = await prisma.utilisateur.find_many()
            for u in users:
                print(f"  - Email: {u.email} | Name: {u.prenom} {u.nom} | Role: {u.role}")
        else:
            print(f"✅ User found!")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.prenom} {user.nom}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            
            # Test password verification
            print(f"\n🔐 Testing password verification...")
            print(f"   Password to test: '{password_to_check}'")
            
            if user.mdp_hash:
                password_match = verify_password(password_to_check, user.mdp_hash)
                print(f"   Password Hash: {user.mdp_hash[:50]}...")
                print(f"   Password matches: {'✅ YES' if password_match else '❌ NO'}")
                
                # Test with some common passwords
                test_passwords = ["admin", "password", "123456", "admin123", "university"]
                print(f"\n🧪 Testing common passwords:")
                for pwd in test_passwords:
                    match = verify_password(pwd, user.mdp_hash)
                    if match:
                        print(f"   '{pwd}': ✅ MATCH!")
                    else:
                        print(f"   '{pwd}': ❌ no match")
            else:
                print("   ❌ NO PASSWORD HASH found for user!")
        
        # Show all users with their info
        print(f"\n📊 All users summary:")
        all_users = await prisma.utilisateur.find_many()
        for u in all_users:
            has_password = "✅" if u.mdp_hash else "❌"
            print(f"   {u.email} ({u.role}) - Password: {has_password}")
            
        # Try direct token creation
        if user:
            print(f"\n🎫 Testing token creation...")
            try:
                from app.core.jwt import create_access_token
                token = create_access_token(data={"sub": user.id})
                print(f"   ✅ Token created: {token[:50]}...")
            except Exception as e:
                print(f"   ❌ Token creation failed: {str(e)}")
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_login())