import requests
import json

# Test teacher registration with department
API_BASE = "http://localhost:8000"

# First get departments to choose one
print("📋 Getting departments...")
try:
    deps_response = requests.get(f"{API_BASE}/auth/departments")
    if deps_response.status_code == 200:
        departments = deps_response.json()
        print(f"✅ Found {len(departments)} departments")
        if departments:
            dept_id = departments[0]["id"]
            dept_name = departments[0]["nom"]
            print(f"🎯 Using department: {dept_name} (ID: {dept_id})")
            
            # Test teacher registration with department_id as query parameter
            teacher_data = {
                "nom": "TestTeacher",
                "prenom": "Registration",
                "email": "test.teacher.registration@university.com",
                "password": "test123",
                "role": "TEACHER"
            }
            
            print("\n👨‍🏫 Testing teacher registration with department_id as query parameter...")
            url = f"{API_BASE}/auth/register?department_id={dept_id}"
            response = requests.post(url, json=teacher_data)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("✅ Teacher registration successful!")
            else:
                print("❌ Teacher registration failed!")
        else:
            print("❌ No departments found")
    else:
        print(f"❌ Failed to get departments: {deps_response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")