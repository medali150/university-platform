#!/usr/bin/env python3
"""
Check and fix student user linking
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def check_and_fix_student_linking():
    """Check if student user is properly linked to student record"""
    
    print("🔍 CHECKING STUDENT USER LINKING")
    print("=" * 50)
    
    # Login as admin to check database
    admin_creds = {"email": "wahid@gmail.com", "password": "dalighgh15"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=admin_creds)
    
    if login_response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if we can get all users to find our student
    try:
        users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            
            # Find our test student
            test_student_user = None
            for user in users:
                if user.get("email") == "ahmed.student@university.edu":
                    test_student_user = user
                    break
            
            if test_student_user:
                print(f"✅ Found test student user:")
                print(f"   ID: {test_student_user.get('id')}")
                print(f"   Email: {test_student_user.get('email')}")
                print(f"   Role: {test_student_user.get('role')}")
                print(f"   Etudiant ID: {test_student_user.get('etudiant_id', 'MISSING!')}")
                
                if not test_student_user.get('etudiant_id'):
                    print("⚠️ Student user is missing etudiant_id link!")
                    print("   This explains why the student endpoints are failing.")
                    
                    # Check if there's an etudiant record with this email
                    print("\n🔍 Checking for student records...")
                    students_response = requests.get(f"{BASE_URL}/admin/students", headers=headers)
                    if students_response.status_code == 200:
                        students = students_response.json()
                        
                        matching_student = None
                        for student in students:
                            if student.get("email") == "ahmed.student@university.edu":
                                matching_student = student
                                break
                        
                        if matching_student:
                            print(f"✅ Found matching student record:")
                            print(f"   Student ID: {matching_student.get('id')}")
                            print(f"   Name: {matching_student.get('prenom')} {matching_student.get('nom')}")
                            print(f"   Group: {matching_student.get('groupe', {}).get('nom', 'No group')}")
                            
                            print("\n💡 Solution: Link the user to the student record")
                            print(f"   UPDATE utilisateur SET etudiant_id = '{matching_student.get('id')}' WHERE id = '{test_student_user.get('id')}';")
                        else:
                            print("❌ No matching student record found")
                            print("   Need to create a student record for this user")
                    else:
                        print(f"❌ Could not fetch students: {students_response.status_code}")
                else:
                    print("✅ Student user is properly linked!")
            else:
                print("❌ Test student user not found in database")
        else:
            print(f"❌ Could not fetch users: {users_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_and_fix_student_linking()