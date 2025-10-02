#!/usr/bin/env python3
"""
Test script to verify API endpoints are working with sample data
"""

import requests
import json
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Department Head Dashboard API Endpoints")
    print("=" * 50)
    
    try:
        # Test login
        print("1. Testing login...")
        login_data = {
            "login": "depthead",
            "password": "depthead123"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        login_result = response.json()
        token = login_result["access_token"]
        print("✅ Login successful!")
        
        # Set headers for authenticated requests
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test endpoints
        endpoints_to_test = [
            ("/schedules/resources/subjects", "Subjects"),
            ("/schedules/resources/teachers", "Teachers"), 
            ("/schedules/resources/groups", "Groups"),
            ("/schedules/resources/rooms", "Rooms"),
            ("/schedules/", "Schedules")
        ]
        
        for endpoint, name in endpoints_to_test:
            print(f"\n2. Testing {name} endpoint: {endpoint}")
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {name}: {len(data)} items found")
                    if data:
                        print(f"   First item: {json.dumps(data[0], indent=2)}")
                else:
                    print(f"❌ {name}: Status {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ {name}: Error - {str(e)}")
        
        print("\n🎉 API Endpoint testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        print("💡 Start the server with: python start_server.py")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())