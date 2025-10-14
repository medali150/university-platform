#!/usr/bin/env python3
"""Test /departments endpoint with authentication"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_departments_endpoint():
    print("=" * 80)
    print("TESTING /departments ENDPOINT")
    print("=" * 80)
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Login first
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "chef.dept1@university.tn",
                "password": "Test123!"
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n1. Testing /departments (no trailing slash):")
            resp1 = await client.get(f"{BASE_URL}/departments", headers=headers)
            print(f"   Status: {resp1.status_code}")
            if resp1.status_code == 200:
                print(f"   ✅ Success: {len(resp1.json())} departments")
            else:
                print(f"   Response: {resp1.text[:200]}")
            
            print("\n2. Testing /departments/ (with trailing slash):")
            resp2 = await client.get(f"{BASE_URL}/departments/", headers=headers)
            print(f"   Status: {resp2.status_code}")
            if resp2.status_code == 200:
                print(f"   ✅ Success: {len(resp2.json())} departments")
            else:
                print(f"   Response: {resp2.text[:200]}")
            
            print("\n3. Testing /auth/departments:")
            resp3 = await client.get(f"{BASE_URL}/auth/departments", headers=headers)
            print(f"   Status: {resp3.status_code}")
            if resp3.status_code == 200:
                data = resp3.json()
                depts = data.get('departments', data)
                print(f"   ✅ Success: {len(depts)} departments")
            else:
                print(f"   Response: {resp3.text[:200]}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_departments_endpoint())
