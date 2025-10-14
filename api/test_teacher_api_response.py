#!/usr/bin/env python3
"""
Test the teacher API to see the exact response format
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Login as teacher
teacher_creds = {
    "email": "wahid@gmail.com",
    "password": "dalighgh15"
}

print("🔍 TESTING TEACHER API RESPONSE FORMAT")
print("=" * 50)

try:
    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_creds)
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get("access_token")
        print("✅ Teacher login successful")
        
        # Get teacher groups
        headers = {"Authorization": f"Bearer {token}"}
        groups_response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
        
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"✅ Found {len(groups)} groups")
            
            if groups:
                # Test first group
                group_id = groups[0]["id"]
                print(f"🔍 Testing group: {group_id}")
                
                # Get group students
                students_response = requests.get(
                    f"{BASE_URL}/teacher/groups/{group_id}/students", 
                    headers=headers
                )
                
                if students_response.status_code == 200:
                    group_data = students_response.json()
                    print("✅ Group students API response:")
                    print(json.dumps(group_data, indent=2, default=str))
                else:
                    print(f"❌ Group students failed: {students_response.status_code}")
                    print(students_response.text)
            else:
                print("⚠️ No groups found for teacher")
        else:
            print(f"❌ Groups failed: {groups_response.status_code}")
            print(groups_response.text)
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)

except Exception as e:
    print(f"❌ Error: {e}")