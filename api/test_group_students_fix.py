#!/usr/bin/env python3

import asyncio
import httpx

async def test_group_students():
    """Test the specific endpoint that was failing"""
    print("=== TESTING GROUP STUDENTS ENDPOINT ===")
    
    base_url = "http://localhost:8000"
    
    # Login credentials
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Login
            print("1. 🔑 Logging in...")
            login_response = await client.post(
                f"{base_url}/auth/login",
                json=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed")
                return
            
            token_data = login_response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print("✅ Login successful!")
            
            # 2. Get groups first
            print("\n2. 👥 Getting groups...")
            groups_response = await client.get(f"{base_url}/teacher/groups", headers=headers)
            if groups_response.status_code != 200:
                print(f"❌ Groups failed: {groups_response.status_code}")
                return
            
            groups = groups_response.json()
            print(f"✅ Found {len(groups)} groups")
            
            # 3. Test each group's students endpoint
            for group in groups:
                group_id = group['id']
                group_name = group['nom']
                print(f"\n3. 👨‍🎓 Testing students for {group_name} (ID: {group_id})...")
                
                students_response = await client.get(
                    f"{base_url}/teacher/groups/{group_id}/students",
                    headers=headers
                )
                
                if students_response.status_code == 200:
                    group_details = students_response.json()
                    students = group_details['students']
                    print(f"✅ Success! Found {len(students)} students in {group_name}")
                    
                    # Show first few students
                    for student in students[:3]:
                        print(f"   - {student['prenom']} {student['nom']} ({student['email']})")
                    if len(students) > 3:
                        print(f"   ... and {len(students) - 3} more students")
                else:
                    print(f"❌ Failed for {group_name}: {students_response.status_code}")
                    print(f"   Error: {students_response.text}")
            
            print(f"\n🎉 GROUP STUDENTS TEST COMPLETE!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_group_students())