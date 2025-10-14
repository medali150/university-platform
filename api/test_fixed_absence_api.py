#!/usr/bin/env python3
"""
Test the fixed absence marking API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test account credentials
TEACHER_CREDS = {
    "email": "wahid@gmail.com",
    "password": "dalighgh15"
}

def test_absence_marking_api():
    """Test the absence marking API after fixing the notification service"""
    
    print("🧪 TESTING FIXED ABSENCE MARKING API")
    print("=" * 50)
    
    try:
        # Step 1: Login as teacher
        print("1️⃣ Teacher Login")
        login_response = requests.post(f"{BASE_URL}/auth/login", json=TEACHER_CREDS)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print("✅ Teacher login successful")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        # Step 2: Get teacher groups
        print("\n2️⃣ Getting Teacher Groups")
        headers = {"Authorization": f"Bearer {token}"}
        groups_response = requests.get(f"{BASE_URL}/teacher/groups", headers=headers)
        
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"✅ Found {len(groups)} groups")
            
            if not groups:
                print("❌ No groups found")
                return False
                
            group = groups[0]
            group_id = group["id"]
            print(f"📋 Using group: {group['nom']} (ID: {group_id})")
        else:
            print(f"❌ Groups request failed: {groups_response.status_code}")
            return False
        
        # Step 3: Get students in the group
        print("\n3️⃣ Getting Students in Group")
        students_response = requests.get(f"{BASE_URL}/teacher/groups/{group_id}/students", headers=headers)
        
        if students_response.status_code == 200:
            group_details = students_response.json()
            students = group_details.get("students", [])
            print(f"✅ Found {len(students)} students")
            
            if not students:
                print("❌ No students found in group")
                return False
                
            student = students[0]
            print(f"👨‍🎓 Using student: {student['prenom']} {student['nom']} (ID: {student['id']})")
        else:
            print(f"❌ Students request failed: {students_response.status_code}")
            return False
        
        # Step 4: Get teacher schedules to find a valid schedule_id
        print("\n4️⃣ Getting Teacher Schedule")
        schedule_response = requests.get(f"{BASE_URL}/teacher/schedule", headers=headers)
        
        if schedule_response.status_code == 200:
            schedules = schedule_response.json()
            print(f"✅ Found {len(schedules)} schedule entries")
            
            if not schedules:
                print("❌ No schedules found")
                return False
                
            # Find a schedule for our group
            group_schedule = None
            for schedule in schedules:
                if schedule.get("groupe", {}).get("id") == group_id:
                    group_schedule = schedule
                    break
            
            if not group_schedule:
                print("❌ No schedule found for this group")
                return False
                
            schedule_id = group_schedule["id"]
            print(f"📅 Using schedule: {group_schedule.get('matiere', {}).get('nom_matiere', 'Unknown')} (ID: {schedule_id})")
        else:
            print(f"❌ Schedule request failed: {schedule_response.status_code}")
            return False
        
        # Step 5: Test marking absence
        print("\n5️⃣ Testing Absence Marking")
        absence_payload = {
            "student_id": student["id"],
            "schedule_id": schedule_id,
            "is_absent": True,
            "motif": "Test absence for notification system"
        }
        
        print("📝 Marking absence with payload:")
        print(json.dumps(absence_payload, indent=2))
        
        absence_response = requests.post(
            f"{BASE_URL}/teacher/absence/mark",
            json=absence_payload,
            headers=headers
        )
        
        if absence_response.status_code == 200:
            result = absence_response.json()
            print("✅ Absence marked successfully!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Check if notification was sent (look for success response)
            if result.get("success"):
                print("🔔 Absence marking completed successfully")
                print("👀 Check server console for notification logs!")
                return True
            else:
                print("⚠️ Absence marking returned success=False")
                return False
        else:
            print(f"❌ Absence marking failed: {absence_response.status_code}")
            print(f"Error: {absence_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_absence_marking_api()
    if success:
        print("\n🎉 Absence marking API test completed successfully!")
        print("🔔 Check the server console for notification service logs!")
    else:
        print("\n❌ Absence marking API test failed.")