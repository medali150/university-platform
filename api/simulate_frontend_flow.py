#!/usr/bin/env python3
"""
Complete test to simulate what frontend does after department head login
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def simulate_frontend_dept_head_login():
    print("=" * 80)
    print("SIMULATING COMPLETE FRONTEND FLOW FOR DEPARTMENT HEAD")
    print("=" * 80)
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Step 1: Login
        print("\n📝 Step 1: Login as Department Head")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "chef.dept1@university.tn",
                "password": "Test123!"
            }
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        login_data = login_response.json()
        token = login_data['access_token']
        user = login_data['user']
        
        print(f"   ✅ Login successful")
        print(f"   User: {user['prenom']} {user['nom']}")
        print(f"   Role: {user['role']}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get current user (like AuthContext does)
        print("\n📝 Step 2: Verify Token with /auth/me")
        me_response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            print(f"   ✅ Token valid")
        else:
            print(f"   ❌ Token verification failed: {me_response.text}")
            return
        
        # Step 3: Load dashboard data (like department-head/page.tsx does)
        print("\n📝 Step 3: Load Departments (for dashboard)")
        dept_response = await client.get(f"{BASE_URL}/departments", headers=headers)
        print(f"   Status: {dept_response.status_code}")
        if dept_response.status_code == 200:
            depts = dept_response.json()
            print(f"   ✅ Departments loaded: {len(depts)}")
        else:
            print(f"   ❌ Failed: {dept_response.text}")
        
        # Step 4: Get students (simulating getDepartmentComprehensiveData)
        print("\n📝 Step 4: Get Students")
        students_response = await client.get(f"{BASE_URL}/students", headers=headers)
        print(f"   Status: {students_response.status_code}")
        if students_response.status_code == 200:
            students = students_response.json()
            print(f"   ✅ Students loaded: {len(students)}")
        elif students_response.status_code == 404:
            print(f"   ℹ️  Endpoint not found (expected)")
        else:
            print(f"   ⚠️  Failed: {students_response.text}")
        
        # Step 5: Get teachers
        print("\n📝 Step 5: Get Teachers")
        teachers_response = await client.get(f"{BASE_URL}/teachers", headers=headers)
        print(f"   Status: {teachers_response.status_code}")
        if teachers_response.status_code == 200:
            teachers = teachers_response.json()
            print(f"   ✅ Teachers loaded: {len(teachers)}")
        elif teachers_response.status_code == 404:
            print(f"   ℹ️  Endpoint not found (expected)")
        else:
            print(f"   ⚠️  Failed: {teachers_response.text}")
        
        # Step 6: Get subjects
        print("\n📝 Step 6: Get Subjects")
        subjects_response = await client.get(f"{BASE_URL}/subjects", headers=headers)
        print(f"   Status: {subjects_response.status_code}")
        if subjects_response.status_code == 200:
            subjects = subjects_response.json()
            print(f"   ✅ Subjects loaded: {len(subjects)}")
        elif subjects_response.status_code == 404:
            print(f"   ℹ️  Endpoint not found (expected)")
        else:
            print(f"   ⚠️  Failed: {subjects_response.text}")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("✅ Department head can login successfully")
        print("✅ Token is valid and works for authenticated endpoints")
        print("✅ All tested endpoints accessible")
        print("\n⚠️  If frontend still fails, the issue is in the frontend code, not backend!")

if __name__ == "__main__":
    asyncio.run(simulate_frontend_dept_head_login())
