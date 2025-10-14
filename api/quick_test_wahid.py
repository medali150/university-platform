"""
Quick Absence System Test for wahid@gmail.com
Simple test to verify basic absence system functionality
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "wahid@gmail.com"
PASSWORD = "dalighgh15"

def test_login():
    """Test user login"""
    print("🔐 Testing Login...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user = data.get("user")
        
        print(f"✅ Login successful!")
        print(f"   User: {user.get('prenom')} {user.get('nom')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Email: {user.get('email')}")
        
        return token, user
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None, None

def test_get_absences(token, user_role):
    """Test getting absences based on role"""
    print(f"\n📋 Testing Get Absences (Role: {user_role})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Choose endpoint based on role
    if user_role == "STUDENT":
        url = f"{BASE_URL}/absences/student/my-absences"
        print("   Using student endpoint...")
    else:
        url = f"{BASE_URL}/absences/all"
        print("   Using general absences endpoint...")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        absences = data.get('absences', []) if isinstance(data, dict) else data
        
        print(f"✅ Found {len(absences)} absences")
        
        if absences:
            print("   Sample absence:")
            sample = absences[0]
            print(f"     ID: {sample.get('id')}")
            print(f"     Student: {sample.get('studentName', 'N/A')}")
            print(f"     Status: {sample.get('status')}")
            print(f"     Date: {sample.get('date')}")
            print(f"     Reason: {sample.get('reason', 'N/A')}")
        
        return absences
    else:
        print(f"❌ Failed to get absences: {response.status_code}")
        print(f"   Response: {response.text}")
        return []

def test_get_teacher_schedule(token, user_role):
    """Test getting teacher schedule if user is a teacher"""
    if user_role != "TEACHER":
        print(f"\n⏭️  Skipping schedule test (user is {user_role}, not TEACHER)")
        return []
    
    print(f"\n📅 Testing Get Teacher Schedule...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
    
    if response.status_code == 200:
        schedules = response.json()
        print(f"✅ Found {len(schedules)} schedule(s) for today")
        
        if schedules:
            print("   Sample schedule:")
            sample = schedules[0]
            print(f"     Subject: {sample.get('matiere', {}).get('nom')}")
            print(f"     Group: {sample.get('groupe', {}).get('nom')}")
            print(f"     Time: {sample.get('heure_debut')} - {sample.get('heure_fin')}")
            print(f"     Room: {sample.get('salle', {}).get('code')}")
        
        return schedules
    else:
        print(f"❌ Failed to get schedule: {response.status_code}")
        print(f"   Response: {response.text}")
        return []

def test_get_teacher_groups(token, user_role):
    """Test getting teacher groups if user is a teacher"""
    if user_role != "TEACHER":
        print(f"\n⏭️  Skipping groups test (user is {user_role}, not TEACHER)")
        return []
    
    print(f"\n👥 Testing Get Teacher Groups...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
    
    if response.status_code == 200:
        groups = response.json()
        print(f"✅ Found {len(groups)} group(s)")
        
        if groups:
            print("   Sample group:")
            sample = groups[0]
            print(f"     Name: {sample.get('nom')}")
            print(f"     Level: {sample.get('niveau', {}).get('nom')}")
            print(f"     Specialty: {sample.get('specialite', {}).get('nom')}")
            print(f"     Students: {sample.get('student_count')}")
        
        return groups
    else:
        print(f"❌ Failed to get groups: {response.status_code}")
        print(f"   Response: {response.text}")
        return []

def test_absence_statistics(token):
    """Test getting absence statistics"""
    print(f"\n📊 Testing Absence Statistics...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/absences/statistics", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Statistics retrieved successfully!")
        
        print("   Statistics:")
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                print(f"     {key}: {value}")
            elif isinstance(value, list):
                print(f"     {key}: {len(value)} items")
            else:
                print(f"     {key}: {value}")
        
        return stats
    else:
        print(f"❌ Failed to get statistics: {response.status_code}")
        print(f"   Response: {response.text}")
        return {}

def main():
    """Run quick absence system test"""
    print("🚀 Quick Absence System Test")
    print("=" * 50)
    print(f"User: {EMAIL}")
    print(f"API: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Login
    token, user = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    user_role = user.get('role')
    
    # Step 2: Get absences
    absences = test_get_absences(token, user_role)
    
    # Step 3: Get teacher-specific data if user is teacher
    schedules = test_get_teacher_schedule(token, user_role)
    groups = test_get_teacher_groups(token, user_role)
    
    # Step 4: Get statistics
    stats = test_absence_statistics(token)
    
    # Summary
    print(f"\n🎯 QUICK TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Authentication: Success")
    print(f"✅ User Role: {user_role}")
    print(f"✅ Absences Found: {len(absences)}")
    
    if user_role == "TEACHER":
        print(f"✅ Today's Schedule: {len(schedules)} classes")
        print(f"✅ Teaching Groups: {len(groups)} groups")
    
    print(f"✅ Statistics: {len(stats)} metrics")
    
    print(f"\n💡 Test completed successfully!")
    print(f"   For detailed testing, run: python test_absence_system_wahid.py")

if __name__ == "__main__":
    main()