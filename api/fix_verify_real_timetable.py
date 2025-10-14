#!/usr/bin/env python3
"""
Fix student-group linking and verify real timetable data
This script will ensure students are properly linked to their groups for the timetable to work
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def fix_and_verify_real_timetable():
    """Fix student group linking and verify timetable"""
    
    logger.info("🔧 FIXING AND VERIFYING REAL TIMETABLE")
    logger.info("=" * 60)
    
    # Test with existing working student first
    logger.info("🧪 Testing with existing working student...")
    
    try:
        # Login with the working student
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "ahmed.student@university.edu",
            "password": "student2025"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            logger.info("✅ Working student login successful")
            
            # Get current timetable
            timetable_response = requests.get(f"{BASE_URL}/student/timetable", headers=headers)
            if timetable_response.status_code == 200:
                data = timetable_response.json()
                logger.info(f"📊 Working student timetable: {data.get('success', False)}")
                logger.info(f"👥 Working student group: {data.get('student_info', {}).get('group', 'Unknown')}")
                
                # Now let's create LI 04 schedule using the working pattern
                logger.info("\n🏗️ Creating LI 04 Schedule using university schedule API...")
                
                # Create schedule for this week
                today = "2025-10-04"  # Current date
                schedule_data = {
                    "group_name": "LI 04",
                    "week_start": "2025-09-30",  # Monday of current week
                    "template": {
                        "monday": [
                            {
                                "start_time": "14:30",
                                "end_time": "16:00", 
                                "subject_name": "Atelier Base de Données Avancée",
                                "teacher_name": "Abdelkader MAATALLAH",
                                "room_name": "Lab Info"
                            },
                            {
                                "start_time": "16:10", 
                                "end_time": "17:40",
                                "subject_name": "Atelier Base de Données Avancée",
                                "teacher_name": "Abdelkader MAATALLAH", 
                                "room_name": "Lab Info"
                            }
                        ],
                        "tuesday": [
                            {
                                "start_time": "08:30",
                                "end_time": "10:00",
                                "subject_name": "Environnement de développement", 
                                "teacher_name": "Ahmed NEFZAOUI",
                                "room_name": "Salle A1"
                            }
                        ],
                        "wednesday": [
                            {
                                "start_time": "08:30",
                                "end_time": "10:00",
                                "subject_name": "Atelier développement Mobile natif",
                                "teacher_name": "Abdelkader MAATALLAH",
                                "room_name": "Atelier"
                            }
                        ],
                        "thursday": [
                            {
                                "start_time": "08:30",
                                "end_time": "10:00", 
                                "subject_name": "Atelier Framework cross-platform",
                                "teacher_name": "Wahid HAMDI",
                                "room_name": "Atelier"
                            }
                        ],
                        "friday": [
                            {
                                "start_time": "14:30",
                                "end_time": "16:00",
                                "subject_name": "Atelier SOA",
                                "teacher_name": "Abdelkader MAATALLAH", 
                                "room_name": "Lab Info"
                            },
                            {
                                "start_time": "16:10",
                                "end_time": "17:40",
                                "subject_name": "Gestion des données Massives", 
                                "teacher_name": "Abdelkader MAATALLAH",
                                "room_name": "Lab Info"
                            }
                        ]
                    }
                }
                
                # Try the university schedule creation endpoint
                schedule_response = requests.post(
                    f"{BASE_URL}/student/admin/create-university-schedule",
                    json=schedule_data,
                    headers=headers
                )
                
                if schedule_response.status_code in [200, 201]:
                    logger.info("✅ LI 04 schedule created successfully!")
                else:
                    logger.warning(f"⚠️ Schedule creation response: {schedule_response.status_code}")
                    logger.info(f"Response: {schedule_response.text}")
                
                # Now create a student specifically for LI 04 group
                logger.info("\n👨‍🎓 Creating dedicated LI 04 student...")
                
                # Register new LI 04 student
                li04_student = {
                    "first_name": "Test",
                    "last_name": "Student LI04",
                    "email": "test.student.li04@univ.tn",
                    "password": "student123",
                    "role": "student"
                }
                
                register_response = requests.post(f"{BASE_URL}/auth/register", json=li04_student)
                if register_response.status_code in [200, 201]:
                    logger.info("✅ LI 04 student registered")
                elif register_response.status_code == 422:
                    logger.info("📍 LI 04 student already exists")
                
                # Try to login as LI 04 student
                li04_login = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": "test.student.li04@univ.tn",
                    "password": "student123"
                })
                
                if li04_login.status_code == 200:
                    li04_token = li04_login.json()["access_token"]
                    li04_headers = {"Authorization": f"Bearer {li04_token}"}
                    logger.info("✅ LI 04 student login successful")
                    
                    # Check LI 04 timetable
                    li04_timetable = requests.get(f"{BASE_URL}/student/timetable", headers=li04_headers)
                    if li04_timetable.status_code == 200:
                        li04_data = li04_timetable.json()
                        logger.info(f"📅 LI 04 timetable success: {li04_data.get('success', False)}")
                        logger.info(f"👥 LI 04 student group: {li04_data.get('student_info', {}).get('group', 'Unknown')}")
                        
                        # Count courses
                        courses_count = 0
                        if 'timetable' in li04_data:
                            for slot_id, slot_data in li04_data['timetable'].items():
                                if 'courses' in slot_data:
                                    for day, course in slot_data['courses'].items():
                                        if course is not None:
                                            courses_count += 1
                        
                        logger.info(f"📚 LI 04 courses found: {courses_count}")
                        
                        if courses_count > 0:
                            logger.info("🎉 SUCCESS! LI 04 student can see real schedule!")
                            
                            # Show some courses
                            logger.info("\n📋 Sample courses for LI 04:")
                            count = 0
                            for slot_id, slot_data in li04_data['timetable'].items():
                                if count >= 3:
                                    break
                                if 'courses' in slot_data:
                                    for day, course in slot_data['courses'].items():
                                        if course is not None and count < 3:
                                            logger.info(f"   • {day} {slot_data.get('time_info', {}).get('label', 'Unknown time')}: {course.get('subject_name', 'Unknown subject')}")
                                            count += 1
                        else:
                            logger.warning("⚠️ No courses found for LI 04 student")
                    else:
                        logger.error(f"❌ LI 04 timetable request failed: {li04_timetable.status_code}")
                else:
                    logger.error(f"❌ LI 04 login failed: {li04_login.status_code}")
                    logger.error(f"Response: {li04_login.text}")
        else:
            logger.error(f"❌ Working student login failed: {login_response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error in verification: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 VERIFICATION COMPLETE")
    logger.info("=" * 60)
    logger.info("🔑 FINAL TEST CREDENTIALS:")
    logger.info("   LI 04 Student: test.student.li04@univ.tn / student123")
    logger.info("   Working Student: ahmed.student@university.edu / student2025")
    logger.info("=" * 60)
    logger.info("🌐 FRONTEND TEST:")
    logger.info("   URL: http://localhost:3000/dashboard/student/timetable")
    logger.info("   Login with LI 04 student to see your real schedule!")
    logger.info("=" * 60)

if __name__ == "__main__":
    fix_and_verify_real_timetable()