#!/usr/bin/env python3
"""Test script to verify subjects CRUD endpoints are working properly"""

import asyncio
import httpx
import json

async def test_subjects_endpoints():
    """Test the subjects endpoints after fixing the database model issues"""
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔍 Testing subjects endpoints...")
            
            # Test 1: Get subjects without authentication (should get 401)
            print("\n1. Testing GET /department-head/subjects/ without auth...")
            response = await client.get('http://localhost:8000/department-head/subjects/')
            print(f"   Status: {response.status_code} (expected 401)")
            
            # Test 2: Try to login with admin credentials
            print("\n2. Testing admin login...")
            login_data = {
                'nom_utilisateur': 'admin',
                'mot_de_passe': 'admin123'
            }
            
            login_response = await client.post('http://localhost:8000/auth/login', json=login_data)
            print(f"   Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get('access_token')
                
                if token:
                    print("   ✅ Login successful, got token")
                    
                    # Test 3: Get subjects with authentication
                    print("\n3. Testing GET /department-head/subjects/ with auth...")
                    headers = {'Authorization': f'Bearer {token}'}
                    subjects_response = await client.get('http://localhost:8000/department-head/subjects/', headers=headers)
                    
                    print(f"   Status: {subjects_response.status_code}")
                    
                    if subjects_response.status_code == 200:
                        subjects_data = subjects_response.json()
                        print(f"   ✅ Success! Got {len(subjects_data.get('subjects', []))} subjects")
                        print(f"   Total pages: {subjects_data.get('totalPages', 0)}")
                        
                        # Show first subject if any
                        subjects = subjects_data.get('subjects', [])
                        if subjects:
                            first_subject = subjects[0]
                            print(f"   First subject: {first_subject.get('nom', 'N/A')}")
                    
                    elif subjects_response.status_code == 500:
                        print(f"   ❌ Server error: {subjects_response.text}")
                    else:
                        print(f"   Status {subjects_response.status_code}: {subjects_response.text}")
                        
                    # Test 4: Get helper endpoints
                    print("\n4. Testing helper endpoints...")
                    
                    # Test levels helper
                    levels_response = await client.get('http://localhost:8000/department-head/subjects/helpers/levels', headers=headers)
                    print(f"   Levels helper status: {levels_response.status_code}")
                    
                    # Test teachers helper  
                    teachers_response = await client.get('http://localhost:8000/department-head/subjects/helpers/teachers', headers=headers)
                    print(f"   Teachers helper status: {teachers_response.status_code}")
                    
                else:
                    print("   ❌ No token received")
            else:
                print(f"   ❌ Login failed: {login_response.text}")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subjects_endpoints())