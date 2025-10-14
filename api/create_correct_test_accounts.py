#!/usr/bin/env python3
"""
Create correct test accounts for manual frontend testing
Uses the proper API schema with nom/prenom fields
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def create_manual_test_accounts():
    """Create teacher and student accounts with correct schema for manual testing"""
    
    print("🏫 CREATING MANUAL TEST ACCOUNTS (CORRECTED SCHEMA)")
    print("=" * 70)
    print(f"📅 Creation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    # Check if server is running
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ API server is running")
    except:
        print("❌ API server is not accessible. Please start the server first.")
        return False
    
    print()
    
    # 1. CREATE TEACHER ACCOUNT
    print("👨‍🏫 CREATING TEACHER ACCOUNT")
    print("-" * 40)
    
    teacher_data = {
        "nom": "Al-Rashid",          # Last name
        "prenom": "Mohammed",        # First name
        "email": "mohammed.teacher@university.edu",
        "password": "teacher2025",
        "role": "TEACHER"           # Must be uppercase
    }
    
    try:
        teacher_response = requests.post(f"{BASE_URL}/auth/register", json=teacher_data)
        
        if teacher_response.status_code in [200, 201]:
            teacher_info = teacher_response.json()
            print(f"✅ Teacher Account Created Successfully!")
            print(f"   📧 Email: {teacher_data['email']}")
            print(f"   🔑 Password: {teacher_data['password']}")
            print(f"   📛 Name: {teacher_data['prenom']} {teacher_data['nom']}")
            print(f"   🆔 User ID: {teacher_info.get('id', 'N/A')}")
            teacher_created = True
        else:
            print(f"❌ Teacher registration failed: {teacher_response.status_code}")
            print(f"   Error: {teacher_response.text}")
            teacher_created = False
    except Exception as e:
        print(f"❌ Teacher registration error: {e}")
        teacher_created = False
    
    print()
    
    # 2. CREATE STUDENT ACCOUNT
    print("👨‍🎓 CREATING STUDENT ACCOUNT")
    print("-" * 40)
    
    student_data = {
        "nom": "Ben Salem",          # Last name
        "prenom": "Ahmed",           # First name
        "email": "ahmed.student@university.edu",
        "password": "student2025", 
        "role": "STUDENT"           # Must be uppercase
    }
    
    try:
        student_response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
        
        if student_response.status_code in [200, 201]:
            student_info = student_response.json()
            print(f"✅ Student Account Created Successfully!")
            print(f"   📧 Email: {student_data['email']}")
            print(f"   🔑 Password: {student_data['password']}")
            print(f"   📛 Name: {student_data['prenom']} {student_data['nom']}")
            print(f"   🆔 User ID: {student_info.get('id', 'N/A')}")
            student_created = True
        else:
            print(f"❌ Student registration failed: {student_response.status_code}")
            print(f"   Error: {student_response.text}")
            student_created = False
    except Exception as e:
        print(f"❌ Student registration error: {e}")
        student_created = False
    
    print()
    
    # 3. TEST LOGIN FOR BOTH ACCOUNTS
    print("🔐 TESTING LOGIN FOR BOTH ACCOUNTS")
    print("-" * 50)
    
    teacher_token = None
    student_token = None
    teacher_user_id = None
    student_user_id = None
    
    if teacher_created:
        # Test teacher login
        teacher_login = {
            "email": teacher_data['email'],
            "password": teacher_data['password']
        }
        
        try:
            teacher_login_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
            
            if teacher_login_response.status_code == 200:
                teacher_token_data = teacher_login_response.json()
                teacher_token = teacher_token_data.get('access_token')
                teacher_user_info = teacher_token_data.get('user', {})
                teacher_user_id = teacher_user_info.get('id')
                print(f"✅ Teacher login successful!")
                print(f"   🎫 Token: {teacher_token[:30]}...")
                print(f"   👤 User ID: {teacher_user_id}")
            else:
                print(f"❌ Teacher login failed: {teacher_login_response.status_code}")
                print(f"   Error: {teacher_login_response.text}")
        except Exception as e:
            print(f"❌ Teacher login error: {e}")
    
    if student_created:
        # Test student login
        student_login = {
            "email": student_data['email'],
            "password": student_data['password']
        }
        
        try:
            student_login_response = requests.post(f"{BASE_URL}/auth/login", json=student_login)
            
            if student_login_response.status_code == 200:
                student_token_data = student_login_response.json()
                student_token = student_token_data.get('access_token')
                student_user_info = student_token_data.get('user', {})
                student_user_id = student_user_info.get('id')
                print(f"✅ Student login successful!")
                print(f"   🎫 Token: {student_token[:30]}...")
                print(f"   👤 User ID: {student_user_id}")
            else:
                print(f"❌ Student login failed: {student_login_response.status_code}")
                print(f"   Error: {student_login_response.text}")
        except Exception as e:
            print(f"❌ Student login error: {e}")
    
    print()
    
    # 4. MANUAL TESTING GUIDE
    print("🧪 MANUAL FRONTEND TESTING GUIDE")
    print("=" * 70)
    print()
    
    print("🔐 TEST ACCOUNT CREDENTIALS:")
    print("-" * 40)
    print()
    print("👨‍🏫 TEACHER ACCOUNT:")
    print(f"   📧 Email: {teacher_data['email']}")
    print(f"   🔑 Password: {teacher_data['password']}")
    print(f"   👤 Full Name: {teacher_data['prenom']} {teacher_data['nom']}")
    if teacher_user_id:
        print(f"   🆔 User ID: {teacher_user_id}")
    print()
    print("👨‍🎓 STUDENT ACCOUNT:")
    print(f"   📧 Email: {student_data['email']}")
    print(f"   🔑 Password: {student_data['password']}")
    print(f"   👤 Full Name: {student_data['prenom']} {student_data['nom']}")
    if student_user_id:
        print(f"   🆔 User ID: {student_user_id}")
    print()
    
    print("📋 TESTING WORKFLOW:")
    print("-" * 30)
    print("1. 🌐 Open your frontend application (usually http://localhost:3000)")
    print("2. 🔑 Login as TEACHER using the credentials above")
    print("3. 📝 Navigate to the teacher dashboard/absence management")
    print("4. ❌ Mark the STUDENT absent for any subject")
    print("5. 📧 Check if absence notification is sent to student")
    print("6. 🔄 Logout and login as STUDENT")
    print("7. 🔔 Check student notifications/dashboard for the absence alert")
    print("8. ✅ Verify notification contains correct information")
    print()
    
    print("🔍 WHAT TO VERIFY:")
    print("-" * 25)
    print("✅ Teacher can mark student absent")
    print("✅ Absence notification is triggered")
    print("✅ Student receives notification email/in-app")
    print("✅ Notification shows correct subject and time")
    print("✅ Student can justify the absence")
    print("✅ Teacher gets justification notification")
    print()
    
    print("🛠️ DEBUGGING TOOLS:")
    print("-" * 25)
    print("• Browser Developer Tools (F12)")
    print("• Network tab to monitor API calls")
    print("• Console tab for JavaScript errors")
    print("• API server logs for notification calls")
    print()
    
    # 5. API TESTING COMMANDS
    if teacher_token and student_token:
        print("🧪 API TESTING COMMANDS:")
        print("-" * 35)
        print()
        print("📝 Test absence marking (use in Postman or curl):")
        print("POST http://localhost:8000/teacher/mark-absence")
        print(f"Authorization: Bearer {teacher_token}")
        print("Content-Type: application/json")
        print()
        print("Body example:")
        test_absence_payload = {
            "student_email": student_data['email'],
            "student_name": f"{student_data['prenom']} {student_data['nom']}",
            "subject_name": "Mathematics",
            "absence_date": datetime.now().strftime('%Y-%m-%d'),
            "absence_time": "10:00",
            "reason": "Late arrival"
        }
        print(json.dumps(test_absence_payload, indent=2))
        print()
        
        print("🔔 Check student notifications:")
        print(f"GET http://localhost:8000/notifications/user/{student_user_id}")
        print(f"Authorization: Bearer {student_token}")
        print()
    
    print("🎯 NOTIFICATION TESTING STEPS:")
    print("-" * 40)
    print("1. Mark student absent using teacher account")
    print("2. Check server console for notification service logs")
    print("3. Look for 'AbsenceNotificationService' log messages")
    print("4. Verify notification was sent successfully")
    print("5. Check student dashboard for new notifications")
    print()
    
    success = teacher_created and student_created and teacher_token and student_token
    
    if success:
        print("🎉 SUCCESS! Both accounts are ready for manual testing!")
        print("🚀 Start your frontend and test the absence notification system!")
    else:
        print("⚠️ Some accounts may not be fully functional. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = create_manual_test_accounts()
    if success:
        print("\n✅ Manual test setup completed successfully!")
    else:
        print("\n❌ Manual test setup had some issues. Please check the logs.")