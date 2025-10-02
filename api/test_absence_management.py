"""
Comprehensive Test Script for Teacher Absence Management System
Tests all the new absence-related endpoints with proper authentication
"""
import asyncio
import httpx
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000"

# Test credentials
TEACHER_CREDENTIALS = {
    "email": "dali.boubaker@university.edu",
    "password": "dali123"
}

async def get_teacher_token():
    """Get authentication token for teacher"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json=TEACHER_CREDENTIALS
        )
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Failed to authenticate teacher: {response.status_code}")
            print(response.text)
            return None

async def test_get_teacher_schedules(token):
    """Test getting teacher's schedules for absence marking"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/admin/teachers/teacher/absences/my-schedules",
            headers=headers
        )
        
        print("\n📅 GET Teacher Schedules:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} schedules")
            if data:
                print("First schedule:")
                print(json.dumps(data[0], indent=2, default=str))
                return data[0]["id"]  # Return first schedule ID for further tests
        else:
            print(f"❌ Error: {response.text}")
            
        return None

async def test_get_schedule_students(token, schedule_id):
    """Test getting students in a specific schedule"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/admin/teachers/teacher/absences/schedule/{schedule_id}/students",
            headers=headers
        )
        
        print(f"\n👥 GET Students for Schedule {schedule_id}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} students")
            if data:
                print("First student:")
                print(json.dumps(data[0], indent=2, default=str))
                return data[0]["id"]  # Return first student ID for further tests
        else:
            print(f"❌ Error: {response.text}")
            
        return None

async def test_mark_student_absence(token, schedule_id, student_id):
    """Test marking a student as absent"""
    headers = {"Authorization": f"Bearer {token}"}
    
    absence_data = {
        "studentId": student_id,
        "scheduleId": schedule_id,
        "reason": "Student was not present during class",
        "notes": "Marked during attendance check"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/admin/teachers/teacher/absences/",
            headers=headers,
            json=absence_data
        )
        
        print(f"\n📝 POST Mark Student Absence:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Absence marked successfully!")
            print(json.dumps(data, indent=2, default=str))
            return data["id"]  # Return absence ID for further tests
        else:
            print(f"❌ Error: {response.text}")
            
        return None

async def test_get_student_absences(token, student_id):
    """Test getting all absences for a specific student"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/admin/teachers/teacher/absences/student/{student_id}",
            headers=headers
        )
        
        print(f"\n📋 GET Student Absences for Student {student_id}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} absences for student")
            if data:
                print("First absence:")
                print(json.dumps(data[0], indent=2, default=str))
        else:
            print(f"❌ Error: {response.text}")

async def test_update_absence(token, absence_id):
    """Test updating an absence record"""
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "reason": "Student was sick - updated reason",
        "notes": "Updated with more detailed information",
        "status": "JUSTIFIED"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/admin/teachers/teacher/absences/{absence_id}",
            headers=headers,
            json=update_data
        )
        
        print(f"\n✏️ PUT Update Absence {absence_id}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Absence updated successfully!")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Error: {response.text}")

async def test_get_absence_statistics(token, student_id):
    """Test getting absence statistics for a student"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/admin/teachers/teacher/absences/student/{student_id}/statistics",
            headers=headers
        )
        
        print(f"\n📊 GET Absence Statistics for Student {student_id}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics retrieved successfully!")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Error: {response.text}")

async def test_delete_absence(token, absence_id):
    """Test deleting an absence record"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/admin/teachers/teacher/absences/{absence_id}",
            headers=headers
        )
        
        print(f"\n🗑️ DELETE Absence {absence_id}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Absence deleted successfully!")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Error: {response.text}")

async def main():
    """Run all absence management tests"""
    print("🧪 Starting Teacher Absence Management Tests")
    print("=" * 50)
    
    # Step 1: Authenticate
    token = await get_teacher_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print(f"✅ Teacher authenticated successfully")
    
    # Step 2: Get teacher's schedules
    schedule_id = await test_get_teacher_schedules(token)
    if not schedule_id:
        print("❌ No schedules found, cannot proceed with absence tests")
        return
    
    # Step 3: Get students for the schedule
    student_id = await test_get_schedule_students(token, schedule_id)
    if not student_id:
        print("❌ No students found in schedule, cannot proceed with absence tests")
        return
    
    # Step 4: Mark student absence
    absence_id = await test_mark_student_absence(token, schedule_id, student_id)
    if not absence_id:
        print("❌ Failed to mark absence, skipping remaining tests")
        return
    
    # Step 5: Get student's absences
    await test_get_student_absences(token, student_id)
    
    # Step 6: Update the absence
    await test_update_absence(token, absence_id)
    
    # Step 7: Get absence statistics
    await test_get_absence_statistics(token, student_id)
    
    # Step 8: Clean up - delete the test absence
    await test_delete_absence(token, absence_id)
    
    print("\n" + "=" * 50)
    print("🎉 All absence management tests completed!")

if __name__ == "__main__":
    asyncio.run(main())