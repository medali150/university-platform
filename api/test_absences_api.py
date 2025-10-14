"""
Test script to check absence management API endpoints
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and get access token"""
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def test_get_all_absences(token):
    """Test getting all absences"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try different possible endpoints
    endpoints = [
        "/absences/",
        "/absences/all",
        "/absence-management/",
        "/absence-management/all"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"\nEndpoint {endpoint}:")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Data: {json.dumps(data, indent=2)}")
                return endpoint, data
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")
    
    return None, None

def test_teacher_mark_absence(token):
    """Test marking a student absent to create absence data"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First get teacher groups to find student and schedule IDs
    response = requests.get(f"{BASE_URL}/teacher/groups/detailed", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get teacher groups: {response.text}")
        return
    
    groups = response.json()
    print(f"Found {len(groups)} groups")
    
    if groups and len(groups) > 0:
        # Get students from first group
        group_id = list(groups.keys())[0] if isinstance(groups, dict) else groups[0]["id"]
        response = requests.get(f"{BASE_URL}/teacher/groups/{group_id}/students", headers=headers)
        
        if response.status_code == 200:
            students = response.json()
            print(f"Found {len(students)} students in group {group_id}")
            
            if students:
                # Get teacher's schedule
                response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
                if response.status_code == 200:
                    schedule = response.json()
                    print(f"Found {len(schedule)} schedule entries")
                    
                    if schedule:
                        # Mark first student absent for first schedule
                        absence_data = {
                            "student_id": students[0]["id"],
                            "schedule_id": schedule[0]["id"],
                            "motif": "Test absence from API script"
                        }
                        
                        response = requests.post(f"{BASE_URL}/teacher/absence/mark", 
                                               json=absence_data, headers=headers)
                        print(f"\nMarking absence status: {response.status_code}")
                        if response.status_code == 200:
                            print("Successfully marked student absent")
                            return response.json()
                        else:
                            print(f"Error marking absence: {response.text}")

if __name__ == "__main__":
    print("Testing absence management API...")
    
    # Get access token
    token = test_login()
    if not token:
        print("Failed to get access token")
        exit(1)
    
    print(f"Got access token: {token[:20]}...")
    
    # Mark a student absent to create test data
    print("\n=== Testing absence marking ===")
    test_teacher_mark_absence(token)
    
    # Test getting all absences
    print("\n=== Testing get all absences ===")
    endpoint, absences = test_get_all_absences(token)
    
    if absences:
        print(f"\nFound {len(absences)} absences using endpoint {endpoint}")
        for absence in absences[:2]:  # Show first 2
            print(f"Absence ID: {absence.get('id')}")
            print(f"Status: {absence.get('statut')}")
            print(f"Student: {absence.get('student', {}).get('prenom')} {absence.get('student', {}).get('nom')}")
            print("---")
    else:
        print("No absences found or API endpoint not working")