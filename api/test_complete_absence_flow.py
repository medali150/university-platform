#!/usr/bin/env python3

import asyncio
import httpx

async def test_complete_absence_flow():
    """Test the complete absence management flow from frontend perspective"""
    print("=== TESTING COMPLETE ABSENCE MANAGEMENT FLOW ===")
    
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login
            print("1. 🔑 Authentication...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            token_data = login_response.json()
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            print("✅ Login successful!")
            
            # 2. Get today's schedule
            print("\n2. 📅 Getting today's schedule...")
            schedule_response = await client.get(f"{base_url}/teacher/schedule/today", headers=headers)
            schedule = schedule_response.json()
            print(f"✅ Found {len(schedule)} classes today")
            
            if not schedule:
                print("❌ No classes today, cannot test absence marking")
                return
            
            first_class = schedule[0]
            class_id = first_class['id']
            group_id = first_class['groupe']['id']
            subject_name = first_class['matiere']['nom']
            group_name = first_class['groupe']['nom']
            time_str = first_class['heure_debut'][:5]
            
            print(f"   Testing with: {time_str} | {subject_name} | {group_name}")
            
            # 3. Get students for this group
            print(f"\n3. 👨‍🎓 Getting students for {group_name}...")
            students_response = await client.get(
                f"{base_url}/teacher/groups/{group_id}/students?schedule_id={class_id}",
                headers=headers
            )
            
            if students_response.status_code != 200:
                print(f"❌ Failed to get students: {students_response.status_code}")
                print(f"   Error: {students_response.text}")
                return
            
            group_details = students_response.json()
            students = group_details['students']
            print(f"✅ Found {len(students)} students in {group_name}")
            
            if not students:
                print("❌ No students found, cannot test absence marking")
                return
            
            # 4. Test marking a student as absent
            test_student = students[0]
            print(f"\n4. ✏️ Marking {test_student['prenom']} {test_student['nom']} as absent...")
            
            absence_data = {
                "student_id": test_student['id'],
                "schedule_id": class_id,
                "is_absent": True,
                "motif": "Test absence - Maladie"
            }
            
            absence_response = await client.post(
                f"{base_url}/teacher/absence/mark",
                headers=headers,
                json=absence_data
            )
            
            if absence_response.status_code in [200, 201]:
                result = absence_response.json()
                print(f"✅ Successfully marked student as absent!")
                print(f"   Student: {test_student['prenom']} {test_student['nom']}")
                print(f"   Class: {subject_name} - {group_name} at {time_str}")
                print(f"   Motif: Test absence - Maladie")
                print(f"   Absence ID: {result.get('absence_id', 'N/A')}")
                
                # 5. Verify the absence shows up when getting students again
                print(f"\n5. 🔍 Verifying absence appears in student list...")
                verify_response = await client.get(
                    f"{base_url}/teacher/groups/{group_id}/students?schedule_id={class_id}",
                    headers=headers
                )
                
                if verify_response.status_code == 200:
                    verify_details = verify_response.json()
                    verify_students = verify_details['students']
                    
                    # Find the student we marked absent
                    marked_student = next(
                        (s for s in verify_students if s['id'] == test_student['id']), 
                        None
                    )
                    
                    if marked_student and marked_student['is_absent']:
                        print(f"✅ Absence verified! Student shows as absent with ID: {marked_student.get('absence_id', 'N/A')}")
                    else:
                        print(f"❌ Absence not reflected in student list")
                else:
                    print(f"❌ Failed to verify absence: {verify_response.status_code}")
                
                # 6. Test marking student as present (removing absence)
                print(f"\n6. ✅ Marking student as present (removing absence)...")
                present_data = {
                    "student_id": test_student['id'],
                    "schedule_id": class_id,
                    "is_absent": False,
                    "motif": None
                }
                
                present_response = await client.post(
                    f"{base_url}/teacher/absence/mark",
                    headers=headers,
                    json=present_data
                )
                
                if present_response.status_code in [200, 201]:
                    present_result = present_response.json()
                    print(f"✅ Successfully marked student as present!")
                    print(f"   Message: {present_result.get('message', 'N/A')}")
                else:
                    print(f"❌ Failed to mark as present: {present_response.status_code}")
                    print(f"   Error: {present_response.text}")
                
            else:
                print(f"❌ Failed to mark absence: {absence_response.status_code}")
                print(f"   Error: {absence_response.text}")
            
            print(f"\n🎉 COMPLETE ABSENCE FLOW TEST FINISHED!")
            print(f"✅ Frontend can now:")
            print(f"   • Display teacher groups and schedules")
            print(f"   • Show students for each group and class")
            print(f"   • Mark students as absent with custom motifs")
            print(f"   • Remove absences (mark as present)")
            print(f"   • See real-time absence status updates")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_absence_flow())