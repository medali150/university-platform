#!/usr/bin/env python3
"""
Test the absence notification system with the created accounts
This script simulates marking a student absent and checks if notifications are sent
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

# Test account credentials
TEACHER_CREDS = {
    "email": "wahid@gmail.com",
    "password": "dalighgh15"
}

STUDENT_CREDS = {
    "email": "ahmed.student@university.edu", 
    "password": "student2025"
}

def test_absence_notification_system():
    """Test the complete absence notification workflow"""
    
    print("🧪 TESTING ABSENCE NOTIFICATION SYSTEM")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Login as teacher
    print("1️⃣ TEACHER LOGIN")
    print("-" * 20)
    
    try:
        teacher_login_response = requests.post(f"{BASE_URL}/auth/login", json=TEACHER_CREDS)
        
        if teacher_login_response.status_code == 200:
            teacher_data = teacher_login_response.json()
            teacher_token = teacher_data.get("access_token")
            teacher_info = teacher_data.get("user", {})
            print(f"✅ Teacher logged in successfully")
            print(f"   👤 Name: {teacher_info.get('prenom')} {teacher_info.get('nom')}")
            print(f"   📧 Email: {teacher_info.get('email')}")
            print(f"   🆔 ID: {teacher_info.get('id')}")
        else:
            print(f"❌ Teacher login failed: {teacher_login_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Teacher login error: {e}")
        return False
    
    print()
    
    # Step 2: Login as student
    print("2️⃣ STUDENT LOGIN")
    print("-" * 20)
    
    try:
        student_login_response = requests.post(f"{BASE_URL}/auth/login", json=STUDENT_CREDS)
        
        if student_login_response.status_code == 200:
            student_data = student_login_response.json()
            student_token = student_data.get("access_token")
            student_info = student_data.get("user", {})
            print(f"✅ Student logged in successfully")
            print(f"   👤 Name: {student_info.get('prenom')} {student_info.get('nom')}")
            print(f"   📧 Email: {student_info.get('email')}")
            print(f"   🆔 ID: {student_info.get('id')}")
        else:
            print(f"❌ Student login failed: {student_login_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Student login error: {e}")
        return False
    
    print()
    
    # Step 3: Mark student absent
    print("3️⃣ MARKING STUDENT ABSENT")
    print("-" * 30)
    
    absence_payload = {
        "student_email": student_info.get("email"),
        "student_name": f"{student_info.get('prenom')} {student_info.get('nom')}",
        "subject_name": "Programming Fundamentals",
        "absence_date": datetime.now().strftime('%Y-%m-%d'),
        "absence_time": "10:30",
        "reason": "Test absence for notification system"
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    try:
        print("📝 Marking absence with payload:")
        print(json.dumps(absence_payload, indent=2))
        print()
        
        absence_response = requests.post(
            f"{BASE_URL}/teacher/mark-absence", 
            json=absence_payload,
            headers=headers
        )
        
        if absence_response.status_code in [200, 201]:
            absence_result = absence_response.json()
            print("✅ Absence marked successfully!")
            print(f"   📋 Response: {json.dumps(absence_result, indent=2)}")
            
            # Check if notification was mentioned in response
            if "notification" in str(absence_result).lower():
                print("🔔 Notification mentioned in response!")
            else:
                print("⚠️ No notification mentioned in response")
                
        else:
            print(f"❌ Failed to mark absence: {absence_response.status_code}")
            print(f"   Error: {absence_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Absence marking error: {e}")
        return False
    
    print()
    
    # Step 4: Check for notifications (if endpoint exists)
    print("4️⃣ CHECKING STUDENT NOTIFICATIONS")
    print("-" * 40)
    
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Try different notification endpoints
    notification_endpoints = [
        f"/notifications/user/{student_info.get('id')}",
        f"/student/notifications",
        f"/notifications",
        f"/student/dashboard"
    ]
    
    for endpoint in notification_endpoints:
        try:
            print(f"🔍 Checking: GET {endpoint}")
            notification_response = requests.get(f"{BASE_URL}{endpoint}", headers=student_headers)
            
            if notification_response.status_code == 200:
                notifications = notification_response.json()
                print(f"✅ Endpoint works: {endpoint}")
                print(f"   📋 Response: {json.dumps(notifications, indent=2, default=str)[:200]}...")
                break
            else:
                print(f"   ❌ {notification_response.status_code}: {endpoint}")
        except Exception as e:
            print(f"   ❌ Error checking {endpoint}: {e}")
    
    print()
    
    # Step 5: Manual verification guide
    print("5️⃣ MANUAL VERIFICATION GUIDE")
    print("-" * 40)
    print("🔍 To manually verify the notification system:")
    print()
    print("📊 Check API Server Console/Logs for:")
    print("   • AbsenceNotificationService logs")
    print("   • Mock notification delivery messages")
    print("   • Any error messages during notification sending")
    print()
    print("🌐 In Frontend Application:")
    print("   1. Login as teacher and mark student absent")
    print("   2. Check if success message appears")
    print("   3. Login as student and check notifications section")
    print("   4. Look for absence notification in student dashboard")
    print()
    print("🛠️ Debug API Directly:")
    print(f"   • POST {BASE_URL}/teacher/mark-absence")
    print(f"   • GET {BASE_URL}/notifications/user/{student_info.get('id')}")
    print(f"   • Use tokens from this test for authorization")
    print()
    
    print("✅ ACCOUNTS READY FOR MANUAL TESTING!")
    print("=" * 60)
    print()
    print("🔐 CREDENTIALS FOR FRONTEND TESTING:")
    print()
    print("👨‍🏫 TEACHER LOGIN:")
    print(f"   📧 Email: {TEACHER_CREDS['email']}")
    print(f"   🔑 Password: {TEACHER_CREDS['password']}")
    print()
    print("👨‍🎓 STUDENT LOGIN:")
    print(f"   📧 Email: {STUDENT_CREDS['email']}")
    print(f"   🔑 Password: {STUDENT_CREDS['password']}")
    print()
    print("🎯 Now test manually in your frontend to see if notifications work!")
    
    return True

if __name__ == "__main__":
    success = test_absence_notification_system()
    if success:
        print("\n🎉 Test setup completed! Ready for manual frontend testing!")
    else:
        print("\n❌ Test setup failed. Please check the API server and accounts.")