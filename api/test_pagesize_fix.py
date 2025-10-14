#!/usr/bin/env python3
"""
Test script to verify the pageSize limit fix
"""

import requests

def test_pagesize_limit():
    """Test that pageSize=1000 is now accepted"""
    
    try:
        # Login as department head
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={
                "email": "test.depthead@university.com",
                "password": "test123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test pageSize=1000
        print("🧪 Testing pageSize=1000...")
        response = requests.get(
            "http://localhost:8000/department-head/subjects/?page=1&pageSize=1000",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved {len(data.get('data', []))} subjects")
            print(f"Total: {data.get('total', 0)}")
            print(f"Page: {data.get('page', 0)}")
            print(f"PageSize: {data.get('pageSize', 0)}")
            print(f"TotalPages: {data.get('totalPages', 0)}")
            
            # Test statistics calculation
            subjects = data.get('data', [])
            if subjects:
                print(f"\n📊 Statistics can be calculated:")
                print(f"- Total subjects: {len(subjects)}")
                
                # Count by level
                levels = {}
                departments = {}
                teachers = {}
                
                for subject in subjects:
                    level_name = subject.get('level', {}).get('name', 'Non spécifié')
                    levels[level_name] = levels.get(level_name, 0) + 1
                    
                    dept_name = subject.get('level', {}).get('specialty', {}).get('department', {}).get('name', 'Non spécifié')
                    departments[dept_name] = departments.get(dept_name, 0) + 1
                    
                    teacher = subject.get('teacher')
                    if teacher and teacher.get('name'):
                        teacher_name = teacher['name']
                    else:
                        teacher_name = 'Non assigné'
                    teachers[teacher_name] = teachers.get(teacher_name, 0) + 1
                
                print(f"- Levels: {len(levels)} unique levels")
                print(f"- Departments: {len(departments)} unique departments")
                print(f"- Teachers: {len(teachers)} unique teachers")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_pagesize_limit()