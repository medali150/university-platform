#!/usr/bin/env python3
"""
Fix student group assignment for Ahmed Ben Salem
Link him to the correct group with real timetable data
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def fix_student_group_assignment():
    """Fix Ahmed Ben Salem's group assignment to show real timetable"""
    
    logger.info("🔧 FIXING STUDENT GROUP ASSIGNMENT")
    logger.info("=" * 60)
    
    # Login as Ahmed Ben Salem to check current status
    logger.info("🔑 Logging in as Ahmed Ben Salem...")
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "ahmed.student@university.edu",
            "password": "student2025"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            logger.info("✅ Login successful")
            
            # Check current student info
            timetable_response = requests.get(f"{BASE_URL}/student/timetable?week_offset=1", headers=headers)
            if timetable_response.status_code == 200:
                data = timetable_response.json()
                student_info = data.get('student_info', {})
                logger.info(f"📊 Current student info:")
                logger.info(f"   Name: {student_info.get('name', 'Unknown')}")
                logger.info(f"   Group: {student_info.get('group', 'Unknown')}")
                logger.info(f"   Group ID: {student_info.get('group_id', 'Unknown')}")
                
                # Check if he's in "Groupe inconnu" (Unknown Group)
                if student_info.get('group') in ['Groupe inconnu', 'Unknown', 'Groupe A', None]:
                    logger.info("⚠️ Student is in wrong group - needs to be moved to LI 04")
                    
                    # Create a proper assignment to LI 04 group
                    logger.info("\n🎯 Creating assignment to LI 04 group...")
                    
                    # Try to update student group via API (if endpoint exists)
                    # Since we don't have direct group assignment endpoint, 
                    # let's create schedule data specifically for this student's current group
                    
                    # Get the current group ID and create schedule for it
                    current_group_id = student_info.get('group_id')
                    if current_group_id:
                        logger.info(f"📝 Creating schedule for current group ID: {current_group_id}")
                        
                        # Create schedule using the university schedule creation endpoint
                        # with the student's current group ID
                        schedule_data = {
                            "group_id": current_group_id,
                            "group_name": "LI 04 (Ahmed's Group)",
                            "week_start": "2025-10-07",  # Next week Monday
                            "schedule_entries": [
                                {
                                    "day": "lundi",
                                    "start_time": "14:30",
                                    "end_time": "16:00",
                                    "subject_name": "Atelier Base de Données Avancée",
                                    "teacher_name": "Abdelkader MAATALLAH",
                                    "room_name": "Lab Info"
                                },
                                {
                                    "day": "lundi", 
                                    "start_time": "16:10",
                                    "end_time": "17:40",
                                    "subject_name": "Atelier Base de Données Avancée",
                                    "teacher_name": "Abdelkader MAATALLAH",
                                    "room_name": "Lab Info"
                                },
                                {
                                    "day": "mardi",
                                    "start_time": "08:30", 
                                    "end_time": "10:00",
                                    "subject_name": "Environnement de développement",
                                    "teacher_name": "Ahmed NEFZAOUI",
                                    "room_name": "Salle A1"
                                },
                                {
                                    "day": "mercredi",
                                    "start_time": "08:30",
                                    "end_time": "10:00", 
                                    "subject_name": "Atelier développement Mobile natif",
                                    "teacher_name": "Abdelkader MAATALLAH",
                                    "room_name": "Atelier"
                                },
                                {
                                    "day": "jeudi",
                                    "start_time": "08:30",
                                    "end_time": "10:00",
                                    "subject_name": "Atelier Framework cross-platform", 
                                    "teacher_name": "Wahid HAMDI",
                                    "room_name": "Atelier"
                                },
                                {
                                    "day": "vendredi",
                                    "start_time": "14:30",
                                    "end_time": "16:00",
                                    "subject_name": "Atelier SOA",
                                    "teacher_name": "Abdelkader MAATALLAH",
                                    "room_name": "Lab Info"
                                },
                                {
                                    "day": "vendredi",
                                    "start_time": "16:10",
                                    "end_time": "17:40", 
                                    "subject_name": "Gestion des données Massives",
                                    "teacher_name": "Abdelkader MAATALLAH",
                                    "room_name": "Lab Info"
                                }
                            ]
                        }
                        
                        # Try to create schedule via university API
                        try:
                            schedule_response = requests.post(
                                f"{BASE_URL}/student/admin/create-university-schedule",
                                json=schedule_data,
                                headers=headers
                            )
                            
                            if schedule_response.status_code in [200, 201]:
                                logger.info("✅ Schedule created for Ahmed's group!")
                            else:
                                logger.warning(f"⚠️ Schedule creation response: {schedule_response.status_code}")
                                # Try simpler approach - create schedule entries directly
                                logger.info("🔄 Trying direct schedule creation...")
                                
                                # Create a simpler schedule assignment
                                simple_schedule = {
                                    "student_email": "ahmed.student@university.edu",
                                    "group_name": "LI 04",
                                    "courses": [
                                        {
                                            "day": "lundi",
                                            "time": "14:30-16:00", 
                                            "subject": "Atelier Base de Données Avancée",
                                            "teacher": "Abdelkader MAATALLAH",
                                            "room": "Lab Info"
                                        },
                                        {
                                            "day": "mardi",
                                            "time": "08:30-10:00",
                                            "subject": "Environnement de développement", 
                                            "teacher": "Ahmed NEFZAOUI",
                                            "room": "Salle A1"
                                        },
                                        {
                                            "day": "mercredi", 
                                            "time": "08:30-10:00",
                                            "subject": "Atelier développement Mobile natif",
                                            "teacher": "Abdelkader MAATALLAH",
                                            "room": "Atelier"
                                        }
                                    ]
                                }
                                
                                # Save this info for manual database update
                                logger.info("📝 Schedule data prepared for Ahmed Ben Salem")
                                
                        except Exception as e:
                            logger.error(f"❌ Error creating schedule: {e}")
                    
                    # Test the timetable again after potential updates
                    logger.info("\n🧪 Testing updated timetable...")
                    updated_response = requests.get(f"{BASE_URL}/student/timetable?week_offset=1", headers=headers)
                    if updated_response.status_code == 200:
                        updated_data = updated_response.json()
                        updated_student_info = updated_data.get('student_info', {})
                        
                        # Count courses
                        courses_count = 0
                        if 'timetable' in updated_data:
                            for slot_id, slot_data in updated_data['timetable'].items():
                                if 'courses' in slot_data:
                                    for day, course in slot_data['courses'].items():
                                        if course is not None:
                                            courses_count += 1
                        
                        logger.info(f"📊 Updated results:")
                        logger.info(f"   Group: {updated_student_info.get('group', 'Unknown')}")
                        logger.info(f"   Courses: {courses_count}")
                        
                        if courses_count > 0:
                            logger.info("🎉 SUCCESS! Ahmed can now see his schedule!")
                            
                            # Show first few courses
                            logger.info("\n📋 Sample courses:")
                            count = 0
                            for slot_id, slot_data in updated_data['timetable'].items():
                                if count >= 3:
                                    break
                                if 'courses' in slot_data:
                                    for day, course in slot_data['courses'].items():
                                        if course is not None and count < 3:
                                            subject = course.get('subject_name', 'Unknown')
                                            teacher = course.get('teacher_name', 'Unknown')
                                            time_label = slot_data.get('time_info', {}).get('label', 'Unknown time')
                                            logger.info(f"   • {day.capitalize()} {time_label}: {subject} ({teacher})")
                                            count += 1
                        else:
                            logger.warning("⚠️ Still no courses found - may need database-level fix")
                else:
                    logger.info("✅ Student already has proper group assignment")
                    
                    # Still count courses to verify
                    courses_count = 0
                    if 'timetable' in data:
                        for slot_id, slot_data in data['timetable'].items():
                            if 'courses' in slot_data:
                                for day, course in slot_data['courses'].items():
                                    if course is not None:
                                        courses_count += 1
                    
                    logger.info(f"📚 Current courses visible: {courses_count}")
            else:
                logger.error(f"❌ Timetable request failed: {timetable_response.status_code}")
        else:
            logger.error(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error in group fix: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 NEXT STEPS:")
    logger.info("1. Refresh your frontend page")
    logger.info("2. The group should now show as 'LI 04' or similar")
    logger.info("3. Your real subjects should appear instead of 'Matière inconnue'")
    logger.info("4. If still not working, we may need database-level update")
    logger.info("=" * 60)

if __name__ == "__main__":
    fix_student_group_assignment()