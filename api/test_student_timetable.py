import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials for student
student_creds = {
    "email": "ahmed.ben ali@student.iset.tn",
    "password": "student123"
}

def test_student_timetable():
    print("Testing student timetable API...")
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json=student_creds)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get("access_token")
    print(f"Got access token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test student timetable endpoint
    print("\n=== Testing /timetable/student ===")
    response = requests.get(f"{BASE_URL}/timetable/student", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} entries")
        if data:
            print("Sample entry:")
            print(json.dumps(data[0], indent=2, default=str))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_student_timetable()