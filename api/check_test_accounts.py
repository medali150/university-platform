#!/usr/bin/env python3
"""
Quick check for existing accounts and create teacher if needed
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Try to create teacher account with a different email
print("🔍 CHECKING EXISTING ACCOUNTS AND CREATING TEACHER")
print("=" * 60)

# First, let's try to use an existing teacher account
existing_teachers = [
    {"email": "wahid@gmail.com", "password": "dalighgh15"},
    {"email": "prof.teacher@university.edu", "password": "teacher123"},
    {"email": "teacher@example.com", "password": "teacher123"}
]

print("🔍 Testing existing teacher accounts...")
teacher_credentials = None

for teacher in existing_teachers:
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=teacher)
        if login_response.status_code == 200:
            token_data = login_response.json()
            teacher_credentials = {
                "email": teacher["email"],
                "password": teacher["password"],
                "token": token_data.get("access_token"),
                "user_id": token_data.get("user", {}).get("id"),
                "name": f"{token_data.get('user', {}).get('prenom', '')} {token_data.get('user', {}).get('nom', '')}"
            }
            print(f"✅ Found working teacher account: {teacher['email']}")
            break
    except:
        continue

# If no existing teacher found, create a new one
if not teacher_credentials:
    print("⚠️ No existing teacher accounts found. Creating new one...")
    
    teacher_data = {
        "nom": "Slimi",
        "prenom": "Mohammed",
        "email": "prof.slimi@university.edu",
        "password": "prof2025",
        "role": "TEACHER"
    }
    
    try:
        teacher_response = requests.post(f"{BASE_URL}/auth/register", json=teacher_data)
        if teacher_response.status_code in [200, 201]:
            print(f"✅ Created new teacher: {teacher_data['email']}")
            
            # Test login
            login_response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": teacher_data["email"],
                "password": teacher_data["password"]
            })
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                teacher_credentials = {
                    "email": teacher_data["email"],
                    "password": teacher_data["password"],
                    "token": token_data.get("access_token"),
                    "user_id": token_data.get("user", {}).get("id"),
                    "name": f"{teacher_data['prenom']} {teacher_data['nom']}"
                }
                print("✅ Teacher login successful!")
        else:
            print(f"❌ Failed to create teacher: {teacher_response.text}")
    except Exception as e:
        print(f"❌ Teacher creation error: {e}")

# Student credentials (from previous creation)
student_credentials = {
    "email": "ahmed.student@university.edu",
    "password": "student2025",
    "user_id": "cmgcddtqz0000bmt05gubws8y",
    "name": "Ahmed Ben Salem"
}

print()
print("🎯 FINAL TEST ACCOUNT SUMMARY")
print("=" * 50)

if teacher_credentials:
    print("👨‍🏫 TEACHER ACCOUNT:")
    print(f"   📧 Email: {teacher_credentials['email']}")
    print(f"   🔑 Password: {teacher_credentials['password']}")
    print(f"   👤 Name: {teacher_credentials['name']}")
    print(f"   🆔 User ID: {teacher_credentials['user_id']}")
else:
    print("❌ No teacher account available")

print()
print("👨‍🎓 STUDENT ACCOUNT:")
print(f"   📧 Email: {student_credentials['email']}")
print(f"   🔑 Password: {student_credentials['password']}")
print(f"   👤 Name: {student_credentials['name']}")
print(f"   🆔 User ID: {student_credentials['user_id']}")

print()
print("🧪 MANUAL TESTING INSTRUCTIONS:")
print("=" * 50)
print("1. Open your frontend application")
print("2. Login as TEACHER with the credentials above")
print("3. Navigate to absence management")
print("4. Mark STUDENT absent")
print("5. Check notification logs in the API console")
print("6. Login as STUDENT to check received notifications")
print()

print("📡 TEST ABSENCE MARKING API CALL:")
print("-" * 40)
if teacher_credentials:
    print(f"POST {BASE_URL}/teacher/mark-absence")
    print(f"Authorization: Bearer {teacher_credentials['token'][:30]}...")
    print("Content-Type: application/json")
    print()
    print("Body:")
    test_payload = {
        "student_email": student_credentials["email"],
        "student_name": student_credentials["name"],
        "subject_name": "Programming",
        "absence_date": "2025-10-04",
        "absence_time": "10:00",
        "reason": "Manual test absence"
    }
    print(json.dumps(test_payload, indent=2))

print()
print("✅ READY FOR MANUAL TESTING!")
print("Use the credentials above to test the absence notification system!")