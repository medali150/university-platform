"""
Debug the absence creation endpoint step by step
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"
CREDENTIALS = {"login": "souhir", "password": "daligh15"}

async def debug_absence_creation():
    """Debug each step of absence creation"""
    print("🔍 Debugging Absence Creation Step by Step")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Authenticate
        print("1️⃣ Authentication...")
        response = await client.post(f"{BASE_URL}/auth/login", json=CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Auth failed: {response.status_code} - {response.text}")
            return
        
        auth_data = response.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Authenticated as: {auth_data['user']['firstName']} {auth_data['user']['lastName']}")
        
        # Step 2: Get schedules
        print("\n2️⃣ Getting teacher schedules...")
        response = await client.get(f"{BASE_URL}/admin/teachers/teacher/absences/my-schedules", headers=headers)
        if response.status_code != 200:
            print(f"❌ Schedules failed: {response.status_code} - {response.text}")
            return
        
        schedules = response.json()
        print(f"✅ Found {len(schedules)} schedules")
        if not schedules:
            print("❌ No schedules available")
            return
        
        schedule = schedules[0]
        schedule_id = schedule["id"]
        print(f"   Using schedule: {schedule_id}")
        print(f"   Subject: {schedule['subject']['name']}")
        
        # Step 3: Get students
        print("\n3️⃣ Getting students for schedule...")
        response = await client.get(f"{BASE_URL}/admin/teachers/teacher/absences/schedule/{schedule_id}/students", headers=headers)
        if response.status_code != 200:
            print(f"❌ Students failed: {response.status_code} - {response.text}")
            return
        
        response_data = response.json()
        print(f"✅ Response received")
        print(f"Response keys: {list(response_data.keys())}")
        
        # Extract students from the response
        students = response_data.get("students", [])
        print(f"✅ Found {len(students)} students")
        
        if not students:
            print("❌ No students available")
            return
        
        student = students[0]
        student_id = student["id"]
        print(f"   Using student: {student_id}")
        print(f"   Name: {student['user']['firstName']} {student['user']['lastName']}")
        
        # Step 4: Create absence (the failing step)
        print("\n4️⃣ Creating absence...")
        absence_data = {
            "studentId": student_id,
            "scheduleId": schedule_id,
            "reason": "Student was absent during class attendance"
        }
        
        print("Sending payload:")
        print(json.dumps(absence_data, indent=2))
        
        response = await client.post(
            f"{BASE_URL}/admin/teachers/teacher/absences/",
            headers=headers,
            json=absence_data
        )
        
        print(f"\nResponse: {response.status_code}")
        print(f"Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Absence created successfully!")
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print("❌ Absence creation failed")
            
            # Let's check if the student and schedule actually exist
            print("\n🔍 Verifying student and schedule exist...")
            
            # Check student directly via Prisma query
            print(f"\n5️⃣ Direct database verification needed...")
            print(f"   Student ID to verify: {student_id}")
            print(f"   Schedule ID to verify: {schedule_id}")

if __name__ == "__main__":
    asyncio.run(debug_absence_creation())