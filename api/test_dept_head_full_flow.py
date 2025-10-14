#!/usr/bin/env python3
"""
Test complete department head flow: login -> get profile -> get department data
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_dept_head_flow():
    print("=" * 80)
    print("TESTING FULL DEPARTMENT HEAD FLOW")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        # Test credentials
        credentials = {
            "email": "chef.dept1@university.tn",
            "password": "Test123!"
        }
        
        print("\n📝 Step 1: Login")
        print(f"   Email: {credentials['email']}")
        
        # Login
        try:
            login_response = await client.post(
                f"{BASE_URL}/auth/login",
                json=credentials
            )
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"   ✅ Login successful")
                print(f"   User: {login_data['user']['prenom']} {login_data['user']['nom']}")
                print(f"   Role: {login_data['user']['role']}")
                
                access_token = login_data['access_token']
                print(f"   Token: {access_token[:50]}...")
                
                # Test protected endpoints
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Step 2: Get current user
                print("\n📝 Step 2: Get Current User (/auth/me)")
                me_response = await client.get(
                    f"{BASE_URL}/auth/me",
                    headers=headers
                )
                print(f"   Status: {me_response.status_code}")
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"   ✅ User data retrieved")
                    print(f"   ID: {me_data['id']}")
                    print(f"   Role: {me_data['role']}")
                else:
                    print(f"   ❌ Failed: {me_response.text}")
                
                # Step 3: Get departments
                print("\n📝 Step 3: Get Departments (/auth/departments)")
                dept_response = await client.get(
                    f"{BASE_URL}/auth/departments",
                    headers=headers
                )
                print(f"   Status: {dept_response.status_code}")
                if dept_response.status_code == 200:
                    dept_data = dept_response.json()
                    depts = dept_data.get('departments', [])
                    print(f"   ✅ Departments retrieved: {len(depts)}")
                    for dept in depts[:3]:  # Show first 3
                        print(f"      - {dept.get('nom', dept.get('name', 'Unknown'))} (ID: {dept['id']})")
                else:
                    print(f"   ❌ Failed: {dept_response.text}")
                
                # Step 4: Try to get department comprehensive data (if endpoint exists)
                print("\n📝 Step 4: Get Department Comprehensive Data")
                if len(depts) > 0:
                    dept_id = depts[0]['id']
                    comp_response = await client.get(
                        f"{BASE_URL}/departments/{dept_id}/comprehensive",
                        headers=headers
                    )
                    print(f"   Status: {comp_response.status_code}")
                    if comp_response.status_code == 200:
                        comp_data = comp_response.json()
                        print(f"   ✅ Comprehensive data retrieved")
                        print(f"   Students: {len(comp_data.get('students', []))}")
                        print(f"   Teachers: {len(comp_data.get('teachers', []))}")
                        print(f"   Subjects: {len(comp_data.get('subjects', []))}")
                    elif comp_response.status_code == 404:
                        print(f"   ℹ️  Endpoint not found (expected)")
                    else:
                        print(f"   ⚠️  Failed: {comp_response.text}")
                
                # Step 5: Check chef departement endpoints
                print("\n📝 Step 5: Check Chef Departement Profile")
                chef_response = await client.get(
                    f"{BASE_URL}/chef-departements/profile",
                    headers=headers
                )
                print(f"   Status: {chef_response.status_code}")
                if chef_response.status_code == 200:
                    chef_data = chef_response.json()
                    print(f"   ✅ Chef profile retrieved")
                    print(f"   Department: {chef_data.get('departement', {}).get('nom', 'N/A')}")
                elif chef_response.status_code == 404:
                    print(f"   ℹ️  Endpoint not found")
                else:
                    print(f"   ⚠️  Failed: {chef_response.text}")
                
            else:
                print(f"   ❌ Login failed")
                print(f"   Response: {login_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_dept_head_flow())
