#!/usr/bin/env python3
"""
Debug and fix the subject names in Ahmed's timetable
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def debug_timetable_structure():
    """Debug the exact timetable structure to see why subjects show as Unknown"""
    
    logger.info("🔍 DEBUGGING TIMETABLE STRUCTURE")
    logger.info("=" * 60)
    
    try:
        # Login as Ahmed
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "ahmed.student@university.edu",
            "password": "student2025"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            logger.info("✅ Login successful")
            
            # Get timetable with week_offset=1 (where we have data)
            timetable_response = requests.get(f"{BASE_URL}/student/timetable?week_offset=1", headers=headers)
            if timetable_response.status_code == 200:
                data = timetable_response.json()
                
                logger.info("📊 Full API Response Structure:")
                logger.info("=" * 40)
                
                # Show basic info
                logger.info(f"Success: {data.get('success', False)}")
                logger.info(f"Student: {data.get('student_info', {}).get('name', 'Unknown')}")
                logger.info(f"Group: {data.get('student_info', {}).get('group', 'Unknown')}")
                
                # Check timetable structure
                timetable = data.get('timetable', {})
                logger.info(f"\nTimetable slots found: {len(timetable)}")
                
                # Show first few slots with detailed info
                slot_count = 0
                for slot_id, slot_data in timetable.items():
                    if slot_count >= 3:
                        break
                    
                    logger.info(f"\n📅 Slot {slot_id}:")
                    logger.info(f"   Time: {slot_data.get('time_info', {}).get('label', 'Unknown')}")
                    
                    courses = slot_data.get('courses', {})
                    logger.info(f"   Days with courses: {len([d for d, c in courses.items() if c is not None])}")
                    
                    for day, course in courses.items():
                        if course is not None:
                            logger.info(f"   📚 {day.capitalize()}:")
                            logger.info(f"      Raw course data: {course}")
                            
                            # Show all available fields
                            if isinstance(course, dict):
                                for key, value in course.items():
                                    logger.info(f"         {key}: {value}")
                            else:
                                logger.info(f"         Course is not dict: {type(course)} = {course}")
                    
                    slot_count += 1
                
                # Show sample of raw JSON for debugging
                logger.info(f"\n🔧 Sample Raw JSON:")
                logger.info("=" * 40)
                sample_data = {
                    "student_info": data.get('student_info', {}),
                    "week_info": data.get('week_info', {}),
                    "sample_slot": {}
                }
                
                # Get first slot with data
                for slot_id, slot_data in timetable.items():
                    courses = slot_data.get('courses', {})
                    for day, course in courses.items():
                        if course is not None:
                            sample_data["sample_slot"] = {
                                "slot_id": slot_id,
                                "day": day,
                                "course": course,
                                "time_info": slot_data.get('time_info', {})
                            }
                            break
                    if sample_data["sample_slot"]:
                        break
                
                logger.info(json.dumps(sample_data, indent=2, ensure_ascii=False))
                
            else:
                logger.error(f"❌ Timetable request failed: {timetable_response.status_code}")
                logger.error(f"Response: {timetable_response.text}")
        else:
            logger.error(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error in debugging: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 ANALYSIS COMPLETE")
    logger.info("Based on the output above, we can see:")
    logger.info("- The exact structure of course data")
    logger.info("- Why subjects might show as 'Unknown'")
    logger.info("- What fields are available vs missing")
    logger.info("=" * 60)

if __name__ == "__main__":
    debug_timetable_structure()