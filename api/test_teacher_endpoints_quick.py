#!/usr/bin/env python3

import asyncio
import httpx

async def test_teacher_endpoints():
    """Test teacher endpoints with real authentication"""
    print("=== TESTING TEACHER ENDPOINTS ===")
    
    base_url = "http://localhost:8000"
    
    # Login first
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login
            print("\n1. 🔑 Logging in...")
            login_response = await client.post(
                f"{base_url}/auth/login",
                json=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login successful!")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test each endpoint that was failing
            endpoints_to_test = [
                ("/teacher/groups", "GET groups"),
                ("/teacher/groups/detailed", "GET groups detailed"),
                ("/teacher/schedule/today", "GET today's schedule"),
                ("/teacher/stats", "GET teacher stats"),
                ("/teacher/profile", "GET teacher profile")
            ]
            
            for endpoint, desc in endpoints_to_test:
                print(f"\n2. 📋 Testing {desc}...")
                
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {desc} - Success!")
                    
                    # Show some preview of the data
                    if isinstance(data, list):
                        print(f"   Returned {len(data)} items")
                        if data and len(data) > 0:
                            print(f"   First item keys: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"   Returned keys: {list(data.keys())}")
                        if 'groups' in data:
                            print(f"   Groups count: {len(data['groups'])}")
                        if 'schedules' in data:
                            print(f"   Schedules count: {len(data['schedules'])}")
                else:
                    print(f"❌ {desc} - Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_teacher_endpoints())