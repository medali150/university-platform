#!/usr/bin/env python3

import asyncio
import requests
import json
from datetime import datetime, timedelta
from app.db.prisma_client import DatabaseManager

# Test configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/schedules"

async def setup_test_data():
    """Create test data for schedule testing"""
    print("=== SETTING UP TEST DATA ===")
    
    db_manager = DatabaseManager()
    await db_manager.connect()
    prisma = db_manager.prisma
    
    try:
        # Create or get department
        dept = await prisma.department.upsert(
            where={"name": "Computer Science"},
            create={
                "name": "Computer Science"
            },
            update={}
        )
        
        # Create specialty
        specialty = await prisma.specialty.upsert(
            where={"name": "Software Engineering"},
            create={
                "name": "Software Engineering",
                "departmentId": dept.id
            },
            update={}
        )
        
        # Create level
        level = await prisma.level.upsert(
            where={"name": "L3"},
            create={
                "name": "L3",
                "specialtyId": specialty.id
            },
            update={}
        )
        
        # Create group
        group = await prisma.group.upsert(
            where={"name": "L3-G1"},
            create={
                "name": "L3-G1",
                "levelId": level.id
            },
            update={}
        )
        
        # Create room
        room = await prisma.room.upsert(
            where={"code": "ROOM-101"},
            create={
                "code": "ROOM-101",
                "type": "LECTURE",
                "capacity": 50
            },
            update={}
        )
        
        # Get existing department head user or create
        dept_head_user = await prisma.user.find_first(
            where={"role": "DEPARTMENT_HEAD"}
        )
        
        if dept_head_user:
            # Create or update teacher record for the department head user
            teacher = await prisma.teacher.upsert(
                where={"userId": dept_head_user.id},
                create={
                    "userId": dept_head_user.id,
                    "departmentId": dept.id
                },
                update={"departmentId": dept.id}
            )
            
            # Create subject taught by this teacher
            subject = await prisma.subject.upsert(
                where={"name": "Advanced Programming"},
                create={
                    "name": "Advanced Programming",
                    "levelId": level.id,
                    "teacherId": teacher.id
                },
                update={}
            )
            
            print(f"✅ Test data created:")
            print(f"   Department: {dept.name} ({dept.id})")
            print(f"   Specialty: {specialty.name} ({specialty.id})")
            print(f"   Level: {level.name} ({level.id})")
            print(f"   Group: {group.name} ({group.id})")
            print(f"   Room: {room.code} ({room.id})")
            print(f"   Teacher: {teacher.id}")
            print(f"   Subject: {subject.name} ({subject.id})")
            
            return {
                "department_id": dept.id,
                "subject_id": subject.id,
                "group_id": group.id,
                "room_id": room.id,
                "teacher_id": teacher.id,
                "dept_head_user_id": dept_head_user.id
            }
        else:
            print("❌ No DEPARTMENT_HEAD user found. Please create one first.")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        return None
    finally:
        await db_manager.disconnect()


def get_auth_token(login: str, password: str):
    """Get authentication token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "login": login,
            "password": password
        })
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_create_schedule(token: str, test_data: dict):
    """Test schedule creation"""
    print("\n=== TESTING SCHEDULE CREATION ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Schedule for tomorrow at 10:00-12:00
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
    
    schedule_data = {
        "date": tomorrow.isoformat(),
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "roomId": test_data["room_id"],
        "subjectId": test_data["subject_id"],
        "groupId": test_data["group_id"],
        "teacherId": test_data["teacher_id"],
        "status": "PLANNED"
    }
    
    try:
        response = requests.post(API_URL, json=schedule_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Schedule created successfully!")
            print(f"   ID: {result['id']}")
            print(f"   Date: {result['date']}")
            print(f"   Time: {result['startTime']} - {result['endTime']}")
            print(f"   Room: {result['room']['code']}")
            print(f"   Subject: {result['subject']['name']}")
            return result['id']
        else:
            print(f"❌ Failed to create schedule: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating schedule: {e}")
        return None


def test_schedule_conflict(token: str, test_data: dict):
    """Test schedule conflict detection"""
    print("\n=== TESTING CONFLICT DETECTION ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create overlapping schedule
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)  # Overlaps with 10-12
    end_time = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
    
    conflicting_schedule = {
        "date": tomorrow.isoformat(),
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "roomId": test_data["room_id"],  # Same room
        "subjectId": test_data["subject_id"],
        "groupId": test_data["group_id"],
        "teacherId": test_data["teacher_id"],
        "status": "PLANNED"
    }
    
    try:
        response = requests.post(API_URL, json=conflicting_schedule, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 409:
            result = response.json()
            print(f"✅ Conflict correctly detected!")
            print(f"   Error: {result['detail']['error']}")
            for conflict in result['detail']['conflicts']:
                print(f"   - {conflict['type']}: {conflict['message']}")
        else:
            print(f"❌ Expected conflict (409) but got: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing conflict: {e}")


def test_update_schedule(token: str, schedule_id: str):
    """Test schedule update"""
    print("\n=== TESTING SCHEDULE UPDATE ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "status": "MAKEUP"
    }
    
    try:
        response = requests.patch(f"{API_URL}/{schedule_id}", json=update_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schedule updated successfully!")
            print(f"   New status: {result['status']}")
        else:
            print(f"❌ Failed to update schedule: {response.text}")
    except Exception as e:
        print(f"❌ Error updating schedule: {e}")


def test_get_department_schedules(token: str):
    """Test getting department schedules"""
    print("\n=== TESTING GET DEPARTMENT SCHEDULES ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/department", headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            schedules = response.json()
            print(f"✅ Retrieved {len(schedules)} schedules")
            for schedule in schedules:
                print(f"   - {schedule['subject']['name']} on {schedule['date']} at {schedule['startTime']} in {schedule['room']['code']}")
        else:
            print(f"❌ Failed to get schedules: {response.text}")
    except Exception as e:
        print(f"❌ Error getting schedules: {e}")


async def main():
    """Main test function"""
    print("🧪 TESTING SCHEDULE ENDPOINTS FOR DEPARTMENT HEADS")
    
    # Setup test data
    test_data = await setup_test_data()
    if not test_data:
        print("❌ Cannot proceed without test data")
        return
    
    # Get department head token
    print(f"\n=== AUTHENTICATING AS DEPARTMENT HEAD ===")
    dept_head_token = get_auth_token("janesmith", "password123")  # Adjust credentials
    
    if not dept_head_token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("✅ Authenticated as Department Head")
    
    # Run tests
    schedule_id = test_create_schedule(dept_head_token, test_data)
    
    if schedule_id:
        test_schedule_conflict(dept_head_token, test_data)
        test_update_schedule(dept_head_token, schedule_id)
    
    test_get_department_schedules(dept_head_token)
    
    print("\n🎉 TESTING COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())