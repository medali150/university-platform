#!/usr/bin/env python3
"""
Debug script for 500 Internal Server Error in image upload
"""

import asyncio
from prisma import Prisma
from app.services.cloudinary_service import CloudinaryService
from app.core.jwt import decode_token
import os
import sys

async def debug_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        prisma = Prisma()
        await prisma.connect()
        
        # Test basic query
        users = await prisma.utilisateur.find_many(take=1)
        print(f"✅ Database connected. Found {len(users)} users in test query")
        
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def debug_cloudinary_service():
    """Test Cloudinary service"""
    print("🔍 Testing Cloudinary service...")
    
    try:
        # Create a simple test image (1x1 pixel red image)
        import io
        from PIL import Image
        
        # Create minimal test image
        img = Image.new('RGB', (1, 1), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Test upload
        result = await CloudinaryService.upload_image(
            file_content=img_bytes.getvalue(),
            public_id="test_debug_image"
        )
        
        print(f"Cloudinary test result: {result}")
        
        if result.get("success"):
            print("✅ Cloudinary service working")
            
            # Test cleanup
            cleanup_result = await CloudinaryService.delete_image("test_debug_image")
            print(f"Cleanup result: {cleanup_result}")
            
            return True
        else:
            print(f"❌ Cloudinary upload failed: {result.get('error')}")
            return False
            
    except ImportError:
        print("⚠️ PIL not available, skipping Cloudinary test")
        return None
    except Exception as e:
        print(f"❌ Cloudinary test failed: {e}")
        return False

async def debug_teacher_lookup():
    """Test teacher lookup logic"""
    print("🔍 Testing teacher lookup...")
    
    try:
        prisma = Prisma()
        await prisma.connect()
        
        # Find teacher users
        teacher_users = await prisma.utilisateur.find_many(
            where={"role": "TEACHER"}
        )
        
        print(f"Found {len(teacher_users)} teacher users")
        
        for user in teacher_users[:3]:  # Check first 3
            print(f"User: {user.email}, enseignant_id: {user.enseignant_id}")
            
            if user.enseignant_id:
                teacher = await prisma.enseignant.find_unique(
                    where={"id": user.enseignant_id}
                )
                if teacher:
                    print(f"  ✅ Teacher record found: {teacher.nom} {teacher.prenom}")
                else:
                    print(f"  ❌ Teacher record NOT found for enseignant_id: {user.enseignant_id}")
            else:
                print(f"  ⚠️ No enseignant_id for user: {user.email}")
        
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Teacher lookup failed: {e}")
        return False

def debug_environment():
    """Check environment variables"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET',
        'DATABASE_URL',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(10, len(value))}...")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def debug_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        from fastapi import FastAPI, UploadFile, File
        print("✅ FastAPI imports working")
        
        from prisma import Prisma
        print("✅ Prisma import working")
        
        from app.services.cloudinary_service import CloudinaryService
        print("✅ CloudinaryService import working")
        
        from app.core.deps import get_current_user, require_teacher
        print("✅ Auth dependencies import working")
        
        from app.schemas.teacher import TeacherImageUpload
        print("✅ Teacher schemas import working")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def debug_jwt_token():
    """Test JWT token handling"""
    print("🔍 Testing JWT token functionality...")
    
    try:
        from app.core.jwt import create_access_token, decode_token
        
        # Create test token
        test_payload = {"sub": "test_user", "type": "access"}
        token = create_access_token(test_payload)
        print(f"✅ Token created: {token[:20]}...")
        
        # Decode token
        decoded = decode_token(token)
        print(f"✅ Token decoded: {decoded}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False

async def main():
    """Run all debug tests"""
    print("🚀 Starting comprehensive debug for 500 error...")
    print("=" * 60)
    
    # Test 1: Environment
    env_ok = debug_environment()
    print()
    
    # Test 2: Imports
    imports_ok = debug_imports()
    print()
    
    # Test 3: JWT
    jwt_ok = await debug_jwt_token()
    print()
    
    # Test 4: Database
    db_ok = await debug_database_connection()
    print()
    
    # Test 5: Teacher lookup
    teacher_ok = await debug_teacher_lookup()
    print()
    
    # Test 6: Cloudinary
    cloudinary_ok = await debug_cloudinary_service()
    print()
    
    # Summary
    print("=" * 60)
    print("🏁 DEBUG SUMMARY:")
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"JWT: {'✅' if jwt_ok else '❌'}")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"Teacher lookup: {'✅' if teacher_ok else '❌'}")
    print(f"Cloudinary: {'✅' if cloudinary_ok else '❌' if cloudinary_ok is not None else '⚠️'}")
    
    if all([env_ok, imports_ok, jwt_ok, db_ok, teacher_ok]):
        print("\n✅ All core components working. 500 error might be in request handling.")
    else:
        print("\n❌ Found issues that could cause 500 error.")

if __name__ == "__main__":
    asyncio.run(main())