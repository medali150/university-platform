#!/usr/bin/env python3

import asyncio
import httpx
import json

# API Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
SUBJECTS_URL = f"{BASE_URL}/department-head/subjects/"

async def test_subjects_department_head_logic():
    """Test the subjects CRUD with department head restrictions"""
    
    async with httpx.AsyncClient() as client:
        print("🔐 Testing Department Head Subjects CRUD Logic...")
        
        # Test 1: Login as department head
        print("\n1️⃣ Logging in as department head...")
        login_data = {
            "email": "test.depthead@university.com",
            "password": "test123"
        }
        
        try:
            response = await client.post(LOGIN_URL, json=login_data)
            print(f"Login Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                user_info = result.get("user", {})
                print(f"✅ Login successful!")
                print(f"User: {user_info.get('prenom')} {user_info.get('nom')}")
                print(f"Role: {user_info.get('role')}")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test 2: Get subjects (should only show subjects from their department)
                print("\n2️⃣ Fetching subjects for department head...")
                response = await client.get(SUBJECTS_URL, headers=headers)
                print(f"Get Subjects Status: {response.status_code}")
                
                if response.status_code == 200:
                    subjects_data = response.json()
                    subjects = subjects_data.get("subjects", [])
                    total = subjects_data.get("total", 0)
                    
                    print(f"✅ Found {total} subjects for this department head")
                    for subject in subjects[:3]:  # Show first 3 subjects
                        specialite = subject.get("specialite", {})
                        departement = specialite.get("departement", {})
                        enseignant = subject.get("enseignant", {})
                        
                        print(f"  📚 Subject: {subject.get('nom')}")
                        print(f"     Specialite: {specialite.get('nom')}")
                        print(f"     Department: {departement.get('nom')}")
                        if enseignant:
                            print(f"     Teacher: {enseignant.get('prenom')} {enseignant.get('nom')}")
                        print()
                
                # Test 3: Get specialites for this department head
                print("\n3️⃣ Fetching specialites for department head...")
                response = await client.get(f"{SUBJECTS_URL}specialites", headers=headers)
                print(f"Get Specialites Status: {response.status_code}")
                
                if response.status_code == 200:
                    specialites = response.json()
                    print(f"✅ Found {len(specialites)} specialites in this department")
                    for spec in specialites[:2]:  # Show first 2
                        print(f"  🎯 Specialite: {spec.get('nom')}")
                
                # Test 4: Get teachers for this department head
                print("\n4️⃣ Fetching teachers for department head...")
                response = await client.get(f"{SUBJECTS_URL}enseignants", headers=headers)
                print(f"Get Teachers Status: {response.status_code}")
                
                if response.status_code == 200:
                    teachers = response.json()
                    print(f"✅ Found {len(teachers)} teachers in this department")
                    for teacher in teachers[:2]:  # Show first 2
                        user = teacher.get("utilisateur", {})
                        print(f"  👨‍🏫 Teacher: {teacher.get('prenom')} {teacher.get('nom')}")
                        print(f"      Email: {teacher.get('email')}")
                
                # Test 5: Try to create a subject for their department
                print("\n5️⃣ Testing subject creation (department validation)...")
                if len(specialites) > 0 and len(teachers) > 0:
                    create_data = {
                        "nom": "Test Subject - Department Head Only",
                        "id_specialite": specialites[0]["id"],
                        "id_enseignant": teachers[0]["id"]
                    }
                    
                    response = await client.post(SUBJECTS_URL, json=create_data, headers=headers)
                    print(f"Create Subject Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        new_subject = response.json()
                        print(f"✅ Subject created successfully!")
                        print(f"Subject ID: {new_subject.get('id')}")
                        
                        # Clean up - delete the test subject
                        delete_url = f"{SUBJECTS_URL}{new_subject.get('id')}"
                        await client.delete(delete_url, headers=headers)
                        print("🧹 Test subject cleaned up")
                    else:
                        print(f"❌ Subject creation failed: {response.text}")
                
            else:
                print(f"❌ Login failed: {response.text}")
                
        except httpx.RequestError as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the server is running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_subjects_department_head_logic())