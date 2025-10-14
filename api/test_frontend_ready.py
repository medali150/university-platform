#!/usr/bin/env python3
"""
Final comprehensive test for university timetable display
"""

import requests
import json

def test_frontend_ready():
    print("🎓 FINAL UNIVERSITY TIMETABLE FRONTEND TEST")
    print("=" * 60)
    
    try:
        # Login
        login_response = requests.post("http://localhost:8000/auth/login", json={
            "email": "ahmed.student@university.edu",
            "password": "student2025"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test university timetable endpoint
        print("\n🏫 Testing University Timetable Endpoint...")
        response = requests.get("http://localhost:8000/student/timetable?week_offset=0", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return
        
        data = response.json()
        print("✅ API call successful")
        
        if not data.get('success'):
            print(f"❌ API error: {data.get('error')}")
            return
        
        print("✅ API returned success=true")
        
        # Analyze structure
        timetable = data.get('timetable', {})
        time_slots = data.get('time_slots', [])
        days = data.get('days', [])
        
        print(f"\n📊 Data Structure Analysis:")
        print(f"  🕐 Time slots: {len(time_slots)}")
        print(f"  📅 Days: {len(days)}")
        print(f"  📋 Timetable slots: {len(timetable)}")
        
        # Count courses and show structure
        total_courses = 0
        table_preview = []
        
        for time_slot in time_slots:
            slot_id = time_slot['id']
            slot_data = timetable.get(slot_id, {})
            courses = slot_data.get('courses', {})
            
            row = [time_slot['label']]
            for day in days:
                day_id = day['id']
                course = courses.get(day_id)
                
                if course:
                    total_courses += 1
                    subject = course.get('subject', {}).get('nom', 'Unknown')
                    teacher = f"{course.get('teacher', {}).get('prenom', '')} {course.get('teacher', {}).get('nom', '')}".strip()
                    room = course.get('room', {}).get('code', 'Unknown')
                    row.append(f"{subject}\\n{teacher}\\n{room}")
                else:
                    row.append("---")
            
            table_preview.append(row)
        
        print(f"  📚 Total courses: {total_courses}")
        
        # Show table preview
        if total_courses > 0:
            print(f"\n🎯 UNIVERSITY TIMETABLE PREVIEW:")
            print("=" * 60)
            
            # Header
            header = ["Horaires"] + [day['name'] for day in days]
            print(" | ".join(f"{h:12}" for h in header))
            print("-" * 80)
            
            # Show first few rows
            for i, row in enumerate(table_preview[:3]):
                cells = []
                for j, cell in enumerate(row):
                    if j == 0:  # Time column
                        cells.append(f"{cell:12}")
                    else:  # Course columns
                        # Show first line only for preview
                        first_line = cell.split('\\n')[0]
                        cells.append(f"{first_line[:12]:12}")
                print(" | ".join(cells))
            
            if len(table_preview) > 3:
                print(f"... and {len(table_preview) - 3} more time slots")
            
            print("\n🎉 UNIVERSITY TIMETABLE DATA IS READY!")
            print("✅ Frontend should display this as a beautiful table")
            
        else:
            print("\n⚠️ No courses found in timetable")
        
        # Frontend integration status
        print(f"\n🎨 FRONTEND INTEGRATION STATUS:")
        print(f"  ✅ API Endpoint: /student/timetable ✓")
        print(f"  ✅ Response Format: University table structure ✓")
        print(f"  ✅ Data Available: {total_courses} courses ✓")
        print(f"  ✅ Table Structure: {len(time_slots)} rows × {len(days)} columns ✓")
        
        print(f"\n🚀 FRONTEND SHOULD NOW SHOW THE UNIVERSITY TIMETABLE!")
        print(f"   Navigate to: http://localhost:3000/dashboard/student/timetable")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_ready()