#!/usr/bin/env python3
"""
Complete Department Head Setup and Testing Script
Creates a department head user and tests schedule creation functionality
"""
import asyncio
import requests
import bcrypt
from prisma import Prisma

BASE_URL = "http://localhost:8000"

async def create_department_head_user(
    email: str, 
    login: str, 
    password: str, 
    first_name: str, 
    last_name: str, 
    department_name: str = "Computer Science"
):
    """Create a complete department head user with all necessary records"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print(f"=== CREATING DEPARTMENT HEAD USER: {first_name} {last_name} ===\n")
        
        # Check if user already exists
        existing_user = await prisma.user.find_unique(
            where={"email": email}
        )
        
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return None
            
        existing_login = await prisma.user.find_unique(
            where={"login": login}
        )
        
        if existing_login:
            print(f"❌ User with login {login} already exists!")
            return None
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Find or create the department
        department = await prisma.department.find_first(
            where={"name": {"contains": department_name}}
        )
        
        if not department:
            print(f"📍 Creating new department: {department_name}")
            department = await prisma.department.create(
                data={"name": department_name}
            )
        else:
            print(f"📍 Found existing department: {department.name}")
        
        # Check if department already has a head
        existing_dept_head = await prisma.departmenthead.find_unique(
            where={"departmentId": department.id}
        )
        
        if existing_dept_head:
            existing_head_user = await prisma.user.find_unique(
                where={"id": existing_dept_head.userId}
            )
            print(f"⚠️  Department already has a head: {existing_head_user.firstName} {existing_head_user.lastName}")
            print(f"Removing existing department head to assign new one...")
            await prisma.departmenthead.delete(where={"id": existing_dept_head.id})
        
        # Create the user
        print(f"👤 Creating user account...")
        user = await prisma.user.create(
            data={
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "login": login,
                "passwordHash": password_hash,
                "role": "DEPARTMENT_HEAD"
            }
        )
        
        # Create the department head record
        print(f"🏢 Creating department head record...")
        dept_head = await prisma.departmenthead.create(
            data={
                "userId": user.id,
                "departmentId": department.id
            },
            include={
                "user": True,
                "department": True
            }
        )
        
        # Create a teacher record if needed (department heads are often teachers too)
        teacher = await prisma.teacher.create(
            data={
                "userId": user.id,
                "departmentId": department.id
            },
            include={
                "user": True,
                "department": True
            }
        )
        
        print(f"✅ Successfully created department head:")
        print(f"   Name: {user.firstName} {user.lastName}")
        print(f"   Email: {user.email}")
        print(f"   Login: {user.login}")
        print(f"   Department: {dept_head.department.name}")
        print(f"   Teacher ID: {teacher.id}")
        
        return {
            "user": user,
            "department_head": dept_head,
            "teacher": teacher,
            "department": department,
            "password": password
        }
        
    except Exception as e:
        print(f"❌ Error creating department head: {e}")
        return None
    finally:
        await prisma.disconnect()

async def setup_sample_data_for_department(department_id: str, teacher_id: str):
    """Create sample subjects, groups, and other resources for the department"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print(f"\n=== SETTING UP SAMPLE DATA FOR DEPARTMENT ===")
        
        # Create a specialty
        specialty = await prisma.specialty.create(
            data={
                "name": "Computer Science Specialty",
                "departmentId": department_id
            }
        )
        
        # Create levels
        levels = []
        for level_name in ["L1", "L2", "L3", "M1", "M2"]:
            level = await prisma.level.create(
                data={
                    "name": level_name,
                    "specialtyId": specialty.id
                }
            )
            levels.append(level)
        
        # Create groups
        groups = []
        for level in levels:
            for group_suffix in ["A", "B"]:
                group = await prisma.group.create(
                    data={
                        "name": f"{level.name}-G{group_suffix}",
                        "levelId": level.id
                    }
                )
                groups.append(group)
        
        # Create subjects
        subjects = []
        subject_names = [
            "Programming Fundamentals",
            "Data Structures",
            "Algorithms",
            "Database Systems",
            "Web Development",
            "Software Engineering"
        ]
        
        for i, subject_name in enumerate(subject_names):
            subject = await prisma.subject.create(
                data={
                    "name": subject_name,
                    "levelId": levels[i % len(levels)].id,
                    "teacherId": teacher_id
                }
            )
            subjects.append(subject)
        
        # Create rooms if they don't exist
        room_codes = ["CS-101", "CS-102", "CS-LAB1", "CS-LAB2"]
        rooms = []
        
        for room_code in room_codes:
            existing_room = await prisma.room.find_unique(where={"code": room_code})
            if not existing_room:
                room = await prisma.room.create(
                    data={
                        "code": room_code,
                        "type": "LAB" if "LAB" in room_code else "LECTURE",
                        "capacity": 30
                    }
                )
                rooms.append(room)
            else:
                rooms.append(existing_room)
        
        print(f"✅ Created sample data:")
        print(f"   Specialty: {specialty.name}")
        print(f"   Levels: {len(levels)}")
        print(f"   Groups: {len(groups)}")
        print(f"   Subjects: {len(subjects)}")
        print(f"   Rooms: {len(rooms)}")
        
        return {
            "specialty": specialty,
            "levels": levels,
            "groups": groups,
            "subjects": subjects,
            "rooms": rooms
        }
        
    except Exception as e:
        print(f"❌ Error setting up sample data: {e}")
        return None
    finally:
        await prisma.disconnect()

def test_login(login: str, password: str):
    """Test login functionality"""
    print(f"\n=== TESTING LOGIN ===")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "login": login,
            "password": password
        })
        
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"Access token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

async def get_department_resources(login: str, password: str):
    """Get all resources available for the department head"""
    print(f"\n=== GETTING DEPARTMENT RESOURCES ===")
    
    # Login first
    token = test_login(login, password)
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get subjects
        subjects_response = requests.get(f"{BASE_URL}/schedules/resources/subjects", headers=headers)
        groups_response = requests.get(f"{BASE_URL}/schedules/resources/groups", headers=headers)
        teachers_response = requests.get(f"{BASE_URL}/schedules/resources/teachers", headers=headers)
        rooms_response = requests.get(f"{BASE_URL}/schedules/resources/rooms", headers=headers)
        
        if all(r.status_code == 200 for r in [subjects_response, groups_response, teachers_response, rooms_response]):
            subjects = subjects_response.json()
            groups = groups_response.json()
            teachers = teachers_response.json()
            rooms = rooms_response.json()
            
            print(f"📚 Available Subjects: {len(subjects)}")
            for subject in subjects:
                print(f"   • {subject['name']} (ID: {subject['id']})")
            
            print(f"\n👥 Available Groups: {len(groups)}")
            for group in groups:
                print(f"   • {group['name']} (ID: {group['id']})")
            
            print(f"\n👨‍🏫 Available Teachers: {len(teachers)}")
            for teacher in teachers:
                print(f"   • {teacher['name']} (ID: {teacher['id']})")
            
            print(f"\n🏢 Available Rooms: {len(rooms)}")
            for room in rooms:
                print(f"   • {room['code']} (ID: {room['id']})")
            
            return {
                "subjects": subjects,
                "groups": groups,
                "teachers": teachers,
                "rooms": rooms,
                "token": token
            }
        else:
            print(f"❌ Failed to get resources")
            return None
            
    except Exception as e:
        print(f"❌ Error getting resources: {e}")
        return None

def test_schedule_creation(resources, token):
    """Test creating a schedule with the available resources"""
    print(f"\n=== TESTING SCHEDULE CREATION ===")
    
    if not resources or not token:
        print("❌ No resources or token available")
        return False
    
    subjects = resources['subjects']
    groups = resources['groups']
    teachers = resources['teachers']
    rooms = resources['rooms']
    
    if not (subjects and groups and teachers and rooms):
        print("❌ Missing required resources")
        return False
    
    # Create schedule payload
    schedule_data = {
        "date": "2025-10-01T08:00:00.000Z",
        "startTime": "2025-10-01T08:00:00.000Z",
        "endTime": "2025-10-01T10:00:00.000Z",
        "roomId": rooms[0]['id'],
        "subjectId": subjects[0]['id'],
        "groupId": groups[0]['id'],
        "teacherId": teachers[0]['id'],
        "status": "PLANNED"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
        
        print(f"Schedule Creation Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Schedule created successfully!")
            print(f"   Schedule ID: {data['id']}")
            print(f"   Subject: {subjects[0]['name']}")
            print(f"   Group: {groups[0]['name']}")
            print(f"   Room: {rooms[0]['code']}")
            print(f"   Time: 08:00 - 10:00")
            return True
        else:
            print(f"❌ Schedule creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating schedule: {e}")
        return False

def generate_swagger_payload(resources):
    """Generate a ready-to-use Swagger payload"""
    if not resources:
        return None
    
    subjects = resources['subjects']
    groups = resources['groups'] 
    teachers = resources['teachers']
    rooms = resources['rooms']
    
    if not (subjects and groups and teachers and rooms):
        return None
    
    payload = {
        "date": "2025-10-01T14:00:00.000Z",
        "startTime": "2025-10-01T14:00:00.000Z", 
        "endTime": "2025-10-01T16:00:00.000Z",
        "roomId": rooms[0]['id'],
        "subjectId": subjects[0]['id'],
        "groupId": groups[0]['id'],
        "teacherId": teachers[0]['id'],
        "status": "PLANNED"
    }
    
    print(f"\n📋 SWAGGER PAYLOAD FOR MANUAL TESTING:")
    print("=" * 60)
    print("{")
    for key, value in payload.items():
        print(f'  "{key}": "{value}",')
    print("}")
    print("=" * 60)
    
    return payload

async def main():
    """Main function to set up everything"""
    print("🚀 DEPARTMENT HEAD COMPLETE SETUP SCRIPT")
    print("=" * 80)
    
    # Configuration - you can modify these
    EMAIL = "hathemhafsi@gmail.com"
    LOGIN = "hathemhafsi@gmail.com"
    PASSWORD = "dslighgh15"
    FIRST_NAME = "Hathem"
    LAST_NAME = "Hafsi"
    DEPARTMENT_NAME = "Computer Science"
    
    # Step 1: Create department head user
    dept_head_data = await create_department_head_user(
        email=EMAIL,
        login=LOGIN,
        password=PASSWORD,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        department_name=DEPARTMENT_NAME
    )
    
    if not dept_head_data:
        print("❌ Failed to create department head user")
        return
    
    # Step 2: Set up sample data
    sample_data = await setup_sample_data_for_department(
        department_id=dept_head_data['department'].id,
        teacher_id=dept_head_data['teacher'].id
    )
    
    if not sample_data:
        print("❌ Failed to set up sample data")
        return
    
    print(f"\n⏳ Waiting for API server to be ready...")
    await asyncio.sleep(2)
    
    # Step 3: Test the setup
    resources = await get_department_resources(LOGIN, PASSWORD)
    
    if resources:
        # Step 4: Test schedule creation
        success = test_schedule_creation(resources, resources['token'])
        
        # Step 5: Generate Swagger payload
        generate_swagger_payload(resources)
        
        print(f"\n🎉 SETUP COMPLETE!")
        print(f"📧 Email: {EMAIL}")
        print(f"🔑 Login: {LOGIN}")
        print(f"🔒 Password: {PASSWORD}")
        print(f"🏢 Department: {DEPARTMENT_NAME}")
        
        if success:
            print(f"✅ Schedule creation test: PASSED")
        else:
            print(f"❌ Schedule creation test: FAILED")
        
        print(f"\n📝 You can now use these credentials in Swagger UI:")
        print(f"   1. Login with: {LOGIN} / {PASSWORD}")
        print(f"   2. Use the generated payload above for schedule creation")
    else:
        print(f"❌ Failed to get resources - check if API server is running")

if __name__ == "__main__":
    asyncio.run(main())