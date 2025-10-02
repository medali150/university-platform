#!/usr/bin/env python3
"""
Migration script to remove login field and use email for authentication
This script will:
1. Generate the database migration
2. Update existing test data to ensure emails are set properly
3. Apply the migration
"""

import asyncio
import subprocess
import sys
from pathlib import Path

async def run_migration():
    """Run the database migration to remove login field"""
    print("=== RUNNING DATABASE MIGRATION ===")
    
    try:
        # Generate migration
        print("📝 Generating migration...")
        result = subprocess.run([
            "prisma", "migrate", "dev", "--name", "remove_login_field"
        ], cwd=".", capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Migration failed: {result.stderr}")
            return False
        
        print("✅ Migration generated successfully")
        
        # Generate Prisma client
        print("🔄 Generating Prisma client...")
        result = subprocess.run([
            "prisma", "generate"
        ], cwd=".", capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Client generation failed: {result.stderr}")
            return False
            
        print("✅ Prisma client generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

async def update_test_data():
    """Update existing test data with proper email addresses"""
    print("=== UPDATING TEST DATA ===")
    
    try:
        # Import after migration
        from app.db.prisma_client import DatabaseManager
        from app.core.security import hash_password
        
        db_manager = DatabaseManager()
        await db_manager.connect()
        prisma = db_manager.prisma
        
        # Define test users with emails
        test_users = [
            {
                "email": "john.doe@university.com",
                "firstName": "John",
                "lastName": "Doe",
                "password": "depthead123",
                "role": "DEPARTMENT_HEAD"
            },
            {
                "email": "teacher@university.com",
                "firstName": "Sample",
                "lastName": "Teacher", 
                "password": "teacher123",
                "role": "TEACHER"
            },
            {
                "email": "student@university.edu",
                "firstName": "Sample",
                "lastName": "Student",
                "password": "student123",
                "role": "STUDENT"
            }
        ]
        
        for user_data in test_users:
            print(f"🔄 Setting up user: {user_data['email']}")
            
            # Check if user already exists
            existing = await prisma.user.find_unique(where={"email": user_data["email"]})
            
            if existing:
                print(f"   ✅ User already exists: {user_data['email']}")
            else:
                # Create new user
                hashed_password = hash_password(user_data["password"])
                new_user = await prisma.user.create(data={
                    "firstName": user_data["firstName"],
                    "lastName": user_data["lastName"],
                    "email": user_data["email"],
                    "passwordHash": hashed_password,
                    "role": user_data["role"]
                })
                print(f"   ✅ Created user: {new_user.email}")
        
        await db_manager.disconnect()
        print("✅ Test data updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating test data: {e}")
        return False

async def main():
    """Main migration process"""
    print("🚀 Starting migration from login to email authentication\n")
    
    # Step 1: Run database migration
    if not await run_migration():
        print("❌ Migration failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Update test data
    if not await update_test_data():
        print("❌ Test data update failed. Migration completed but test data may need manual update.")
        sys.exit(1)
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Updated Test Credentials:")
    print("   Department Head: john.doe@university.com / depthead123")
    print("   Teacher: teacher@university.com / teacher123")
    print("   Student: student@university.edu / student123")
    print("\n✅ You can now use email addresses for authentication!")

if __name__ == "__main__":
    asyncio.run(main())