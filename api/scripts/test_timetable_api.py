#!/usr/bin/env python3
"""
Test timetable API endpoints directly
"""
import asyncio
import requests
import json

async def test_timetable_endpoints():
    """Test timetable API endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Login with test credentials
    login_data = {
        "email": "test.depthead@university.com",
        "password": "test123"
    }
    
    print("🔐 Logging in...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            # Test each endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            
            endpoints = [
                ("/department-head/timetable/groups", "Groups"),
                ("/department-head/timetable/teachers", "Teachers"),
                ("/department-head/timetable/subjects", "Subjects"),
                ("/department-head/timetable/specialities", "Specialities"),
                ("/department-head/timetable/rooms", "Rooms")
            ]
            
            for endpoint, name in endpoints:
                print(f"\n🔍 Testing {name} ({endpoint})")
                try:
                    response = requests.get(f"{base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {name}: {len(data)} items")
                        
                        # Show first item structure
                        if data and len(data) > 0:
                            print(f"   📋 Sample item keys: {list(data[0].keys())}")
                            if name == "Groups" and data[0]:
                                print(f"   👥 First group: {data[0].get('nom', 'N/A')}")
                            elif name == "Subjects" and data[0]:
                                print(f"   📚 First subject: {data[0].get('nom', 'N/A')}")
                            elif name == "Specialities" and data[0]:
                                print(f"   🎓 First speciality: {data[0].get('nom', 'N/A')}")
                    else:
                        print(f"❌ {name}: Status {response.status_code}")
                        print(f"   Response: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"❌ {name}: Request error - {e}")
        else:
            print(f"❌ Login failed: Status {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_timetable_endpoints())