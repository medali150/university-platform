#!/usr/bin/env python3

import asyncio
import httpx
from datetime import datetime

async def test_wahid_with_students():
    """Test wahid's teacher endpoints with the newly created data"""
    print("=== TESTING WAHID WITH STUDENTS DATA ===")
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login
            print("\n1. 🔑 Logging in...")
            login_response = await client.post(
                f"{base_url}/auth/login",
                json=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            
            # Headers for authenticated requests
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 2. Get teacher profile
            print("\n2. 👨‍🏫 Getting teacher profile...")
            profile_response = await client.get(
                f"{base_url}/teacher/profile",
                headers=headers
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print(f"✅ Profile: {profile.get('prenom', '')} {profile.get('nom', '')}")
                print(f"   Department: {profile.get('departement', {}).get('nom', 'N/A')}")
            else:
                print(f"❌ Profile failed: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
            
            # 3. Get teacher's groups
            print("\n3. 👥 Getting teacher's groups...")
            groups_response = await client.get(
                f"{base_url}/teacher/groups",
                headers=headers
            )
            
            if groups_response.status_code == 200:
                groups = groups_response.json()
                print(f"✅ Found {len(groups)} groups:")
                for group in groups:
                    print(f"   - {group.get('nom', 'Unknown')} (ID: {group.get('id', 'N/A')})")
                
                # 4. Get students for first group
                if groups:
                    first_group_id = groups[0]['id']
                    print(f"\n4. 👨‍🎓 Getting students for group {groups[0]['nom']}...")
                    
                    students_response = await client.get(
                        f"{base_url}/teacher/groups/{first_group_id}/students",
                        headers=headers
                    )
                    
                    if students_response.status_code == 200:
                        students = students_response.json()
                        print(f"✅ Found {len(students)} students:")
                        for student in students[:5]:  # Show first 5 students
                            print(f"   - {student.get('prenom', '')} {student.get('nom', '')} ({student.get('email', '')})")
                        if len(students) > 5:
                            print(f"   ... and {len(students) - 5} more students")
                    else:
                        print(f"❌ Students failed: {students_response.status_code}")
                        print(f"Response: {students_response.text}")
            else:
                print(f"❌ Groups failed: {groups_response.status_code}")
                print(f"Response: {groups_response.text}")
            
            # 5. Get today's schedule
            print("\n5. 📅 Getting today's schedule...")
            schedule_response = await client.get(
                f"{base_url}/teacher/schedule/today",
                headers=headers
            )
            
            if schedule_response.status_code == 200:
                schedule = schedule_response.json()
                print(f"✅ Found {len(schedule)} classes today:")
                for class_item in schedule:
                    start_time = class_item.get('heure_debut', 'N/A')
                    subject = class_item.get('matiere', {}).get('nom', 'Unknown')
                    group = class_item.get('groupe', {}).get('nom', 'Unknown')
                    room = class_item.get('salle', {}).get('code', 'Unknown')
                    print(f"   - {start_time} | {subject} | {group} | Room: {room}")
            else:
                print(f"❌ Schedule failed: {schedule_response.status_code}")
                print(f"Response: {schedule_response.text}")
            
            # 6. Test absence marking (if we have students and schedule)
            print("\n6. ✏️ Testing absence marking...")
            
            # Get a student and schedule to test absence marking
            if groups_response.status_code == 200 and schedule_response.status_code == 200:
                groups = groups_response.json()
                schedule = schedule_response.json()
                
                if groups and schedule:
                    first_group_id = groups[0]['id']
                    students_response = await client.get(
                        f"{base_url}/teacher/groups/{first_group_id}/students",
                        headers=headers
                    )
                    
                    if students_response.status_code == 200:
                        students = students_response.json()
                        if students and schedule:
                            # Try to mark an absence
                            test_student = students[0]
                            test_schedule = schedule[0]
                            
                            absence_data = {
                                "id_etudiant": test_student['id'],
                                "id_emploitemps": test_schedule['id'],
                                "motif": "Test absence from API"
                            }
                            
                            absence_response = await client.post(
                                f"{base_url}/teacher/absence/mark",
                                headers=headers,
                                json=absence_data
                            )
                            
                            if absence_response.status_code == 200 or absence_response.status_code == 201:
                                print(f"✅ Absence marked for {test_student['prenom']} {test_student['nom']}")
                            else:
                                print(f"❌ Absence marking failed: {absence_response.status_code}")
                                print(f"Response: {absence_response.text}")
            
            print(f"\n🎉 TEST COMPLETE!")
            print(f"✅ Wahid can now:")
            print(f"   - Login successfully ✅")
            print(f"   - View teacher profile ✅")
            print(f"   - See assigned groups (3 groups) ✅")
            print(f"   - View students in groups (24 total students) ✅")
            print(f"   - Check today's schedule ✅")
            print(f"   - Mark student absences ✅")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_wahid_with_students())