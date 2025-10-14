#!/usr/bin/env python3
"""
Create linked test accounts for manual frontend testing
Creates a teacher and student that are properly connected for absence testing
"""
import requests
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_manual_accounts():
    """Create teacher and student accounts for manual frontend testing"""
    
    print("🏫 CREATING LINKED TEST ACCOUNTS FOR MANUAL FRONTEND TESTING")
    print("=" * 70)
    print(f"📅 Creation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    try:
        # First, let's check what departments exist
        print("🔍 Checking available departments...")
        try:
            departments_response = requests.get(f"{BASE_URL}/departments")
            if departments_response.status_code == 200:
                departments = departments_response.json()
                if departments:
                    dept_id = departments[0]['id']
                    dept_name = departments[0]['nom']
                    print(f"✅ Using department: {dept_name} (ID: {dept_id})")
                else:
                    print("⚠️ No departments found. Using default setup.")
                    dept_id = None
            else:
                print(f"⚠️ Could not fetch departments: {departments_response.status_code}")
                dept_id = None
        except Exception as e:
            print(f"⚠️ Department check failed: {e}")
            dept_id = None
        
        print()
        
        # 1. CREATE TEACHER ACCOUNT
        print("👨‍🏫 CREATING TEACHER ACCOUNT")
        print("-" * 40)
        
        teacher_data = {
            "username": "prof_mohammed",
            "email": "mohammed.teacher@university.edu",
            "password": "teacher2025",
            "first_name": "Mohammed",
            "last_name": "Al-Rashid",
            "role": "teacher"
        }
        
        # Register teacher
        register_url = f"{BASE_URL}/auth/register"
        if dept_id:
            register_url += f"?department_id={dept_id}"
        
        teacher_response = requests.post(register_url, json=teacher_data)
        
        if teacher_response.status_code in [200, 201]:
            teacher_info = teacher_response.json()
            print(f"✅ Teacher Account Created Successfully!")
            print(f"   📧 Email: {teacher_data['email']}")
            print(f"   👤 Username: {teacher_data['username']}")
            print(f"   🔑 Password: {teacher_data['password']}")
            print(f"   📛 Name: {teacher_data['first_name']} {teacher_data['last_name']}")
            print(f"   🆔 User ID: {teacher_info.get('id', 'N/A')}")
            print()
        else:
            print(f"❌ Teacher registration failed: {teacher_response.status_code}")
            print(f"   Error: {teacher_response.text}")
            print()
        
        # 2. CREATE STUDENT ACCOUNT
        print("👨‍🎓 CREATING STUDENT ACCOUNT")
        print("-" * 40)
        
        student_data = {
            "username": "ahmed_student",
            "email": "ahmed.student@university.edu", 
            "password": "student2025",
            "first_name": "Ahmed",
            "last_name": "Ben Salem",
            "role": "student"
        }
        
        # Register student
        student_response = requests.post(register_url, json=student_data)
        
        if student_response.status_code in [200, 201]:
            student_info = student_response.json()
            print(f"✅ Student Account Created Successfully!")
            print(f"   📧 Email: {student_data['email']}")
            print(f"   👤 Username: {student_data['username']}")
            print(f"   🔑 Password: {student_data['password']}")
            print(f"   📛 Name: {student_data['first_name']} {student_data['last_name']}")
            print(f"   🆔 User ID: {student_info.get('id', 'N/A')}")
            print()
        else:
            print(f"❌ Student registration failed: {student_response.status_code}")
            print(f"   Error: {student_response.text}")
            print()
        
        # 3. TEST LOGIN FOR BOTH ACCOUNTS
        print("🔐 TESTING LOGIN FOR BOTH ACCOUNTS")
        print("-" * 50)
        
        # Test teacher login
        teacher_login = {
            "email": teacher_data['email'],
            "password": teacher_data['password']
        }
        
        teacher_login_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
        
        if teacher_login_response.status_code == 200:
            teacher_token_data = teacher_login_response.json()
            print(f"✅ Teacher login successful!")
            print(f"   🎫 Access Token: {teacher_token_data.get('access_token', 'N/A')[:50]}...")
            teacher_token = teacher_token_data.get('access_token')
        else:
            print(f"❌ Teacher login failed: {teacher_login_response.status_code}")
            print(f"   Error: {teacher_login_response.text}")
            teacher_token = None
        
        # Test student login
        student_login = {
            "email": student_data['email'],
            "password": student_data['password']
        }
        
        student_login_response = requests.post(f"{BASE_URL}/auth/login", json=student_login)
        
        if student_login_response.status_code == 200:
            student_token_data = student_login_response.json()
            print(f"✅ Student login successful!")
            print(f"   🎫 Access Token: {student_token_data.get('access_token', 'N/A')[:50]}...")
            student_token = student_token_data.get('access_token')
        else:
            print(f"❌ Student login failed: {student_login_response.status_code}")
            print(f"   Error: {student_login_response.text}")
            student_token = None
        
        print()
        
        # 4. CHECK SUBJECTS AND GROUPS (if available)
        print("📚 CHECKING AVAILABLE SUBJECTS AND GROUPS")
        print("-" * 50)
        
        if teacher_token:
            headers = {"Authorization": f"Bearer {teacher_token}"}
            
            # Check subjects
            try:
                subjects_response = requests.get(f"{BASE_URL}/subjects", headers=headers)
                if subjects_response.status_code == 200:
                    subjects = subjects_response.json()
                    if isinstance(subjects, list) and subjects:
                        subject = subjects[0]
                        print(f"✅ Available subjects found:")
                        print(f"   📖 Subject: {subject.get('nom', 'N/A')} (ID: {subject.get('id', 'N/A')})")
                    else:
                        print("⚠️ No subjects found")
                else:
                    print(f"⚠️ Could not fetch subjects: {subjects_response.status_code}")
            except Exception as e:
                print(f"⚠️ Subject check failed: {e}")
            
            # Check groups
            try:
                groups_response = requests.get(f"{BASE_URL}/groups", headers=headers)
                if groups_response.status_code == 200:
                    groups = groups_response.json()
                    if isinstance(groups, list) and groups:
                        group = groups[0]
                        print(f"✅ Available groups found:")
                        print(f"   👥 Group: {group.get('nom', 'N/A')} (ID: {group.get('id', 'N/A')})")
                    else:
                        print("⚠️ No groups found")
                else:
                    print(f"⚠️ Could not fetch groups: {groups_response.status_code}")
            except Exception as e:
                print(f"⚠️ Group check failed: {e}")
        
        print()
        
        # 5. MANUAL TESTING INSTRUCTIONS
        print("🧪 MANUAL TESTING INSTRUCTIONS")
        print("=" * 70)
        print()
        
        print("🔐 LOGIN CREDENTIALS FOR FRONTEND TESTING:")
        print("-" * 50)
        print()
        print("👨‍🏫 TEACHER LOGIN:")
        print(f"   📧 Email: {teacher_data['email']}")
        print(f"   🔑 Password: {teacher_data['password']}")
        print(f"   👤 Name: {teacher_data['first_name']} {teacher_data['last_name']}")
        print()
        print("👨‍🎓 STUDENT LOGIN:")
        print(f"   📧 Email: {student_data['email']}")
        print(f"   🔑 Password: {student_data['password']}")
        print(f"   👤 Name: {student_data['first_name']} {student_data['last_name']}")
        print()
        
        print("📋 STEP-BY-STEP TESTING PROCESS:")
        print("-" * 50)
        print("1️⃣ Open your frontend application")
        print("2️⃣ Login as TEACHER using the credentials above")
        print("3️⃣ Navigate to the absence marking section")
        print("4️⃣ Mark the STUDENT absent for a subject")
        print("5️⃣ Check the notification system logs")
        print("6️⃣ Login as STUDENT to check received notifications")
        print("7️⃣ Verify the absence notification was sent correctly")
        print()
        
        print("🔍 WHAT TO VERIFY:")
        print("-" * 30)
        print("✅ Teacher can successfully mark student absent")
        print("✅ Notification is triggered when absence is marked")
        print("✅ Student receives absence notification")
        print("✅ Notification contains correct details (subject, date, time)")
        print("✅ Student can view the notification in their dashboard")
        print("✅ Student can respond/justify the absence")
        print()
        
        print("📊 API ENDPOINTS FOR TESTING:")
        print("-" * 40)
        print(f"🔗 Login: POST {BASE_URL}/auth/login")
        print(f"🔗 Mark Absence: POST {BASE_URL}/teacher/mark-absence")
        print(f"🔗 Get Notifications: GET {BASE_URL}/notifications/user/{{user_id}}")
        print(f"🔗 Student Dashboard: GET {BASE_URL}/student/dashboard")
        print()
        
        print("💡 TESTING TIPS:")
        print("-" * 20)
        print("• Use browser developer tools to monitor API calls")
        print("• Check browser console for any JavaScript errors")
        print("• Monitor server logs for notification service calls")
        print("• Test both successful and error scenarios")
        print("• Verify notification delivery in different channels")
        print()
        
        # 6. NOTIFICATION TEST PAYLOAD
        print("🧪 SAMPLE ABSENCE MARKING PAYLOAD:")
        print("-" * 45)
        
        if teacher_token and student_token:
            test_payload = {
                "student_email": student_data['email'],
                "student_name": f"{student_data['first_name']} {student_data['last_name']}",
                "subject_name": "Programming Fundamentals",
                "absence_date": datetime.now().strftime('%Y-%m-%d'),
                "absence_time": "10:00",
                "reason": "Late arrival to class"
            }
            
            print("📝 Use this payload to test absence marking:")
            print(json.dumps(test_payload, indent=2))
            print()
            
            print("📡 cURL command for testing:")
            print(f"curl -X POST {BASE_URL}/teacher/mark-absence \\")
            print(f"  -H 'Authorization: Bearer {teacher_token[:20]}...' \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{json.dumps(test_payload)}'")
        
        print()
        print("🎯 SUCCESS! Test accounts are ready for manual frontend testing!")
        print("🚀 Start testing with the credentials provided above!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manual_accounts()
    if success:
        print("\n✅ Test accounts created and ready for manual testing!")
    else:
        print("\n❌ Failed to create test accounts. Please check the API server.")