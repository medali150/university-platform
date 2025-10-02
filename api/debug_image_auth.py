#!/usr/bin/env python3
"""
Debug script for teacher image upload authentication
"""

import asyncio
import httpx
import base64
from io import BytesIO
from PIL import Image

async def debug_image_upload():
    """Debug image upload authentication"""
    
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
                print(f"Response: {login_response.text}")
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            print(f"✅ Login successful")
            print(f"Token: {token[:50]}...")
            
            # Test authentication with a simple profile request first
            print("\n🔍 Testing profile endpoint with token...")
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            
            if profile_response.status_code == 200:
                print("✅ Profile authentication works")
            else:
                print(f"❌ Profile authentication failed: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
                return
            
            # Create a simple test image
            print("\n🖼️  Creating test image...")
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            # Test image upload endpoint
            print("\n📸 Testing image upload with authentication...")
            
            # Method 1: Using files parameter (multipart/form-data)
            files = {"file": ("test.jpg", img_buffer.getvalue(), "image/jpeg")}
            
            upload_response = await client.post(
                f"{base_url}/teacher/profile/upload-image",
                headers=headers,
                files=files
            )
            
            print(f"Upload response status: {upload_response.status_code}")
            print(f"Upload response body: {upload_response.text}")
            
            if upload_response.status_code == 401:
                print("\n🔍 Debugging authentication headers...")
                print(f"Authorization header: {headers.get('Authorization', 'MISSING')}")
                
                # Check if token is valid by decoding it
                import jwt
                from app.core.jwt import decode_token
                
                try:
                    # Test token decoding
                    payload = decode_token(token)
                    print(f"Token payload: {payload}")
                    
                    if payload:
                        print("✅ Token is valid")
                    else:
                        print("❌ Token is invalid")
                        
                except Exception as e:
                    print(f"❌ Token decode error: {e}")
            
            elif upload_response.status_code == 200:
                result = upload_response.json()
                print(f"✅ Image upload successful!")
                print(f"Image URL: {result.get('image_url', 'N/A')}")
            
            else:
                print(f"❌ Unexpected status: {upload_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_image_upload())