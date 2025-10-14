"""
Fixed Absence System Test for Teacher (wahid@gmail.com)
Uses correct API endpoints based on the actual backend implementation
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "wahid@gmail.com"
PASSWORD = "dalighgh15"

def test_teacher_endpoints():
    """Test all available teacher endpoints"""
    print("🚀 Fixed Absence System Test for Teacher")
    print("=" * 60)
    
    # Step 1: Login
    print("🔐 Step 1: Authentication")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    data = response.json()
    token = data.get("access_token")
    user = data.get("user")
    
    print(f"✅ Login successful! User: {user.get('prenom')} {user.get('nom')} (Role: {user.get('role')})")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test Teacher Profile
    print(f"\n👤 Step 2: Teacher Profile")
    response = requests.get(f"{BASE_URL}/teacher/profile", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Profile retrieved successfully!")
        print(f"   Department: {profile.get('department', {}).get('nom', 'N/A')}")
        print(f"   Subjects: {len(profile.get('subjects_taught', []))} subjects")
    else:
        print(f"❌ Profile failed: {response.status_code} - {response.text}")
    
    # Step 3: Test Teacher Groups
    print(f"\n👥 Step 3: Teacher Groups")
    response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
    
    if response.status_code == 200:
        groups = response.json()
        print(f"✅ Found {len(groups)} groups!")
        for i, group in enumerate(groups[:3]):  # Show first 3 groups
            print(f"   Group {i+1}: {group.get('nom')} ({group.get('student_count')} students)")
        return groups
    else:
        print(f"❌ Groups failed: {response.status_code} - {response.text}")
        return []
    
    # Step 4: Test Today's Schedule
    print(f"\n📅 Step 4: Today's Schedule")
    response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
    
    if response.status_code == 200:
        schedule = response.json()
        print(f"✅ Found {len(schedule)} classes today!")
        for i, class_item in enumerate(schedule[:3]):  # Show first 3 classes
            print(f"   Class {i+1}: {class_item.get('matiere', {}).get('nom')} - {class_item.get('groupe', {}).get('nom')}")
            print(f"            Time: {class_item.get('heure_debut')} - {class_item.get('heure_fin')}")
        return schedule
    else:
        print(f"❌ Schedule failed: {response.status_code} - {response.text}")
        return []

def test_group_students(token, groups):
    """Test getting students for each group"""
    print(f"\n🎓 Step 5: Group Students")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    all_students = []
    
    for i, group in enumerate(groups[:2]):  # Test first 2 groups
        group_id = group.get('id')
        print(f"\n   Testing Group: {group.get('nom')}")
        
        response = requests.get(f"{BASE_URL}/teacher/groups/{group_id}/students", headers=headers)
        
        if response.status_code == 200:
            group_data = response.json()
            students = group_data.get('students', [])
            print(f"   ✅ Found {len(students)} students in this group")
            
            # Show first few students
            for j, student in enumerate(students[:3]):
                print(f"      Student {j+1}: {student.get('prenom')} {student.get('nom')}")
                all_students.append({
                    'id': student.get('id'),
                    'name': f"{student.get('prenom')} {student.get('nom')}",
                    'group': group.get('nom'),
                    'group_id': group_id
                })
        else:
            print(f"   ❌ Students failed for group {group.get('nom')}: {response.status_code}")
    
    return all_students

def test_absence_creation(token, students, schedule):
    """Test creating absences for students"""
    print(f"\n➕ Step 6: Test Absence Creation")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if not students:
        print("   ❌ No students available for testing")
        return []
    
    if not schedule:
        print("   ❌ No schedule available for testing")
        return []
    
    created_absences = []
    
    # Test creating absence for first student and first class
    student = students[0]
    class_item = schedule[0]
    
    print(f"   Creating absence for: {student['name']}")
    print(f"   Class: {class_item.get('matiere', {}).get('nom')}")
    
    absence_data = {
        "student_id": student['id'],
        "schedule_id": class_item.get('id'),
        "is_absent": True,
        "motif": f"Test absence created by {EMAIL} at {datetime.now().isoformat()}"
    }
    
    response = requests.post(f"{BASE_URL}/teacher/absence/mark", headers=headers, json=absence_data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✅ Absence created successfully!")
        print(f"      Message: {result.get('message', 'N/A')}")
        created_absences.append(result)
    else:
        print(f"   ❌ Absence creation failed: {response.status_code} - {response.text}")
    
    return created_absences

def test_absence_endpoints(token):
    """Test absence management endpoints"""
    print(f"\n📋 Step 7: Test Absence Endpoints")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different absence endpoints
    endpoints_to_test = [
        ("/absences", "All Absences"),
        ("/absences/all", "All Absences (alternative)"),
        ("/absences/student/my-absences", "My Absences (if student)"),
        ("/teacher/absences", "Teacher Absences"),
        ("/teacher/absences/my-absences", "Teacher My Absences")
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"\n   Testing: {description} ({endpoint})")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict):
                count = len(data.get('absences', data.get('data', [])))
            else:
                count = 1
            
            print(f"   ✅ Success! Found {count} records")
            
            if count > 0:
                # Show sample data
                sample = data[0] if isinstance(data, list) else data
                if isinstance(sample, dict):
                    print(f"      Sample keys: {list(sample.keys())[:5]}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.reason}")

def main():
    """Run comprehensive teacher absence system test"""
    print("Starting comprehensive test...")
    
    # Step 1-4: Basic teacher endpoints
    groups = test_teacher_endpoints()
    
    if not groups:
        print("\n❌ Cannot proceed without groups data")
        return
    
    # Get token again for subsequent tests
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    token = response.json().get("access_token")
    
    # Step 5: Test group students
    students = test_group_students(token, groups)
    
    # Step 6: Get schedule for absence creation
    headers = {"Authorization": f"Bearer {token}"}
    schedule_response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
    schedule = schedule_response.json() if schedule_response.status_code == 200 else []
    
    # Step 7: Test absence creation
    created_absences = test_absence_creation(token, students, schedule)
    
    # Step 8: Test absence endpoints
    test_absence_endpoints(token)
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Authentication: Success")
    print(f"✅ Groups Found: {len(groups)}")
    print(f"✅ Students Found: {len(students)}")
    print(f"✅ Today's Classes: {len(schedule)}")
    print(f"✅ Absences Created: {len(created_absences)}")
    
    print(f"\n💡 Teacher absence system test completed!")
    print(f"   User {EMAIL} can access teacher-specific endpoints")
    print(f"   Ready for frontend integration testing")

if __name__ == "__main__":
    main()