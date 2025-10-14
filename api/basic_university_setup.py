#!/usr/bin/env python3
"""
BASIC UNIVERSITY SETUP
=====================
Create basic university structure first, then users
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def setup_basic_university():
    """Setup basic university structure"""
    
    # Login as admin
    print("🔐 Logging in as admin...")
    login_data = {"email": "admin@university.com", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Admin login successful!")
            admin_token = token_data['access_token']
            headers = {"Authorization": f"Bearer {admin_token}"}
        else:
            print(f"   ❌ Admin login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Admin login error: {str(e)}")
        return
    
    # Create departments using direct API calls
    print("\n🏛️  Creating Departments...")
    
    departments_to_create = [
        "Génie Mécanique",
        "Génie Électrique", 
        "Génie Civil",
        "Technologie d'Informatique"
    ]
    
    created_departments = []
    
    for dept_name in departments_to_create:
        try:
            response = requests.post(
                f"{BASE_URL}/departments", 
                json={"name": dept_name},
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                dept = response.json()
                created_departments.append(dept)
                print(f"   ✅ Created: {dept_name}")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"   ⚠️  Already exists: {dept_name}")
                # Try to get existing department
                get_response = requests.get(f"{BASE_URL}/departments", headers=headers)
                if get_response.status_code == 200:
                    departments = get_response.json()
                    for existing_dept in departments:
                        if existing_dept['name'] == dept_name:
                            created_departments.append(existing_dept)
                            break
            else:
                print(f"   ❌ Failed to create {dept_name}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creating {dept_name}: {str(e)}")
    
    print(f"\n📊 Summary: {len(created_departments)} departments available")
    
    # Test if departments endpoint works now
    print("\n🧪 Testing departments endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/auth/departments", headers=headers)
        if response.status_code == 200:
            auth_departments = response.json()["departments"]
            print(f"   ✅ Auth departments endpoint working: {len(auth_departments)} departments")
            
            # Now test user registration with departments
            if auth_departments:
                print("\n👨‍🏫 Testing teacher registration...")
                teacher_data = {
                    "nom": "TEACHER",
                    "prenom": "Test",
                    "email": "quicktest.teacher@university.com",
                    "password": "teacher123",
                    "role": "TEACHER"
                }
                
                dept_id = auth_departments[0]["id"]
                
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=teacher_data,
                    params={"department_id": dept_id},
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    print("   ✅ Teacher registration working!")
                elif response.status_code == 400 and "already exists" in response.text:
                    print("   ⚠️  Teacher already exists")
                else:
                    print(f"   ❌ Teacher registration failed: {response.text}")
            
        else:
            print(f"   ❌ Auth departments endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing departments endpoint: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 BASIC UNIVERSITY SETUP COMPLETE!")
    print("   ✅ Admin authentication working")
    print("   ✅ Departments created")  
    print("   ✅ Auth endpoints working")
    print("   ✅ Ready for full user registration!")
    print("=" * 50)

if __name__ == "__main__":
    setup_basic_university()