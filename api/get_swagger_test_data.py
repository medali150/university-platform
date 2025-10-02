"""
Get Real Student and Schedule IDs for Testing Absence Creation
This script gets actual IDs from the database for Swagger testing
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

# Teacher credentials
TEACHER_CREDENTIALS = {
    "login": "souhir",
    "password": "daligh15"
}

async def get_test_data_for_swagger():
    """Get real student and schedule IDs for Swagger testing"""
    print("🔍 Getting Test Data for Swagger UI")
    print("=" * 50)
    
    # Get teacher token
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(f"{BASE_URL}/auth/login", json=TEACHER_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Failed to authenticate: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        auth_data = response.json()
        print(f"✅ Authentication successful!")
        print(f"User: {auth_data['user']['firstName']} {auth_data['user']['lastName']}")
        print(f"Role: {auth_data['user']['role']}")
        
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get teacher schedules
        response = await client.get(f"{BASE_URL}/admin/teachers/teacher/absences/my-schedules", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get schedules: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        schedules = response.json()
        if not schedules:
            print("❌ No schedules found")
            return
        
        schedule = schedules[0]
        schedule_id = schedule["id"]
        
        print(f"✅ Found Schedule:")
        print(f"   ID: {schedule_id}")
        print(f"   Subject: {schedule['subject']['name']}")
        print(f"   Date: {schedule['date']}")
        print(f"   Time: {schedule['startTime']} - {schedule['endTime']}")
        
        # Get students for this schedule
        response = await client.get(f"{BASE_URL}/admin/teachers/teacher/absences/schedule/{schedule_id}/students", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get students: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        students = response.json()
        print(f"📊 Students found: {len(students)}")
        
        if not students:
            print("❌ No students found in this schedule")
            print("This might be because:")
            print("   - The group has no enrolled students")
            print("   - Student records are not properly set up")
            print("   - Group-student associations are missing")
            return
        
        student = students[0]
        student_id = student["id"]
        
        print(f"\n✅ Found Student:")
        print(f"   ID: {student_id}")
        print(f"   Name: {student['user']['firstName']} {student['user']['lastName']}")
        print(f"   Email: {student['user']['email']}")
        print(f"   Enrollment: {student['enrollmentNumber']}")
        
        # Create the proper JSON payload
        test_payload = {
            "studentId": student_id,
            "scheduleId": schedule_id,
            "reason": "Student was absent during class attendance",
            "notes": "Marked during attendance check"
        }
        
        print(f"\n📋 CORRECT JSON PAYLOAD FOR SWAGGER:")
        print("=" * 50)
        print("Copy and paste this into Swagger UI for testing:")
        print()
        print(json.dumps(test_payload, indent=2))
        print()
        print("=" * 50)
        
        # Also show the minimal version
        minimal_payload = {
            "studentId": student_id,
            "scheduleId": schedule_id,
            "reason": "Student absent"
        }
        
        print(f"\n📋 MINIMAL JSON PAYLOAD (also works):")
        print("=" * 50)
        print(json.dumps(minimal_payload, indent=2))
        print("=" * 50)
        
        return test_payload

if __name__ == "__main__":
    asyncio.run(get_test_data_for_swagger())