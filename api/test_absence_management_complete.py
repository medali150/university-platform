"""
Test script for Absence Management API endpoints
"""

import asyncio
import json
from datetime import datetime, timedelta
import aiohttp

BASE_URL = "http://localhost:8000"

# Test data
TEACHER_LOGIN = {
    "email": "boubaked.mohamed@example.com",
    "password": "password123"
}

STUDENT_LOGIN = {
    "email": "student1@example.com", 
    "password": "password123"
}

DEPT_HEAD_LOGIN = {
    "email": "dept.head@example.com",
    "password": "password123"
}

async def login(session, login_data):
    """Login and get access token"""
    async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("access_token")
        else:
            text = await response.text()
            print(f"Login failed: {response.status} - {text}")
            return None

async def test_create_absence(session, token, schedule_id, student_id):
    """Test creating an absence"""
    headers = {"Authorization": f"Bearer {token}"}
    absence_data = {
        "studentId": student_id,
        "scheduleId": schedule_id,
        "reason": "Maladie - Fièvre",
        "status": "unjustified"
    }
    
    async with session.post(f"{BASE_URL}/absences/", json=absence_data, headers=headers) as response:
        data = await response.json()
        print(f"Create Absence - Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data.get("id") if response.status == 200 else None

async def test_get_absences(session, token):
    """Test getting absences"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(f"{BASE_URL}/absences/", headers=headers) as response:
        data = await response.json()
        print(f"Get Absences - Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_justify_absence(session, token, absence_id):
    """Test justifying an absence"""
    headers = {"Authorization": f"Bearer {token}"}
    justification_data = {
        "justificationText": "J'étais malade avec de la fièvre. J'ai consulté un médecin.",
        "supportingDocuments": ["medical_certificate.pdf"]
    }
    
    async with session.put(f"{BASE_URL}/absences/{absence_id}/justify", 
                          json=justification_data, headers=headers) as response:
        data = await response.json()
        print(f"Justify Absence - Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_review_absence(session, token, absence_id):
    """Test reviewing an absence"""
    headers = {"Authorization": f"Bearer {token}"}
    review_data = {
        "reviewStatus": "approved",
        "reviewNotes": "Justification acceptée - certificat médical valide."
    }
    
    async with session.put(f"{BASE_URL}/absences/{absence_id}/review", 
                          json=review_data, headers=headers) as response:
        data = await response.json()
        print(f"Review Absence - Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_statistics(session, token):
    """Test getting absence statistics"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(f"{BASE_URL}/absences/statistics", headers=headers) as response:
        data = await response.json()
        print(f"Get Statistics - Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def get_test_data(session, token):
    """Get test data for schedules and students"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get schedules
    async with session.get(f"{BASE_URL}/schedules/", headers=headers) as response:
        if response.status == 200:
            schedules_data = await response.json()
            schedules = schedules_data.get("data", [])
            print(f"Found {len(schedules)} schedules")
            if schedules:
                return schedules[0]["id"], schedules[0].get("groupId")
    
    return None, None

async def get_students_in_group(session, token, group_id):
    """Get students in a specific group"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # This endpoint might not exist yet, so we'll try to get students
    async with session.get(f"{BASE_URL}/admin/students", headers=headers) as response:
        if response.status == 200:
            students_data = await response.json()
            students = students_data.get("data", [])
            # Filter students by group if possible
            for student in students:
                if student.get("groupId") == group_id:
                    return student["id"]
            # If no match, return first student
            if students:
                return students[0]["id"]
    
    return None

async def main():
    """Main test function"""
    print("🧪 Testing Absence Management API")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # 1. Login as teacher to create absence
        print("\n1. 👨‍🏫 Login as Teacher")
        teacher_token = await login(session, TEACHER_LOGIN)
        if not teacher_token:
            print("❌ Teacher login failed")
            return
        
        # 2. Get test data (schedule and student)
        print("\n2. 📚 Getting test data...")
        schedule_id, group_id = await get_test_data(session, teacher_token)
        if not schedule_id:
            print("❌ No schedules found")
            return
        
        print(f"✅ Schedule ID: {schedule_id}")
        print(f"✅ Group ID: {group_id}")
        
        # Get a student in the group
        student_id = await get_students_in_group(session, teacher_token, group_id)
        if not student_id:
            print("❌ No students found")
            return
        
        print(f"✅ Student ID: {student_id}")
        
        # 3. Create absence
        print("\n3. ➕ Creating absence...")
        absence_id = await test_create_absence(session, teacher_token, schedule_id, student_id)
        if not absence_id:
            print("❌ Failed to create absence")
            return
        
        # 4. Login as student to justify absence
        print("\n4. 🎓 Login as Student")
        student_token = await login(session, STUDENT_LOGIN)
        if student_token:
            print("\n5. 📝 Justifying absence...")
            await test_justify_absence(session, student_token, absence_id)
        
        # 6. Login as department head to review
        print("\n6. 👔 Login as Department Head")
        dept_head_token = await login(session, DEPT_HEAD_LOGIN)
        if dept_head_token:
            print("\n7. ✅ Reviewing absence...")
            await test_review_absence(session, dept_head_token, absence_id)
            
            print("\n8. 📊 Getting statistics...")
            await test_get_statistics(session, dept_head_token)
        
        # 9. Get all absences
        print("\n9. 📋 Getting all absences...")
        await test_get_absences(session, teacher_token)
        
        print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())