#!/usr/bin/env python3
"""
Test script for teacher department update endpoint
"""

import asyncio
import httpx

async def test_department_update():
    """Test teacher department update endpoint"""
    
    base_url = "http://localhost:8000"
    
    # First, login as the teacher to get a token
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔐 Logging in as teacher...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(login_response.text)
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Login successful!")
            
            # Get current profile first
            print("\n📋 Getting current teacher profile...")
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                current_dept = profile_data.get('department', {})
                print(f"✅ Current department: {current_dept.get('nom')} (ID: {current_dept.get('id')})")
            else:
                print(f"❌ Failed to get profile: {profile_response.status_code}")
                return
            
            # Get available departments
            print("\n🏢 Getting available departments...")
            departments_response = await client.get(f"{base_url}/teacher/departments", headers=headers)
            
            if departments_response.status_code != 200:
                print(f"❌ Failed to get departments: {departments_response.status_code}")
                return
            
            departments = departments_response.json()
            print(f"✅ Found {len(departments)} departments")
            
            # Find a different department to switch to
            target_dept = None
            for dept in departments:
                if dept['id'] != current_dept.get('id'):
                    target_dept = dept
                    break
            
            if not target_dept:
                print("ℹ️ Only one department available, creating a test department...")
                # For testing, let's just use the current department ID (no actual change)
                target_dept = {'id': current_dept.get('id'), 'nom': current_dept.get('nom')}
            
            print(f"🎯 Target department: {target_dept['nom']} (ID: {target_dept['id']})")
            
            # Test the department update
            print("\n🔄 Testing department update...")
            update_data = {
                "new_department_id": target_dept['id']
            }
            
            update_response = await client.put(
                f"{base_url}/teacher/profile/department", 
                json=update_data,
                headers=headers
            )
            
            if update_response.status_code == 200:
                update_result = update_response.json()
                print("✅ Department update successful!")
                print(f"   New department: {update_result.get('new_department', {}).get('nom')}")
                print(f"   Message: {update_result.get('message')}")
            else:
                print(f"❌ Department update failed: {update_response.status_code}")
                print(f"Response: {update_response.text}")
                
            print("\n🎉 Department update test completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_department_update())