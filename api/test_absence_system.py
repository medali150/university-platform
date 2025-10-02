#!/usr/bin/env python3
"""
Test script for the teacher absence management system
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "jean.martin@university.com"  # Teacher user
TEST_PASSWORD = "password123"

def get_auth_token():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful!")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_teacher_groups(token):
    """Test getting teacher groups"""
    print("\n📚 Testing teacher groups endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ Found {len(groups)} groups")
            
            for group in groups:
                print(f"  - {group['nom']} ({group['niveau']['nom']}) - {group['student_count']} étudiants")
            
            return groups
        else:
            print(f"❌ Failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def test_group_students(token, group_id):
    """Test getting students in a group"""
    print(f"\n👥 Testing group students endpoint for group {group_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/teacher/groups/{group_id}/students", 
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            group_details = response.json()
            print(f"✅ Group: {group_details['nom']}")
            print(f"  - Level: {group_details['niveau']['nom']}")
            print(f"  - Students: {len(group_details['students'])}")
            
            for student in group_details['students']:
                status = "Absent" if student['is_absent'] else "Present"
                print(f"    • {student['prenom']} {student['nom']} - {status}")
            
            return group_details
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_today_schedule(token):
    """Test getting today's schedule"""
    print("\n📅 Testing today's schedule endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            schedules = response.json()
            print(f"✅ Found {len(schedules)} classes today")
            
            for schedule in schedules:
                start_time = datetime.fromisoformat(schedule['heure_debut'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(schedule['heure_fin'].replace('Z', '+00:00'))
                
                print(f"  - {schedule['matiere']['nom']}")
                print(f"    Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                print(f"    Group: {schedule['groupe']['nom']}")
                print(f"    Room: {schedule['salle']['code']}")
            
            return schedules
        else:
            print(f"❌ Failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def test_mark_absence(token, student_id, schedule_id):
    """Test marking student absence"""
    print(f"\n📝 Testing mark absence endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    absence_data = {
        "student_id": student_id,
        "schedule_id": schedule_id,
        "is_absent": True,
        "motif": "Test absence marking"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/teacher/absence/mark",
            headers=headers,
            json=absence_data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            if result.get('absence_id'):
                print(f"  Absence ID: {result['absence_id']}")
            return result
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Run all tests"""
    print("🚀 Testing Teacher Absence Management System")
    print("=" * 50)
    
    # Step 1: Login
    token = get_auth_token()
    if not token:
        return
    
    # Step 2: Get teacher groups
    groups = test_teacher_groups(token)
    if not groups:
        print("⚠️ No groups found, cannot continue with student tests")
        return
    
    # Step 3: Get students from first group
    first_group = groups[0]
    group_details = test_group_students(token, first_group['id'])
    
    # Step 4: Get today's schedule
    schedules = test_today_schedule(token)
    
    # Step 5: Test absence marking (if we have both students and schedule)
    if group_details and group_details['students'] and schedules:
        first_student = group_details['students'][0]
        first_schedule = schedules[0]
        
        print(f"\n🔬 Testing absence marking:")
        print(f"  Student: {first_student['prenom']} {first_student['nom']}")
        print(f"  Schedule: {first_schedule['matiere']['nom']}")
        
        test_mark_absence(token, first_student['id'], first_schedule['id'])
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")


if __name__ == "__main__":
    main()