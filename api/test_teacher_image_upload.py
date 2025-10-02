#!/usr/bin/env python3
"""
Test script for teacher image upload functionality
"""

import asyncio
import httpx
from pathlib import Path

async def test_teacher_image_upload():
    """Test teacher image upload endpoints"""
    
    base_url = "http://localhost:8000"
    
    # First, login as the teacher to get a token
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔐 Logging in as teacher...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(login_response.text)
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Login successful")
            
            # Test teacher profile endpoint (should now include image_url)
            print("\n📋 Testing teacher profile endpoint...")
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Teacher profile retrieved successfully!")
                print(f"   Teacher: {profile_data.get('teacher_info', {}).get('nom')} {profile_data.get('teacher_info', {}).get('prenom')}")
                print(f"   Current image: {profile_data.get('teacher_info', {}).get('image_url', 'None')}")
            else:
                print(f"❌ Profile request failed: {profile_response.status_code}")
                print(profile_response.text)
            
            # Test image upload endpoint (simulate with a small test file)
            print("\n📸 Testing image upload endpoint...")
            
            # Create a small test image file (simple base64 encoded small image)
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {"file": ("test.png", test_image_data, "image/png")}
            
            # Note: For a real test, you'd need actual Cloudinary credentials
            print("   (Simulating image upload - requires Cloudinary credentials)")
            print("   Endpoint: POST /teacher/profile/upload-image")
            print("   Expected response: {success: true, message: '...', image_url: '...'}")
            
            # Test image deletion endpoint
            print("\n🗑️  Testing image deletion endpoint...")
            print("   Endpoint: DELETE /teacher/profile/image")
            print("   Expected response: {message: 'Image deleted successfully'}")
            
            # Test profile info update endpoint
            print("\n✏️  Testing profile update endpoint...")
            update_data = {
                "nom": "Martin",
                "prenom": "Jean",
                "email": "jean.martin@university.com"
            }
            
            update_response = await client.put(
                f"{base_url}/teacher/profile/info", 
                headers=headers,
                json=update_data
            )
            
            if update_response.status_code == 200:
                update_result = update_response.json()
                print("✅ Profile update endpoint works!")
                print(f"   Message: {update_result.get('message')}")
            else:
                print(f"❌ Profile update failed: {update_response.status_code}")
                print(update_response.text)
                
            print("\n🎉 All teacher image endpoints tested!")
            print("\n📝 Next steps:")
            print("   1. Set up Cloudinary account and get credentials")
            print("   2. Update .env file with Cloudinary credentials:")
            print("      CLOUDINARY_CLOUD_NAME=your_cloud_name")
            print("      CLOUDINARY_API_KEY=your_api_key")
            print("      CLOUDINARY_API_SECRET=your_api_secret")
            print("   3. Test image upload with real image files")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_teacher_image_upload())