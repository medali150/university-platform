#!/usr/bin/env python3
"""
Setup existing user as department head and test functionality
"""
import asyncio
import requests
import bcrypt
from prisma import Prisma

BASE_URL = "http://localhost:8000"

async def setup_existing_user_as_dept_head():
    """Set up existing user as department head"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("=== SETTING UP EXISTING USER AS DEPARTMENT HEAD ===\n")
        
        # Find the existing user
        user = await prisma.user.find_unique(
            where={"email": "hathemhafsi@gmail.com"},
            include={
                "departmentHead": {"include": {"department": True}},
                "teacher": {"include": {"department": True}}
            }
        )
        
        if not user:
            print("❌ User not found!")
            return None
        
        print(f"👤 Found user: {user.firstName} {user.lastName}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Login: {user.login}")
        print(f"👔 Current role: {user.role}")
        
        # Update role to DEPARTMENT_HEAD if needed
        if user.role != "DEPARTMENT_HEAD":
            print("🔄 Updating role to DEPARTMENT_HEAD...")
            user = await prisma.user.update(
                where={"id": user.id},
                data={"role": "DEPARTMENT_HEAD"}
            )
        
        # Find Computer Science department
        cs_dept = await prisma.department.find_first(
            where={"name": {"contains": "Computer Science"}}
        )
        
        if not cs_dept:
            print("📍 Creating Computer Science department...")
            cs_dept = await prisma.department.create(
                data={"name": "Computer Science Department"}
            )
        
        # Check if user already has department head record
        if not user.departmentHead:
            # Check if department already has a head
            existing_dept_head = await prisma.departmenthead.find_unique(
                where={"departmentId": cs_dept.id}
            )
            
            if existing_dept_head:
                print("⚠️  Removing existing department head...")
                await prisma.departmenthead.delete(where={"id": existing_dept_head.id})
            
            print("🏢 Creating department head record...")
            dept_head = await prisma.departmenthead.create(
                data={
                    "userId": user.id,
                    "departmentId": cs_dept.id
                }
            )
        else:
            print("✅ User already has department head record")
            dept_head = user.departmentHead
        
        # Check if user has teacher record
        if not user.teacher:
            print("👨‍🏫 Creating teacher record...")
            teacher = await prisma.teacher.create(
                data={
                    "userId": user.id,
                    "departmentId": cs_dept.id
                }
            )
        else:
            print("✅ User already has teacher record")
            teacher = user.teacher
        
        # Get updated user info
        updated_user = await prisma.user.find_unique(
            where={"id": user.id},
            include={
                "departmentHead": {"include": {"department": True}},
                "teacher": {"include": {"department": True}}
            }
        )
        
        print(f"\n✅ Setup complete!")
        print(f"   Name: {updated_user.firstName} {updated_user.lastName}")
        print(f"   Email: {updated_user.email}")
        print(f"   Login: {updated_user.login}")
        print(f"   Role: {updated_user.role}")
        print(f"   Department: {updated_user.departmentHead.department.name}")
        
        return updated_user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        await prisma.disconnect()

def test_login_and_get_resources():
    """Test login and get available resources"""
    print(f"\n=== TESTING LOGIN AND RESOURCES ===")
    
    # Test login
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "login": "hathemhafsi@gmail.com",
            "password": "dslighgh15"
        })
        
        print(f"Login Status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return None
            
        data = response.json()
        token = data['access_token']
        print(f"✅ Login successful!")
        
        # Get resources
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n📚 Getting available resources...")
        subjects_response = requests.get(f"{BASE_URL}/schedules/resources/subjects", headers=headers)
        groups_response = requests.get(f"{BASE_URL}/schedules/resources/groups", headers=headers)
        teachers_response = requests.get(f"{BASE_URL}/schedules/resources/teachers", headers=headers)
        rooms_response = requests.get(f"{BASE_URL}/schedules/resources/rooms", headers=headers)
        
        if subjects_response.status_code == 200:
            subjects = subjects_response.json()
            print(f"✅ Subjects: {len(subjects)} available")
            for i, subject in enumerate(subjects[:3]):  # Show first 3
                print(f"   {i+1}. {subject['name']} (ID: {subject['id']})")
        else:
            print(f"❌ Failed to get subjects: {subjects_response.text}")
            
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"✅ Groups: {len(groups)} available")
            for i, group in enumerate(groups[:3]):  # Show first 3
                print(f"   {i+1}. {group['name']} (ID: {group['id']})")
        else:
            print(f"❌ Failed to get groups: {groups_response.text}")
            
        if teachers_response.status_code == 200:
            teachers = teachers_response.json()
            print(f"✅ Teachers: {len(teachers)} available")
            for i, teacher in enumerate(teachers[:3]):  # Show first 3
                print(f"   {i+1}. {teacher['name']} (ID: {teacher['id']})")
        else:
            print(f"❌ Failed to get teachers: {teachers_response.text}")
            
        if rooms_response.status_code == 200:
            rooms = rooms_response.json()
            print(f"✅ Rooms: {len(rooms)} available")
            for i, room in enumerate(rooms[:3]):  # Show first 3
                print(f"   {i+1}. {room['code']} (ID: {room['id']})")
        else:
            print(f"❌ Failed to get rooms: {rooms_response.text}")
        
        # Test schedule creation if we have resources
        if all(r.status_code == 200 for r in [subjects_response, groups_response, teachers_response, rooms_response]):
            subjects = subjects_response.json()
            groups = groups_response.json()
            teachers = teachers_response.json()
            rooms = rooms_response.json()
            
            if subjects and groups and teachers and rooms:
                print(f"\n🧪 Testing schedule creation...")
                
                schedule_data = {
                    "date": "2025-10-02T10:00:00.000Z",
                    "startTime": "2025-10-02T10:00:00.000Z",
                    "endTime": "2025-10-02T12:00:00.000Z",
                    "roomId": rooms[0]['id'],
                    "subjectId": subjects[0]['id'],
                    "groupId": groups[0]['id'],
                    "teacherId": teachers[0]['id'],
                    "status": "PLANNED"
                }
                
                schedule_response = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
                
                print(f"Schedule Creation Status: {schedule_response.status_code}")
                if schedule_response.status_code == 201:
                    print(f"✅ Schedule created successfully!")
                    schedule = schedule_response.json()
                    print(f"   Schedule ID: {schedule['id']}")
                else:
                    print(f"❌ Schedule creation failed: {schedule_response.text}")
                
                # Generate Swagger payload
                print(f"\n📋 SWAGGER PAYLOAD FOR MANUAL TESTING:")
                print("=" * 60)
                print("{")
                print(f'  "date": "2025-10-02T14:00:00.000Z",')
                print(f'  "startTime": "2025-10-02T14:00:00.000Z",')
                print(f'  "endTime": "2025-10-02T16:00:00.000Z",')
                print(f'  "roomId": "{rooms[0]["id"]}",')
                print(f'  "subjectId": "{subjects[0]["id"]}",')
                print(f'  "groupId": "{groups[0]["id"]}",')
                print(f'  "teacherId": "{teachers[0]["id"]}",')
                print(f'  "status": "PLANNED"')
                print("}")
                print("=" * 60)
                
                print(f"\n🎯 LOGIN CREDENTIALS FOR SWAGGER:")
                print(f'{{')
                print(f'  "login": "hathemhafsi@gmail.com",')
                print(f'  "password": "dslighgh15"')
                print(f'}}')
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None

async def main():
    """Main execution function"""
    print("🔧 EXISTING USER SETUP AS DEPARTMENT HEAD")
    print("=" * 80)
    
    # Step 1: Set up existing user as department head
    user = await setup_existing_user_as_dept_head()
    
    if not user:
        print("❌ Failed to set up user as department head")
        return
    
    # Wait a moment for changes to propagate
    print(f"\n⏳ Waiting for changes to take effect...")
    await asyncio.sleep(2)
    
    # Step 2: Test functionality
    success = test_login_and_get_resources()
    
    if success:
        print(f"\n🎉 SETUP AND TESTING COMPLETE!")
        print(f"✅ User is now ready to use as department head")
        print(f"✅ All functionality tested successfully")
    else:
        print(f"\n⚠️  Setup completed but testing had issues")
        print(f"   Check if the API server is running on {BASE_URL}")

if __name__ == "__main__":
    asyncio.run(main())