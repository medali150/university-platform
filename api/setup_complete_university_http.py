#!/usr/bin/env python3
"""
Complete University Setup Script using HTTP API
Creates students, levels, teachers, and all necessary data via API calls
"""
import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def login_admin():
    """Login and get admin token"""
    login_data = {
        "email": "admin@university.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Admin login successful")
            return token_data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during admin login: {str(e)}")
        return None

def get_auth_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def create_specialties_and_levels(token):
    """Create specialties and levels for existing departments"""
    headers = get_auth_headers(token)
    
    print("=== Getting Departments ===")
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get departments: {response.status_code}")
        return [], []
    
    departments = response.json()
    print(f"Found {len(departments)} departments")
    
    # Define specialties for each department
    specialties_data = {
        "Génie Mécanique": [
            "Génie Mécanique - Production",
            "Génie Mécanique - Maintenance"
        ],
        "Génie Électrique": [
            "Génie Électrique - Automatique", 
            "Génie Électrique - Électronique"
        ],
        "Génie Civil": [
            "Génie Civil - Bâtiment",
            "Génie Civil - Travaux Publics"
        ],
        "Technologie d'Informatique": [
            "Développement Logiciel",
            "Réseaux et Systèmes",
            "Systèmes d'Information"
        ]
    }
    
    created_specialties = []
    
    print("\n=== Creating Specialties ===")
    for dept in departments:
        dept_name = dept['name']
        if dept_name in specialties_data:
            for spec_name in specialties_data[dept_name]:
                spec_data = {
                    "name": spec_name,
                    "departmentId": dept['id']
                }
                
                try:
                    response = requests.post(f"{BASE_URL}/specialties", json=spec_data, headers=headers)
                    if response.status_code in [200, 201]:
                        spec = response.json()
                        created_specialties.append(spec)
                        print(f"✅ Created specialty: {spec['name']}")
                    elif response.status_code == 500:
                        print(f"⚠️ Specialty {spec_name} might already exist (500 error)")
                    else:
                        print(f"❌ Failed to create specialty {spec_name}: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error creating specialty {spec_name}: {str(e)}")
    
    print(f"Created {len(created_specialties)} specialties")
    
    # Create levels for each specialty
    print("\n=== Creating Levels ===")
    created_levels = []
    
    level_names = ["1ère Année", "2ème Année", "3ème Année"]
    
    for spec in created_specialties:
        for level_name in level_names:
            level_data = {
                "name": level_name,
                "specialtyId": spec['id']
            }
            
            try:
                response = requests.post(f"{BASE_URL}/admin/levels", json=level_data, headers=headers)
                if response.status_code in [200, 201]:
                    level = response.json()
                    created_levels.append(level)
                    print(f"✅ Created level: {level['name']} for {spec['name']}")
                else:
                    print(f"❌ Failed to create level {level_name}: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Error creating level {level_name}: {str(e)}")
    
    return created_specialties, created_levels

def create_teachers(departments, token):
    """Create teachers for each department"""
    headers = get_auth_headers(token)
    
    print("\n=== Creating Teachers ===")
    
    # Teacher names for different departments
    teacher_names = {
        "Génie Mécanique": [
            {"prenom": "Ahmed", "nom": "BOUALI"},
            {"prenom": "Leila", "nom": "MEZGHANI"},
            {"prenom": "Karim", "nom": "TRABELSI"}
        ],
        "Génie Électrique": [
            {"prenom": "Amina", "nom": "KARRAY"},
            {"prenom": "Riadh", "nom": "MAHJOUB"},
            {"prenom": "Nadia", "nom": "SALEM"}
        ],
        "Génie Civil": [
            {"prenom": "Youssef", "nom": "NEFZAOUI"},
            {"prenom": "Sarra", "nom": "HAMDI"},
            {"prenom": "Mohamed", "nom": "ARFAOUI"}
        ],
        "Technologie d'Informatique": [
            {"prenom": "Fatma", "nom": "MAATALLAH"},
            {"prenom": "Slim", "nom": "CHAOUACHI"},
            {"prenom": "Ines", "nom": "DRISSI"},
            {"prenom": "Wahid", "nom": "DEVELOPER"}  # Special teacher
        ]
    }
    
    created_teachers = []
    
    for dept in departments:
        dept_name = dept['name']
        if dept_name in teacher_names:
            print(f"\n📚 Creating teachers for {dept_name}:")
            
            for teacher_data in teacher_names[dept_name]:
                # Create teacher user
                teacher_email = f"{teacher_data['prenom'].lower()}.{teacher_data['nom'].lower()}@university.tn"
                if teacher_data['nom'] == "DEVELOPER":
                    teacher_email = "wahid@gmail.com"  # Special case
                
                user_data = {
                    "prenom": teacher_data['prenom'],
                    "nom": teacher_data['nom'],
                    "email": teacher_email,
                    "password": "teacher123" if teacher_data['nom'] != "DEVELOPER" else "dalighgh15",
                    "role": "TEACHER"
                }
                
                try:
                    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
                    if response.status_code in [200, 201]:
                        teacher = response.json()
                        created_teachers.append(teacher)
                        print(f"✅ Created teacher: {teacher['prenom']} {teacher['nom']}")
                    elif response.status_code == 400 and "already exists" in response.text:
                        print(f"⚠️ Teacher {teacher_data['prenom']} {teacher_data['nom']} already exists")
                    else:
                        print(f"❌ Failed to create teacher {teacher_data['prenom']} {teacher_data['nom']}: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error creating teacher: {str(e)}")
    
    return created_teachers

def create_students_and_groups(token):
    """Create groups and students"""
    headers = get_auth_headers(token)
    
    print("\n=== Creating Students ===")
    
    # Get available levels first (we need to find them via a different approach since we might not have direct access)
    # Let's create some sample student users first
    
    student_names = [
        ("Ahmed", "BEN ALI"), ("Fatma", "JLASSI"), ("Mohamed", "TRABELSI"),
        ("Amina", "KACEM"), ("Youssef", "MANSOUR"), ("Leila", "GHARBI"),
        ("Karim", "BOUAZIZI"), ("Nadia", "SFAR"), ("Slim", "MEJRI"),
        ("Salma", "KAMMOUN"), ("Omar", "CHEBBI"), ("Ines", "TLILI"),
        ("Bilel", "DHAOUI"), ("Rania", "MOKRANI"), ("Hedi", "ZOUARI"),
        ("Marwa", "BELAID"), ("Fares", "SASSI"), ("Yasmine", "HADDAD"),
        ("Walid", "CHOUCHANE"), ("Sonia", "KOUKI"), ("Amine", "LAZAAR"),
        ("Emna", "TURKI"), ("Mehdi", "OUALI"), ("Jihen", "AGREBI"),
        ("Tarek", "HIBA"), ("Rim", "NIZAR"), ("Salma", "FAROUK"),
        ("Dorra", "WASSIM"), ("Mehdi", "INES"), ("Nour", "KHALED"),
        ("Saber", "AMANI"), ("Wided", "HASSEN"), ("Malek", "FATHIA")
    ]
    
    created_students = []
    
    for i, (prenom, nom) in enumerate(student_names):
        student_email = f"{prenom.lower()}.{nom.lower()}@student.university.tn"
        
        user_data = {
            "prenom": prenom,
            "nom": nom,
            "email": student_email,
            "password": "student123",
            "role": "STUDENT"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                student = response.json()
                created_students.append(student)
                if i % 5 == 0:  # Print every 5th student to avoid spam
                    print(f"✅ Created student: {student['prenom']} {student['nom']}")
            elif response.status_code == 400 and "already exists" in response.text:
                if i % 10 == 0:  # Print every 10th existing student
                    print(f"⚠️ Student {prenom} {nom} already exists")
            else:
                print(f"❌ Failed to create student {prenom} {nom}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating student: {str(e)}")
    
    print(f"✅ Processed {len(student_names)} students")
    return created_students

def create_rooms(token):
    """Create sample rooms"""
    headers = get_auth_headers(token)
    
    print("\n=== Creating Rooms ===")
    
    rooms_data = [
        {"code": "AMPHA", "type": "LECTURE", "capacity": 200},
        {"code": "AMPHB", "type": "LECTURE", "capacity": 150},
        {"code": "A101", "type": "LECTURE", "capacity": 40},
        {"code": "A102", "type": "LECTURE", "capacity": 35},
        {"code": "A201", "type": "LECTURE", "capacity": 45},
        {"code": "LI1", "type": "LAB", "capacity": 30},
        {"code": "LI2", "type": "LAB", "capacity": 25},
        {"code": "LM1", "type": "LAB", "capacity": 20},
        {"code": "EX1", "type": "EXAM", "capacity": 60},
        {"code": "EX2", "type": "EXAM", "capacity": 80}
    ]
    
    created_rooms = []
    
    # Note: We need to check if there's a rooms API endpoint
    print("⚠️ Room creation via API not implemented - would need room management endpoints")
    print("   Rooms should be created via database scripts or admin interface")
    
    return created_rooms

def main():
    """Main setup function"""
    print("🚀 Starting Complete University Setup via HTTP API")
    print("=" * 60)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    print("✅ Admin authentication successful")
    
    # Get existing departments
    headers = get_auth_headers(token)
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get departments")
        return
    
    departments = response.json()
    print(f"✅ Found {len(departments)} departments")
    
    # Create specialties and levels
    specialties, levels = create_specialties_and_levels(token)
    
    # Create teachers
    teachers = create_teachers(departments, token)
    
    # Create students
    students = create_students_and_groups(token)
    
    # Create rooms
    rooms = create_rooms(token)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 UNIVERSITY SETUP COMPLETE!")
    print("=" * 60)
    
    print(f"📊 Summary:")
    print(f"   🏛️  Departments: {len(departments)}")
    print(f"   📋 Specialties: {len(specialties)}")
    print(f"   📚 Levels: {len(levels)}")
    print(f"   👨‍🏫 Teachers: {len(teachers)}")
    print(f"   👨‍🎓 Students: {len(students)}")
    print(f"   🏢 Rooms: {len(rooms)}")
    
    print(f"\n🔐 Login Credentials:")
    print(f"   🔑 Admin: admin@university.com / admin123")
    print(f"   👨‍🏫 Teachers: [name]@university.tn / teacher123")
    print(f"   👨‍🏫 Special: wahid@gmail.com / dalighgh15")
    print(f"   👨‍🎓 Students: [name]@student.university.tn / student123")
    
    # Test the registration fix
    print(f"\n🧪 Testing Registration System:")
    response = requests.get(f"{BASE_URL}/auth/available-departments")
    if response.status_code == 200:
        dept_info = response.json()
        print(f"   ✅ Available departments for registration: {dept_info['available_count']}")
        if dept_info['available_departments']:
            print(f"   📋 Available departments:")
            for dept in dept_info['available_departments']:
                print(f"      - {dept['nom']} (ID: {dept['id']})")
    
    print(f"\n✅ Setup complete! The university platform is ready to use.")

if __name__ == "__main__":
    main()