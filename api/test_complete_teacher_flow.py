import requests
import json

API_BASE = "http://localhost:8000"

def test_teacher_registration():
    """Test teacher registration with department selection"""
    
    # First, get available departments
    print("1. Getting available departments...")
    try:
        dept_response = requests.get(f"{API_BASE}/auth/departments")
        print(f"Departments Status: {dept_response.status_code}")
        departments = dept_response.json()
        print("Available departments:", json.dumps(departments, indent=2))
        
        if not departments.get('departments'):
            print("❌ No departments available!")
            return
            
        # Use the first department
        dept_id = departments['departments'][0]['id']
        dept_name = departments['departments'][0]['nom']
        print(f"✅ Using department: {dept_name} (ID: {dept_id})")
        
    except Exception as e:
        print(f"❌ Error getting departments: {e}")
        return
    
    # Test teacher registration
    print("\n2. Testing teacher registration...")
    teacher_data = {
        "nom": "TestTeacher",
        "prenom": "New",
        "email": "newteacher@university.com",
        "password": "teacher123",
        "role": "TEACHER"
    }
    
    url = f"{API_BASE}/auth/register?department_id={dept_id}"
    
    try:
        response = requests.post(url, json=teacher_data)
        print(f"Registration Status: {response.status_code}")
        result = response.json()
        print("Registration Response:", json.dumps(result, indent=2))
        
        if response.status_code == 200:
            print("✅ Teacher registration successful!")
            
            # Test login
            print("\n3. Testing teacher login...")
            login_data = {
                "email": teacher_data["email"],
                "password": teacher_data["password"]
            }
            
            login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Teacher login successful!")
                print(f"User: {login_result['user']['prenom']} {login_result['user']['nom']} ({login_result['user']['role']})")
            else:
                print("❌ Teacher login failed:", login_response.json())
                
        else:
            print("❌ Teacher registration failed!")
            
    except Exception as e:
        print(f"❌ Error during teacher registration: {e}")

if __name__ == "__main__":
    test_teacher_registration()