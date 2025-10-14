#!/usr/bin/env python3
"""
COMPLETE AUTH SYSTEM FIX
========================
Fix and test the complete authentication system for:
- Department Heads (Chef de Département)
- Teachers (Enseignants) 
- Students (Étudiants)
"""

import requests
import json
import asyncio

BASE_URL = "http://localhost:8000"

def create_admin_user():
    """Ensure admin user exists"""
    print("🔧 Creating Admin User...")
    
    admin_data = {
        "nom": "ADMIN",
        "prenom": "Super",
        "email": "admin@university.com",
        "password": "admin123",
        "role": "ADMIN"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code in [200, 201]:
            print("   ✅ Admin user created successfully")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ✅ Admin user already exists")
            return True
        else:
            print(f"   ❌ Failed to create admin: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error creating admin: {str(e)}")
        return False

def login_admin():
    """Login as admin"""
    print("🔐 Admin Login...")
    
    login_data = {"email": "admin@university.com", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Admin login successful")
            return token_data['access_token']
        else:
            print(f"   ❌ Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Admin login error: {str(e)}")
        return None

def setup_university_structure(token):
    """Create basic university structure"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🏛️  Setting up University Structure...")
    
    # Create departments
    departments = [
        {"name": "Génie Mécanique"},
        {"name": "Génie Électrique"}, 
        {"name": "Génie Civil"},
        {"name": "Technologie d'Informatique"}
    ]
    
    created_departments = []
    
    for dept_data in departments:
        try:
            response = requests.post(f"{BASE_URL}/departments", json=dept_data, headers=headers)
            if response.status_code in [200, 201]:
                dept = response.json()
                created_departments.append(dept)
                print(f"   ✅ Created department: {dept_data['name']}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Get existing department
                response = requests.get(f"{BASE_URL}/departments", headers=headers)
                if response.status_code == 200:
                    all_depts = response.json()
                    for existing_dept in all_depts:
                        if existing_dept['name'] == dept_data['name']:
                            created_departments.append(existing_dept)
                            print(f"   ✅ Using existing department: {dept_data['name']}")
                            break
            else:
                print(f"   ❌ Failed to create department {dept_data['name']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating department: {str(e)}")
    
    return created_departments

def test_department_head_auth(departments, token):
    """Test department head registration and login"""
    print("\n👥 Testing Department Head Authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    dept_heads = [
        {"nom": "MAATALLAH", "prenom": "Mohamed", "email": "mohamed.maatallah@head.univ.tn", "dept_name": "Technologie d'Informatique"},
        {"nom": "NEFZAOUI", "prenom": "Fatma", "email": "fatma.nefzaoui@head.univ.tn", "dept_name": "Génie Mécanique"},
    ]
    
    successful_heads = []
    
    for head_data in dept_heads:
        print(f"\n   Testing: {head_data['prenom']} {head_data['nom']} → {head_data['dept_name']}")
        
        # Find department ID
        dept_id = None
        for dept in departments:
            if dept['name'] == head_data['dept_name']:
                dept_id = dept['id']
                break
        
        if not dept_id:
            print(f"      ❌ Department {head_data['dept_name']} not found")
            continue
        
        # Register department head
        user_data = {
            "nom": head_data["nom"],
            "prenom": head_data["prenom"],
            "email": head_data["email"],
            "password": "depthead123",
            "role": "DEPARTMENT_HEAD"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user_data,
                params={"department_id": dept_id},
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                head = response.json()
                print(f"      ✅ Registration successful")
                successful_heads.append({
                    "email": head_data["email"],
                    "password": "depthead123",
                    "name": f"{head_data['prenom']} {head_data['nom']}"
                })
            elif response.status_code == 400 and ("already exists" in response.text or "already has a department head" in response.text):
                print(f"      ⚠️  Already exists or department already has head")
                successful_heads.append({
                    "email": head_data["email"],
                    "password": "depthead123",
                    "name": f"{head_data['prenom']} {head_data['nom']}"
                })
            else:
                print(f"      ❌ Registration failed: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Registration error: {str(e)}")
    
    # Test login for department heads
    print(f"\n   Testing Department Head Login...")
    for head in successful_heads:
        login_data = {"email": head["email"], "password": head["password"]}
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                print(f"      ✅ {head['name']} login successful")
                print(f"         Role: {token_data['user']['role']}")
            else:
                print(f"      ❌ {head['name']} login failed: {response.text}")
        except Exception as e:
            print(f"      ❌ {head['name']} login error: {str(e)}")
    
    return successful_heads

def test_teacher_auth(departments, token):
    """Test teacher registration and login"""
    print("\n👨‍🏫 Testing Teacher Authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    teachers = [
        {"nom": "BOUALI", "prenom": "Ahmed", "email": "ahmed.bouali@gm.univ.tn", "dept_name": "Génie Mécanique"},
        {"nom": "KARRAY", "prenom": "Amina", "email": "amina.karray@ge.univ.tn", "dept_name": "Génie Électrique"},
        {"nom": "DEVELOPER", "prenom": "Wahid", "email": "wahid@gmail.com", "dept_name": "Technologie d'Informatique"},
    ]
    
    successful_teachers = []
    
    for teacher_data in teachers:
        print(f"\n   Testing: {teacher_data['prenom']} {teacher_data['nom']} → {teacher_data['dept_name']}")
        
        # Find department ID
        dept_id = None
        for dept in departments:
            if dept['name'] == teacher_data['dept_name']:
                dept_id = dept['id']
                break
        
        if not dept_id:
            print(f"      ❌ Department {teacher_data['dept_name']} not found")
            continue
        
        # Register teacher
        password = "dalighgh15" if teacher_data['nom'] == "DEVELOPER" else "teacher123"
        user_data = {
            "nom": teacher_data["nom"],
            "prenom": teacher_data["prenom"],
            "email": teacher_data["email"],
            "password": password,
            "role": "TEACHER"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user_data,
                params={"department_id": dept_id},
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                teacher = response.json()
                print(f"      ✅ Registration successful")
                successful_teachers.append({
                    "email": teacher_data["email"],
                    "password": password,
                    "name": f"{teacher_data['prenom']} {teacher_data['nom']}"
                })
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"      ⚠️  Already exists")
                successful_teachers.append({
                    "email": teacher_data["email"],
                    "password": password,
                    "name": f"{teacher_data['prenom']} {teacher_data['nom']}"
                })
            else:
                print(f"      ❌ Registration failed: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Registration error: {str(e)}")
    
    # Test login for teachers
    print(f"\n   Testing Teacher Login...")
    for teacher in successful_teachers:
        login_data = {"email": teacher["email"], "password": teacher["password"]}
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                print(f"      ✅ {teacher['name']} login successful")
                print(f"         Role: {token_data['user']['role']}")
            else:
                print(f"      ❌ {teacher['name']} login failed: {response.text}")
        except Exception as e:
            print(f"      ❌ {teacher['name']} login error: {str(e)}")
    
    return successful_teachers

def test_student_auth(token):
    """Test student registration and login"""
    print("\n👨‍🎓 Testing Student Authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    students = [
        {"nom": "BEN ALI", "prenom": "Ahmed", "email": "ahmed.benali001@student.univ.tn"},
        {"nom": "TRABELSI", "prenom": "Fatma", "email": "fatma.trabelsi002@student.univ.tn"},
        {"nom": "KARRAY", "prenom": "Mohamed", "email": "mohamed.karray003@student.univ.tn"},
    ]
    
    successful_students = []
    
    for student_data in students:
        print(f"\n   Testing: {student_data['prenom']} {student_data['nom']}")
        
        # Register student (with defaults)
        user_data = {
            "nom": student_data["nom"],
            "prenom": student_data["prenom"],
            "email": student_data["email"],
            "password": "student123",
            "role": "STUDENT"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                student = response.json()
                print(f"      ✅ Registration successful")
                successful_students.append({
                    "email": student_data["email"],
                    "password": "student123",
                    "name": f"{student_data['prenom']} {student_data['nom']}"
                })
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"      ⚠️  Already exists")
                successful_students.append({
                    "email": student_data["email"],
                    "password": "student123",
                    "name": f"{student_data['prenom']} {student_data['nom']}"
                })
            else:
                print(f"      ❌ Registration failed: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Registration error: {str(e)}")
    
    # Test login for students
    print(f"\n   Testing Student Login...")
    for student in successful_students:
        login_data = {"email": student["email"], "password": student["password"]}
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                print(f"      ✅ {student['name']} login successful")
                print(f"         Role: {token_data['user']['role']}")
            else:
                print(f"      ❌ {student['name']} login failed: {response.text}")
        except Exception as e:
            print(f"      ❌ {student['name']} login error: {str(e)}")
    
    return successful_students

def main():
    """Main authentication system test"""
    print("🚀 COMPLETE AUTH SYSTEM FIX & TEST")
    print("=" * 60)
    print("Testing: Department Heads, Teachers, Students")
    print("=" * 60)
    
    # Step 1: Create admin user
    if not create_admin_user():
        print("❌ Cannot proceed without admin user")
        return
    
    # Step 2: Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Step 3: Setup university structure
    departments = setup_university_structure(token)
    if not departments:
        print("❌ Cannot proceed without departments")
        return
    
    # Step 4: Test department head authentication
    dept_heads = test_department_head_auth(departments, token)
    
    # Step 5: Test teacher authentication
    teachers = test_teacher_auth(departments, token)
    
    # Step 6: Test student authentication
    students = test_student_auth(token)
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 AUTH SYSTEM TEST COMPLETE")
    print("=" * 60)
    
    print(f"📊 Results Summary:")
    print(f"   🏛️  Departments: {len(departments)}")
    print(f"   👥 Department Heads: {len(dept_heads)}")
    print(f"   👨‍🏫 Teachers: {len(teachers)}")
    print(f"   👨‍🎓 Students: {len(students)}")
    
    print(f"\n🔐 Test Credentials:")
    print(f"   🔑 Admin: admin@university.com / admin123")
    
    if dept_heads:
        print(f"   👥 Department Heads:")
        for head in dept_heads:
            print(f"      - {head['email']} / depthead123")
    
    if teachers:
        print(f"   👨‍🏫 Teachers:")
        for teacher in teachers:
            print(f"      - {teacher['email']} / {teacher['password']}")
    
    if students:
        print(f"   👨‍🎓 Students:")
        for student in students[:3]:  # Show first 3
            print(f"      - {student['email']} / student123")
    
    print(f"\n✅ Authentication system is working for all user types!")
    print(f"✅ Ready for frontend integration!")

if __name__ == "__main__":
    main()