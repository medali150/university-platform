#!/usr/bin/env python3

import asyncio
from app.db.prisma_client import DatabaseManager
from app.core.security import hash_password

async def create_user():
    print("=== CREATE USER TOOL ===")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # User details
        login = "boubaked"
        password = "faddou"
        first_name = "Boubaked"
        last_name = "Faddou"
        email = "boubaked@gmail.com"  # Fixed the email typo from your form
        role = "STUDENT"  # As shown in the dropdown
        
        print(f"📝 Creating user:")
        print(f"   Login: {login}")
        print(f"   Password: {password}")
        print(f"   Name: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        
        # Check if user already exists
        existing = await prisma.user.find_first(
            where={
                "OR": [
                    {"email": email},
                    {"login": login}
                ]
            }
        )
        
        if existing:
            print(f"❌ User already exists with login '{existing.login}' or email '{existing.email}'")
            return
        
        # Hash password
        hashed_password = hash_password(password)
        print(f"🔐 Password hashed: {hashed_password[:50]}...")
        
        # Create user
        new_user = await prisma.user.create(
            data={
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "login": login,
                "passwordHash": hashed_password,
                "role": role
            }
        )
        
        print(f"✅ User created successfully!")
        print(f"   ID: {new_user.id}")
        print(f"   Full details: {new_user}")
        
        # Test login immediately
        print(f"\n🧪 Testing login...")
        from app.core.security import verify_password
        
        login_test = await prisma.user.find_unique(where={"login": login})
        if login_test and verify_password(password, login_test.passwordHash):
            print(f"✅ Login test successful!")
        else:
            print(f"❌ Login test failed!")
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_user())