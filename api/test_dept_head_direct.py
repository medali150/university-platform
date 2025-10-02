#!/usr/bin/env python3
"""
Direct test of department head registration logic
"""

import asyncio
import sys
import os
from typing import Optional

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_dept_head_registration_direct():
    """Test department head registration logic directly"""
    print("🧪 Testing Department Head Registration Logic Directly...")
    
    try:
        # Import required modules
        from prisma import Prisma
        from app.core.security import hash_password
        from pydantic import BaseModel
        
        # Define user data structure
        class UserCreate(BaseModel):
            nom: str
            prenom: str
            email: str
            password: str
            role: str
        
        # Create test data
        user_data = UserCreate(
            nom="TestDeptHead",
            prenom="Jean",
            email="testdepthead@university.com",
            password="test123456",
            role="DEPARTMENT_HEAD"
        )
        
        # Simulated department_id from frontend
        department_id = "cmg6pgscg0000bm1oh0w4v8js"  # Using the "Informatique" department
        
        print(f"📋 Test data:")
        print(f"  - Name: {user_data.prenom} {user_data.nom}")
        print(f"  - Email: {user_data.email}")
        print(f"  - Role: {user_data.role}")
        print(f"  - Department ID: {department_id}")
        
        # Connect to database
        prisma = Prisma()
        await prisma.connect()
        print("✅ Database connected")
        
        # Test the registration logic step by step
        print("\n🔍 Step 1: Check if user exists...")
        existing = await prisma.utilisateur.find_unique(where={"email": user_data.email})
        if existing:
            print("⚠️  User already exists, deleting for test...")
            await prisma.utilisateur.delete(where={"id": existing.id})
        print("✅ User check passed")
        
        print("\n🔍 Step 2: Hash password...")
        hashed_password = hash_password(user_data.password)
        print("✅ Password hashed")
        
        print("\n🔍 Step 3: Get default data...")
        default_department = await prisma.departement.find_first()
        print(f"✅ Default department: {default_department.nom}")
        
        print("\n🔍 Step 4: Department head specific logic...")
        selected_department_id = department_id or default_department.id
        print(f"Selected department ID: {selected_department_id}")
        
        # Verify department exists
        selected_department = await prisma.departement.find_unique(
            where={"id": selected_department_id}
        )
        if not selected_department:
            print("❌ Selected department not found!")
            return
        print(f"✅ Department found: {selected_department.nom}")
        
        # Check for existing head
        existing_head = await prisma.chefdepartement.find_first(
            where={"id_departement": selected_department_id}
        )
        if existing_head:
            print(f"⚠️  Department already has a head (ID: {existing_head.id})")
            print("   Deleting for test...")
            await prisma.chefdepartement.delete(where={"id": existing_head.id})
        print("✅ Department head check passed")
        
        print("\n🔍 Step 5: Create user...")
        new_user = await prisma.utilisateur.create(
            data={
                "prenom": user_data.prenom,
                "nom": user_data.nom,
                "email": user_data.email,
                "mdp_hash": hashed_password,
                "role": user_data.role
            }
        )
        print(f"✅ User created: {new_user.id}")
        
        print("\n🔍 Step 6: Create department head record...")
        dept_head = await prisma.chefdepartement.create(
            data={
                "id_utilisateur": new_user.id,
                "id_departement": selected_department_id
            }
        )
        print(f"✅ Department head created: {dept_head.id}")
        
        print("\n🎉 Registration completed successfully!")
        print(f"   User: {new_user.prenom} {new_user.nom}")
        print(f"   Role: {new_user.role}")
        print(f"   Department: {selected_department.nom}")
        
        # Cleanup
        await prisma.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dept_head_registration_direct())