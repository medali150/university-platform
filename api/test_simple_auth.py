#!/usr/bin/env python3
"""
Simple authentication test for image upload
"""

import asyncio
import httpx

async def test_simple_auth():
    """Test simple authentication"""
    
    base_url = "http://localhost:8000"
    
    # Login data
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Login first
            print("🔐 Logging in...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            print(f"✅ Login successful")
            
            # Test simple profile endpoint first
            print("\n📋 Testing profile endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            
            print(f"Profile status: {profile_response.status_code}")
            if profile_response.status_code == 401:
                print("❌ Profile endpoint returns 401 - authentication issue!")
                print(f"Response: {profile_response.text}")
            elif profile_response.status_code == 200:
                print("✅ Profile endpoint works - authentication OK")
                profile_data = profile_response.json()
                teacher_name = f"{profile_data['teacher_info']['prenom']} {profile_data['teacher_info']['nom']}"
                print(f"Teacher: {teacher_name}")
                
                # Now test image upload endpoint with a simple POST (no file)
                print("\n📸 Testing image upload endpoint structure...")
                upload_response = await client.post(
                    f"{base_url}/teacher/profile/upload-image",
                    headers=headers
                )
                
                print(f"Upload status: {upload_response.status_code}")
                if upload_response.status_code == 401:
                    print("❌ Image upload returns 401 - authentication issue!")
                elif upload_response.status_code == 422:
                    print("✅ Image upload authentication works (422 = missing file, but auth passed)")
                else:
                    print(f"Response: {upload_response.text}")
            
        except httpx.ConnectError:
            print("❌ Connection error - is the server running on port 8000?")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_auth())