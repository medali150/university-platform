#!/usr/bin/env python3
"""
Test authentication for department heads
"""
import asyncio
import requests
from prisma import Prisma

BASE_URL = "http://localhost:8000"

async def get_dept_head_credentials():
    """Get department head credentials from database"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        dept_heads = await prisma.user.find_many(
            where={"role": "DEPARTMENT_HEAD"},
            include={
                "departmentHead": {
                    "include": {
                        "department": True
                    }
                }
            }
        )
        
        print("=== DEPARTMENT HEAD USERS ===")
        for user in dept_heads:
            print(f"\nUser: {user.firstName} {user.lastName}")
            print(f"Email: {user.email}")
            print(f"Login: {user.login}")
            print(f"ID: {user.id}")
            if user.departmentHead:
                print(f"Department: {user.departmentHead.department.name}")
            else:
                print("❌ No DepartmentHead record linked!")
                
        return dept_heads
    finally:
        await prisma.disconnect()

def test_login(login: str, password: str = "password123"):
    """Test login for a user"""
    print(f"\n=== TESTING LOGIN FOR {login} ===")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "login": login,
            "password": password
        })
        
        print(f"Status: {response.status_code}")
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

def test_schedule_creation_with_token(token: str):
    """Test creating a schedule with the token"""
    print(f"\n=== TESTING SCHEDULE CREATION ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample schedule data - using string IDs for testing
    schedule_data = {
        "date": "2025-09-28T16:37:34.087Z",
        "startTime": "2025-09-28T16:37:34.087Z", 
        "endTime": "2025-09-28T16:37:34.087Z",
        "roomId": "string",
        "subjectId": "string",
        "groupId": "string", 
        "teacherId": "string",
        "status": "PLANNED"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404 and "Department Head record not found" in response.text:
            print("❌ Issue confirmed: Department Head record not found")
        elif response.status_code == 404:
            print("❌ Different 404 error - probably missing resources")
        else:
            print(f"Different response than expected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    dept_heads = await get_dept_head_credentials()
    
    if dept_heads:
        # Try to login with the first department head
        first_dept_head = dept_heads[0]
        token = test_login(first_dept_head.login)
        
        if token:
            test_schedule_creation_with_token(token)
        
        # Also try with other common passwords
        for password in ["password", "123456", "admin"]:
            print(f"\nTrying with password: {password}")
            token = test_login(first_dept_head.login, password)
            if token:
                test_schedule_creation_with_token(token)
                break

if __name__ == "__main__":
    asyncio.run(main())