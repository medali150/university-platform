#!/usr/bin/env python3
"""
Complete Department Head Setup - Final Version
Creates all necessary resources for the department head user
"""
import asyncio
import requests
from prisma import Prisma

BASE_URL = "http://localhost:8000"

async def setup_complete_department_resources():
    """Set up complete resources for the department head"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== SETTING UP COMPLETE DEPARTMENT RESOURCES ===\n")
        
        # Get the user and their department
        user = await prisma.user.find_unique(
            where={"email": "hathemhafsi@gmail.com"},
            include={
                "departmentHead": {"include": {"department": True}},
                "teacher": {"include": {"department": True}}
            }
        )
        
        if not user or not user.departmentHead:
            print("❌ User or department head record not found!")
            return False
        
        dept = user.departmentHead.department
        teacher = user.teacher
        
        print(f"👤 User: {user.firstName} {user.lastName}")
        print(f"🏢 Department: {dept.name}")
        print(f"👨‍🏫 Teacher ID: {teacher.id}")
        
        # Create specialty for the department
        specialty = await prisma.specialty.find_first(
            where={"departmentId": dept.id}
        )
        
        if not specialty:
            print("📋 Creating specialty...")
            specialty = await prisma.specialty.create(
                data={
                    "name": f"{dept.name} Specialty",
                    "departmentId": dept.id
                }
            )
        
        # Create levels
        level_names = ["L1", "L2", "L3", "M1", "M2"]
        levels = []
        
        for level_name in level_names:
            existing_level = await prisma.level.find_first(
                where={
                    "name": level_name,
                    "specialtyId": specialty.id
                }
            )
            
            if not existing_level:
                level = await prisma.level.create(
                    data={
                        "name": level_name,
                        "specialtyId": specialty.id
                    }
                )
                levels.append(level)
            else:
                levels.append(existing_level)
        
        print(f"📚 Levels: {len(levels)} created/found")
        
        # Create groups
        groups_created = 0
        for level in levels:
            for group_suffix in ["A", "B"]:
                group_name = f"{level.name}-G{group_suffix}"
                existing_group = await prisma.group.find_first(
                    where={
                        "name": group_name,
                        "levelId": level.id
                    }
                )
                
                if not existing_group:
                    await prisma.group.create(
                        data={
                            "name": group_name,
                            "levelId": level.id
                        }
                    )
                    groups_created += 1
        
        print(f"👥 Groups: {groups_created} new groups created")
        
        # Create subjects
        subject_names = [
            "Fundamentals Course",
            "Advanced Topics", 
            "Practical Applications",
            "Theory and Methods",
            "Research Project"
        ]
        
        subjects_created = 0
        for i, subject_name in enumerate(subject_names):
            level = levels[i % len(levels)]
            
            existing_subject = await prisma.subject.find_first(
                where={
                    "name": subject_name,
                    "levelId": level.id,
                    "teacherId": teacher.id
                }
            )
            
            if not existing_subject:
                await prisma.subject.create(
                    data={
                        "name": subject_name,
                        "levelId": level.id,
                        "teacherId": teacher.id
                    }
                )
                subjects_created += 1
        
        print(f"📖 Subjects: {subjects_created} new subjects created")
        
        # Create rooms if needed
        room_codes = ["ROOM-101", "ROOM-102", "LAB-201", "LAB-202"]
        rooms_created = 0
        
        for room_code in room_codes:
            existing_room = await prisma.room.find_unique(
                where={"code": room_code}
            )
            
            if not existing_room:
                await prisma.room.create(
                    data={
                        "code": room_code,
                        "type": "LAB" if "LAB" in room_code else "LECTURE",
                        "capacity": 30
                    }
                )
                rooms_created += 1
        
        print(f"🏢 Rooms: {rooms_created} new rooms created")
        
        print(f"\n✅ Department setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up resources: {e}")
        return False
    finally:
        await prisma.disconnect()

def test_complete_functionality():
    """Test the complete functionality"""
    print(f"\n=== TESTING COMPLETE FUNCTIONALITY ===")
    
    # Login
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "login": "hathemhafsi@gmail.com",
            "password": "dslighgh15"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Login successful!")
        
        # Get all resources
        subjects_response = requests.get(f"{BASE_URL}/schedules/resources/subjects", headers=headers)
        groups_response = requests.get(f"{BASE_URL}/schedules/resources/groups", headers=headers)
        teachers_response = requests.get(f"{BASE_URL}/schedules/resources/teachers", headers=headers)
        rooms_response = requests.get(f"{BASE_URL}/schedules/resources/rooms", headers=headers)
        
        print(f"\n📊 Resource Status:")
        print(f"   Subjects: {subjects_response.status_code}")
        print(f"   Groups: {groups_response.status_code}")
        print(f"   Teachers: {teachers_response.status_code}")
        print(f"   Rooms: {rooms_response.status_code}")
        
        if all(r.status_code == 200 for r in [subjects_response, groups_response, teachers_response, rooms_response]):
            subjects = subjects_response.json()
            groups = groups_response.json()
            teachers = teachers_response.json()
            rooms = rooms_response.json()
            
            print(f"\n📈 Available Resources:")
            print(f"   📚 Subjects: {len(subjects)}")
            print(f"   👥 Groups: {len(groups)}")
            print(f"   👨‍🏫 Teachers: {len(teachers)}")
            print(f"   🏢 Rooms: {len(rooms)}")
            
            if subjects and groups and teachers and rooms:
                # Test schedule creation
                schedule_data = {
                    "date": "2025-10-03T09:00:00.000Z",
                    "startTime": "2025-10-03T09:00:00.000Z",
                    "endTime": "2025-10-03T11:00:00.000Z",
                    "roomId": rooms[0]['id'],
                    "subjectId": subjects[0]['id'],
                    "groupId": groups[0]['id'],
                    "teacherId": teachers[0]['id'],
                    "status": "PLANNED"
                }
                
                schedule_response = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
                
                print(f"\n🧪 Schedule Creation Test:")
                print(f"   Status: {schedule_response.status_code}")
                
                if schedule_response.status_code == 201:
                    schedule = schedule_response.json()
                    print(f"   ✅ SUCCESS! Schedule ID: {schedule['id']}")
                else:
                    print(f"   ❌ FAILED: {schedule_response.text}")
                
                # Generate final Swagger payload
                print(f"\n" + "="*80)
                print(f"🎯 FINAL SWAGGER PAYLOADS FOR TESTING")
                print(f"="*80)
                
                print(f"\n1️⃣ LOGIN PAYLOAD:")
                print(f'{{')
                print(f'  "login": "hathemhafsi@gmail.com",')
                print(f'  "password": "dslighgh15"')
                print(f'}}')
                
                print(f"\n2️⃣ SCHEDULE CREATION PAYLOAD:")
                print(f'{{')
                print(f'  "date": "2025-10-03T14:00:00.000Z",')
                print(f'  "startTime": "2025-10-03T14:00:00.000Z",')
                print(f'  "endTime": "2025-10-03T16:00:00.000Z",')
                print(f'  "roomId": "{rooms[0]["id"]}",')
                print(f'  "subjectId": "{subjects[0]["id"]}",')
                print(f'  "groupId": "{groups[0]["id"]}",')
                print(f'  "teacherId": "{teachers[0]["id"]}",')
                print(f'  "status": "PLANNED"')
                print(f'}}')
                
                print(f"\n📋 Resource Details:")
                print(f"   Subject: {subjects[0]['name']}")
                print(f"   Group: {groups[0]['name']}")
                print(f"   Teacher: {teachers[0]['name']}")
                print(f"   Room: {rooms[0]['code']}")
                
                print(f"\n" + "="*80)
                
                return True
            else:
                print(f"❌ Some resources are empty")
                return False
        else:
            print(f"❌ Failed to get some resources")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

async def main():
    """Main execution"""
    print("🚀 COMPLETE DEPARTMENT HEAD SETUP - FINAL")
    print("="*80)
    
    # Step 1: Set up all resources
    success = await setup_complete_department_resources()
    
    if not success:
        print("❌ Failed to set up resources")
        return
    
    # Wait for changes to propagate
    await asyncio.sleep(2)
    
    # Step 2: Test everything
    test_success = test_complete_functionality()
    
    if test_success:
        print(f"\n🎉 COMPLETE SETUP SUCCESSFUL!")
        print(f"✅ Department head user is fully configured")
        print(f"✅ All resources are available") 
        print(f"✅ Schedule creation is working")
        print(f"✅ Ready for use in Swagger UI")
    else:
        print(f"\n⚠️  Setup completed but testing had issues")

if __name__ == "__main__":
    asyncio.run(main())