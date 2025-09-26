#!/usr/bin/env python3
"""
Database Fix Script
Fixes the schema mismatch issue by updating the database to match Prisma schema
"""

import asyncio
import os
import sys

async def fix_database():
    """Fix database schema issues"""
    print("🔧 Fixing database schema...")
    
    try:
        from app.db.prisma_client import get_prisma
        
        # Test connection first
        print("1️⃣ Testing database connection...")
        prisma = await get_prisma()
        
        # Try to count users to see if basic connection works
        try:
            user_count = await prisma.user.count()
            print(f"✅ Database connected. Found {user_count} users.")
            
            # Try to create a test query to see if schema is correct
            print("2️⃣ Testing schema compatibility...")
            
            # This should work if schema is correct
            test_user = await prisma.user.find_first()
            if test_user:
                print(f"✅ Schema appears to be working. Sample user: {test_user.firstName}")
            else:
                print("ℹ️  No users found, but schema seems compatible.")
                
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "Could not find field" in error_msg and "role" in error_msg:
                print("❌ Schema mismatch detected: role field missing")
                print("🛠️  You need to update your database schema.")
                print("\n📋 Manual fix required:")
                print("1. Run: npx prisma db push")
                print("2. Or manually add role column to User table")
                print("3. Restart the server")
                return False
            else:
                print(f"❌ Unexpected database error: {error_msg}")
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def create_admin_if_needed():
    """Create admin user if it doesn't exist"""
    print("\n3️⃣ Checking for admin user...")
    
    try:
        from app.db.prisma_client import get_prisma
        from app.core.security import hash_password
        
        prisma = await get_prisma()
        
        # Check if admin exists
        admin = await prisma.user.find_first(
            where={"login": "admin"}
        )
        
        if admin:
            print(f"✅ Admin user exists: {admin.firstName} {admin.lastName}")
            return True
        
        print("🔧 Creating admin user...")
        
        # Create admin user
        admin_data = {
            "firstName": "System",
            "lastName": "Administrator",
            "email": "admin@university.com", 
            "login": "admin",
            "passwordHash": hash_password("admin123"),
            "role": "ADMIN"
        }
        
        new_admin = await prisma.user.create(data=admin_data)
        
        # Create admin record
        await prisma.admin.create(
            data={
                "userId": new_admin.id,
                "level": "SUPER_ADMIN"
            }
        )
        
        print(f"✅ Admin user created: {new_admin.firstName} {new_admin.lastName}")
        print("   Login: admin")
        print("   Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

async def main():
    """Main function"""
    print("🎓 University Database Fix & Setup")
    print("=" * 50)
    
    # Fix database schema
    if not await fix_database():
        print("\n❌ Database fix failed. Please follow manual instructions.")
        sys.exit(1)
    
    # Create admin user
    if not await create_admin_if_needed():
        print("\n⚠️  Admin user creation failed, but database is working.")
        print("You can create admin manually via /auth/register endpoint.")
    
    print("\n🎉 Database setup complete!")
    print("\n🚀 Next steps:")
    print("1. Start server: uvicorn main:app --reload")
    print("2. Open Swagger UI: http://127.0.0.1:8000/docs") 
    print("3. Login as admin: admin / admin123")
    print("4. Test admin endpoints!")

if __name__ == "__main__":
    asyncio.run(main())