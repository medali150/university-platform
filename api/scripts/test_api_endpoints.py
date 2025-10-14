#!/usr/bin/env python3
"""
Direct API test to check timetable endpoints
"""
import asyncio
import requests
import json
from prisma import Prisma

async def test_api_endpoints():
    """Test API endpoints directly"""
    
    base_url = "http://localhost:8000"
    
    # Test if API is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("Please start the backend server first:")
        print("cd c:\\Users\\pc\\universety_app\\api")
        print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Get a test token for department head
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Get department head user
        dept_head_user = await prisma.utilisateur.find_first(
            where={"email": "boubaker@university.com"}
        )
        
        if not dept_head_user:
            print("❌ Test department head user not found")
            return
            
        print(f"👤 Found test user: {dept_head_user.email}")
        
        # Try to login and get token
        login_data = {
            "email": "boubaker@university.com",
            "password": "password123"  # Default password from sample data
        }
        
        print("🔐 Attempting login...")
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            # Test timetable endpoints with token
            headers = {"Authorization": f"Bearer {access_token}"}
            
            endpoints_to_test = [
                "/department-head/timetable/groups",
                "/department-head/timetable/teachers", 
                "/department-head/timetable/subjects",
                "/department-head/timetable/specialities",
                "/department-head/timetable/rooms"
            ]
            
            for endpoint in endpoints_to_test:
                print(f"\n🔍 Testing {endpoint}")
                try:
                    response = requests.get(f"{base_url}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Success - {len(data)} items returned")
                        if data:
                            print(f"   📋 Sample item: {data[0] if len(data) > 0 else 'None'}")
                    else:
                        print(f"❌ Failed - Status: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Request error: {e}")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())