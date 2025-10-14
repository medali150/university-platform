#!/usr/bin/env python3
"""
IMPROVED UNIVERSITY SETUP WITH FIXED AUTH
================================
Create university data using the improved authentication system:
- Remove math department
- Create proper department structure
- Use new auth logic for teachers (with department selection)
- Use new auth logic for students (with specialty/group selection)
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000"

# University structure with proper departments
UNIVERSITY_STRUCTURE = {
    "Génie Mécanique": {
        "code": "GM",
        "teachers": [
            {"prenom": "Ahmed", "nom": "BOUALI", "email": "ahmed.bouali@gm.univ.tn"},
            {"prenom": "Leila", "nom": "MEZGHANI", "email": "leila.mezghani@gm.univ.tn"},
            {"prenom": "Karim", "nom": "TRABELSI", "email": "karim.trabelsi@gm.univ.tn"},
        ]
    },
    "Génie Électrique": {
        "code": "GE", 
        "teachers": [
            {"prenom": "Amina", "nom": "KARRAY", "email": "amina.karray@ge.univ.tn"},
            {"prenom": "Riadh", "nom": "MAHJOUB", "email": "riadh.mahjoub@ge.univ.tn"},
            {"prenom": "Sarra", "nom": "HAMDI", "email": "sarra.hamdi@ge.univ.tn"},
        ]
    },
    "Génie Civil": {
        "code": "GC",
        "teachers": [
            {"prenom": "Youssef", "nom": "NEFZAOUI", "email": "youssef.nefzaoui@gc.univ.tn"},
            {"prenom": "Fatma", "nom": "MAATALLAH", "email": "fatma.maatallah@gc.univ.tn"},
            {"prenom": "Slim", "nom": "CHAOUACHI", "email": "slim.chaouachi@gc.univ.tn"},
        ]
    },
    "Technologie d'Informatique": {
        "code": "TI",
        "teachers": [
            {"prenom": "Wahid", "nom": "DEVELOPER", "email": "wahid@gmail.com"},
            {"prenom": "Mariam", "nom": "TECHNO", "email": "mariam.techno@ti.univ.tn"},
            {"prenom": "Tarek", "nom": "NETWORK", "email": "tarek.network@ti.univ.tn"},
            {"prenom": "Hiba", "nom": "AIDEV", "email": "hiba.ai@ti.univ.tn"},
        ]
    }
}

def login_admin():
    """Login as admin and get token"""
    login_data = {"email": "admin@university.com", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Admin authentication successful")
            return token_data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None

def get_auth_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def setup_university_with_improved_auth(token):
    """Setup university using improved auth system"""
    headers = get_auth_headers(token)
    
    print("🏛️  Setting up University with Improved Auth System...")
    
    # Step 1: Get existing departments
    print("\n📚 Getting Departments...")
    try:
        response = requests.get(f"{BASE_URL}/auth/departments", headers=headers)
        if response.status_code == 200:
            departments_data = response.json()["departments"]
            departments = {dept["nom"]: dept for dept in departments_data}
            print(f"   ✅ Found {len(departments)} departments")
            
            # Show which departments we have
            for dept_name in departments:
                print(f"      - {dept_name}")
        else:
            print(f"   ❌ Failed to get departments: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error getting departments: {str(e)}")
        return
    
    # Step 2: Get specialties and groups
    print("\n🎓 Getting Academic Structure...")
    try:
        spec_response = requests.get(f"{BASE_URL}/auth/specialties", headers=headers)
        group_response = requests.get(f"{BASE_URL}/auth/groups", headers=headers)
        
        specialties = []
        groups = []
        
        if spec_response.status_code == 200:
            specialties = spec_response.json()["specialties"]
            print(f"   ✅ Found {len(specialties)} specialties")
        
        if group_response.status_code == 200:
            groups = group_response.json()["groups"]
            print(f"   ✅ Found {len(groups)} groups")
            
    except Exception as e:
        print(f"   ❌ Error getting academic structure: {str(e)}")
        specialties = []
        groups = []
    
    # Step 3: Create teachers with department selection
    print("\n👨‍🏫 Creating Teachers with Department Selection...")
    created_teachers = {}
    
    for dept_name, dept_config in UNIVERSITY_STRUCTURE.items():
        if dept_name in departments:
            dept_id = departments[dept_name]["id"]
            print(f"\n   Creating teachers for {dept_name}:")
            
            created_teachers[dept_name] = []
            
            for teacher_data in dept_config["teachers"]:
                user_data = {
                    "prenom": teacher_data["prenom"],
                    "nom": teacher_data["nom"],
                    "email": teacher_data["email"],
                    "password": "teacher123" if teacher_data["nom"] != "DEVELOPER" else "dalighgh15",
                    "role": "TEACHER"
                }
                
                try:
                    # Use improved auth with department selection
                    response = requests.post(
                        f"{BASE_URL}/auth/register",
                        json=user_data,
                        params={"department_id": dept_id},
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        teacher = response.json()
                        created_teachers[dept_name].append(teacher)
                        print(f"      ✅ Created: {teacher_data['prenom']} {teacher_data['nom']} → {dept_name}")
                    elif response.status_code == 400 and "already exists" in response.text:
                        print(f"      ⚠️  Exists: {teacher_data['prenom']} {teacher_data['nom']}")
                    else:
                        print(f"      ❌ Failed: {teacher_data['prenom']} {teacher_data['nom']} - {response.text}")
                        
                except Exception as e:
                    print(f"      ❌ Error creating teacher: {str(e)}")
        else:
            print(f"   ⚠️  Department {dept_name} not found, skipping teachers")
    
    # Step 4: Create students with specialty/group selection
    print("\n👨‍🎓 Creating Students with Academic Structure...")
    
    first_names = ["Ahmed", "Mohamed", "Ali", "Youssef", "Fatma", "Amina", "Leila", "Sarra", "Omar", "Karim"]
    last_names = ["BEN ALI", "TRABELSI", "MEZGHANI", "KARRAY", "BOUALI", "MAHJOUB", "SALEM", "NEFZAOUI"]
    
    created_students = []
    students_to_create = 50  # Create 50 students
    
    for i in range(students_to_create):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{i+1:03d}@student.univ.tn"
        
        user_data = {
            "prenom": first_name,
            "nom": last_name,
            "email": email,
            "password": "student123",
            "role": "STUDENT"
        }
        
        try:
            # Create student with or without specific specialty/group
            params = {}
            if specialties and groups and i % 3 == 0:  # Every 3rd student gets specific assignment
                params["specialty_id"] = random.choice(specialties)["id"]
                params["group_id"] = random.choice(groups)["id"]
            
            if params:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=user_data,
                    params=params,
                    headers=headers
                )
            else:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=user_data,
                    headers=headers
                )
            
            if response.status_code in [200, 201]:
                student = response.json()
                created_students.append(student)
                if (i + 1) % 10 == 0:  # Progress every 10 students
                    print(f"      ✅ Created {i + 1}/{students_to_create} students...")
            elif response.status_code == 400 and "already exists" in response.text:
                continue  # Skip existing
                
        except Exception as e:
            if i < 5:  # Only show first few errors
                print(f"      ❌ Student creation error: {str(e)}")
    
    print(f"   ✅ Successfully created {len(created_students)} students")
    
    # Step 5: Create department heads for remaining departments
    print("\n👥 Creating Department Heads...")
    
    dept_head_candidates = [
        {"nom": "MAATALLAH", "prenom": "Mohamed", "email": "mohamed.maatallah@head.univ.tn", "dept": "Technologie d'Informatique"},
        {"nom": "NEFZAOUI", "prenom": "Fatma", "email": "fatma.nefzaoui@head.univ.tn", "dept": "Génie Mécanique"},
        {"nom": "HAMDI", "prenom": "Ahmed", "email": "ahmed.hamdi@head.univ.tn", "dept": "Génie Électrique"},
        {"nom": "ARFAOUI", "prenom": "Sarra", "email": "sarra.arfaoui@head.univ.tn", "dept": "Génie Civil"}
    ]
    
    created_heads = []
    
    for head_data in dept_head_candidates:
        if head_data["dept"] in departments:
            dept_id = departments[head_data["dept"]]["id"]
            
            user_data = {
                "prenom": head_data["prenom"],
                "nom": head_data["nom"],
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
                    dept_head = response.json()
                    created_heads.append(dept_head)
                    print(f"   ✅ Created department head: {head_data['prenom']} {head_data['nom']} → {head_data['dept']}")
                elif response.status_code == 400 and "already has a department head" in response.text:
                    print(f"   ⚠️  Department {head_data['dept']} already has a head")
                elif response.status_code == 400 and "already exists" in response.text:
                    print(f"   ⚠️  User {head_data['prenom']} {head_data['nom']} already exists")
                else:
                    print(f"   ❌ Failed to create head for {head_data['dept']}: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error creating department head: {str(e)}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 IMPROVED UNIVERSITY SETUP COMPLETE!")
    print("=" * 60)
    
    total_teachers = sum(len(teachers) for teachers in created_teachers.values())
    
    print(f"📊 Created with Improved Auth System:")
    print(f"   🏛️  Using Departments: {len(departments)}")
    print(f"   👨‍🏫 Teachers (with dept selection): {total_teachers}")
    print(f"   👨‍🎓 Students (with academic structure): {len(created_students)}")
    print(f"   👥 Department Heads: {len(created_heads)}")
    
    print(f"\n🔧 Auth System Improvements:")
    print("   ✅ Teachers require department selection")
    print("   ✅ Students can specify specialty/group or use defaults")
    print("   ✅ Department heads require department selection")
    print("   ✅ Comprehensive validation and error handling")
    
    print(f"\n🔐 Login Credentials:")
    print("   🔑 Admin: admin@university.com / admin123")
    print("   👥 Department Heads: [email] / depthead123")
    print("   👨‍🏫 Teachers: [email] / teacher123 (except wahid@gmail.com / dalighgh15)")
    print("   👨‍🎓 Students: [email] / student123")
    
    print(f"\n✅ All 3 applications ready with improved auth!")

def main():
    print("🚀 IMPROVED UNIVERSITY SETUP")
    print("Using Fixed Authentication Logic")
    print("=" * 50)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        return
    
    # Setup university with improved auth
    setup_university_with_improved_auth(token)

if __name__ == "__main__":
    main()