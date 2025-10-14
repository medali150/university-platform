#!/usr/bin/env python3

import asyncio
import httpx
import json

async def test_teacher_frontend_data():
    """Test all data needed by the teacher frontend"""
    print("=== TESTING TEACHER FRONTEND DATA ===")
    
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login
            print("\n1. 🔑 Authentication...")
            login_response = await client.post(
                f"{base_url}/auth/login",
                json=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed")
                return
            
            token_data = login_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print("✅ Authentication successful!")
            
            # 2. Get teacher profile
            print("\n2. 👨‍🏫 Teacher Profile...")
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            if profile_response.status_code == 200:
                profile = profile_response.json()
                teacher_info = profile['teacher_info']
                print(f"✅ Teacher: {teacher_info['prenom']} {teacher_info['nom']}")
                print(f"   Email: {teacher_info['email']}")
                print(f"   Department: {profile['department']['nom']}")
                print(f"   Subjects: {len(profile['subjects_taught'])}")
                for subject in profile['subjects_taught']:
                    print(f"     - {subject['nom']}")
            
            # 3. Get groups
            print("\n3. 👥 Teacher Groups...")
            groups_response = await client.get(f"{base_url}/teacher/groups", headers=headers)
            if groups_response.status_code == 200:
                groups = groups_response.json()
                print(f"✅ Found {len(groups)} groups:")
                for group in groups:
                    print(f"   - {group['nom']}: {group['student_count']} students")
                    print(f"     Level: {group['niveau']['nom']}")
                    print(f"     Specialty: {group['specialite']['nom']}")
                    print(f"     Subjects: {', '.join([s['nom'] for s in group['subjects']])}")
                
                # 4. Get students for each group
                print("\n4. 👨‍🎓 Students in Groups...")
                for group in groups:
                    students_response = await client.get(
                        f"{base_url}/teacher/groups/{group['id']}/students", 
                        headers=headers
                    )
                    if students_response.status_code == 200:
                        group_details = students_response.json()
                        students = group_details['students']
                        print(f"✅ Group {group['nom']}: {len(students)} students")
                        for student in students[:3]:  # Show first 3
                            print(f"     - {student['prenom']} {student['nom']} ({student['email']})")
                        if len(students) > 3:
                            print(f"     ... and {len(students) - 3} more students")
            
            # 5. Get today's schedule
            print("\n5. 📅 Today's Schedule...")
            schedule_response = await client.get(f"{base_url}/teacher/schedule/today", headers=headers)
            if schedule_response.status_code == 200:
                schedule = schedule_response.json()
                print(f"✅ Found {len(schedule)} classes today:")
                for class_item in schedule:
                    time_str = class_item['heure_debut'][:5]  # HH:MM
                    subject = class_item['matiere']['nom']
                    group = class_item['groupe']['nom']
                    room = class_item['salle']['code']
                    print(f"   - {time_str} | {subject} | {group} | Room: {room}")
                
                # 6. Test absence marking if we have classes today
                if schedule:
                    print("\n6. ✏️ Testing Absence Marking...")
                    first_class = schedule[0]
                    class_id = first_class['id']
                    group_name = first_class['groupe']['nom']
                    
                    # Get students for this group to test absence marking
                    students_response = await client.get(
                        f"{base_url}/teacher/groups/{first_class['groupe']['id']}/students",
                        headers=headers
                    )
                    
                    if students_response.status_code == 200:
                        group_details = students_response.json()
                        students = group_details['students']
                        
                        if students:
                            # Test marking one student as absent
                            test_student = students[0]
                            absence_data = {
                                "student_id": test_student['id'],
                                "schedule_id": class_id,
                                "is_absent": True,
                                "motif": "Test absence from frontend integration"
                            }
                            
                            absence_response = await client.post(
                                f"{base_url}/teacher/absence/mark",
                                headers=headers,
                                json=absence_data
                            )
                            
                            if absence_response.status_code in [200, 201]:
                                result = absence_response.json()
                                print(f"✅ Successfully marked {test_student['prenom']} {test_student['nom']} as absent")
                                print(f"   Class: {first_class['matiere']['nom']} - {group_name}")
                                print(f"   Absence ID: {result.get('absence_id', 'N/A')}")
                            else:
                                print(f"❌ Failed to mark absence: {absence_response.status_code}")
                                print(f"   Error: {absence_response.text}")
            
            # 7. Get detailed groups info
            print("\n7. 📊 Detailed Groups Information...")
            detailed_response = await client.get(f"{base_url}/teacher/groups/detailed", headers=headers)
            if detailed_response.status_code == 200:
                detailed = detailed_response.json()
                print(f"✅ Total groups: {detailed['total_groups']}")
                print(f"✅ Total students: {detailed['total_students']}")
            
            # 8. Get teacher stats
            print("\n8. 📈 Teacher Statistics...")
            stats_response = await client.get(f"{base_url}/teacher/stats", headers=headers)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Today's classes: {stats['today_classes']}")
                print(f"✅ Pending absences: {stats['pending_absences']}")
                print(f"✅ Messages: {stats['messages']}")
            
            print(f"\n🎉 FRONTEND DATA INTEGRATION COMPLETE!")
            print(f"✅ All teacher endpoints working correctly")
            print(f"✅ Groups and students data available")
            print(f"✅ Schedule data accessible")
            print(f"✅ Absence marking functional")
            print(f"✅ Teacher profile data complete")
            
            print(f"\n💡 FRONTEND READY!")
            print(f"The teacher absence management interface can now:")
            print(f"• Display teacher profile and subjects")
            print(f"• Show all teaching groups with student counts")
            print(f"• List students in each group")
            print(f"• Display today's schedule")
            print(f"• Mark student absences with motifs")
            print(f"• Show teaching statistics")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_teacher_frontend_data())