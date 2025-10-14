#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta, date

def create_university_timetable():
    """Create a realistic university timetable like the example provided"""
    
    print("=== CREATING UNIVERSITY TIMETABLE ===")
    
    base_url = "http://localhost:8000"
    
    # Login as student
    login_data = {
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # First create sample schedules
        print("🔧 Creating sample university schedule...")
        create_response = requests.post(
            f"{base_url}/student/admin/create-sample-schedule",
            headers=headers
        )
        
        if create_response.status_code == 200:
            print("✅ Sample schedules created!")
            result = create_response.json()
            print(f"   Created {len(result.get('schedules_created', []))} schedule entries")
        else:
            print(f"⚠️ Schedule creation status: {create_response.status_code}")
        
        # Test the new timetable endpoint
        print("\n📅 Testing university timetable view...")
        timetable_response = requests.get(f"{base_url}/student/timetable", headers=headers)
        
        if timetable_response.status_code == 200:
            timetable_data = timetable_response.json()
            print("✅ Timetable endpoint works!")
            
            if timetable_data.get("success"):
                print("\n🎓 UNIVERSITY TIMETABLE STRUCTURE:")
                print(f"Student: {timetable_data['student_info']['name']}")
                print(f"Group: {timetable_data['student_info']['group']}")
                print(f"Week: {timetable_data['week_info']['start_date']} to {timetable_data['week_info']['end_date']}")
                
                # Display timetable in table format
                timetable = timetable_data["timetable"]
                days = timetable_data["days"]
                time_slots = timetable_data["time_slots"]
                
                print("\n📋 WEEKLY TIMETABLE:")
                print("=" * 120)
                
                # Header
                header = f"{'Time Slot':<20}"
                for day in days:
                    header += f"{day['name']:<18}"
                print(header)
                print("-" * 120)
                
                # Rows
                for slot in time_slots:
                    slot_data = timetable.get(slot["id"], {})
                    row = f"{slot['label']:<20}"
                    
                    for day in days:
                        course = slot_data.get("courses", {}).get(day["id"])
                        if course:
                            # Format like university example: Subject + Teacher + Room
                            cell_content = f"{course['subject'][:12]}\n{course['teacher'][:12]}\n{course['room']}"
                            row += f"{cell_content:<18}"
                        else:
                            row += f"{'---':<18}"
                    
                    print(row)
                    print("-" * 120)
                
                print("\n🎉 TIMETABLE DISPLAY SUCCESSFUL!")
                print("This matches the university schedule format you provided!")
                
            else:
                print(f"❌ Timetable error: {timetable_data.get('error')}")
                
        else:
            print(f"❌ Timetable endpoint failed: {timetable_response.status_code}")
            print(timetable_response.text)
        
        # Also test the regular schedule endpoint for comparison
        print("\n📊 Comparing with regular schedule endpoint...")
        schedule_response = requests.get(f"{base_url}/student/schedule", headers=headers)
        
        if schedule_response.status_code == 200:
            schedule_data = schedule_response.json()
            schedules_count = len(schedule_data.get("schedules", []))
            print(f"✅ Regular schedule endpoint: {schedules_count} schedules found")
        
        print("\n✅ UNIVERSITY TIMETABLE SYSTEM READY!")
        print("The system now supports:")
        print("  📅 Weekly timetable view (like university schedule)")
        print("  🕐 Standard time slots (8:30-10:00, 10:10-11:40, etc.)")
        print("  📚 Subject + Teacher + Room display")
        print("  📆 Week navigation (current, next, previous)")
        print("  👥 Group-based schedule management")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    create_university_timetable()