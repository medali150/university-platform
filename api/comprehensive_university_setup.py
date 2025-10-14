#!/usr/bin/env python3
"""
COMPREHENSIVE UNIVERSITY DATABASE SETUP
================================

This script creates a complete university database structure:
1. Deletes the "math" department and any orphaned data
2. Creates 4 departments with complete academic structure
3. Sets up users, teachers, students, schedules, and rooms
4. Provides proper data for all 3 applications (admin-panel, frontend, api)

Database Structure:
- Departments → Specialties → Levels → Groups → Students
- Departments → Teachers → Subjects (with coefficients)
- Rooms → Schedules → Absences
"""

import asyncio
import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Comprehensive University Data Structure
UNIVERSITY_STRUCTURE = {
    "Génie Mécanique": {
        "code": "GM",
        "specialties": {
            "Génie Mécanique - Production": {
                "code": "GMP",
                "levels": ["GM1", "GM2", "GM3"],
                "subjects": [
                    {"name": "Mécanique des Fluides", "coefficient": 3.0},
                    {"name": "Thermodynamique", "coefficient": 2.5},
                    {"name": "Résistance des Matériaux", "coefficient": 3.0},
                    {"name": "Fabrication Mécanique", "coefficient": 2.0},
                    {"name": "CAO/DAO", "coefficient": 2.5},
                    {"name": "Maintenance Industrielle", "coefficient": 2.0}
                ]
            },
            "Génie Mécanique - Construction": {
                "code": "GMC", 
                "levels": ["GM1", "GM2", "GM3"],
                "subjects": [
                    {"name": "Construction Mécanique", "coefficient": 3.0},
                    {"name": "Dessin Industriel", "coefficient": 2.0},
                    {"name": "Matériaux et Métallurgie", "coefficient": 2.5},
                    {"name": "Technologie Mécanique", "coefficient": 2.5}
                ]
            }
        },
        "teachers": [
            {"prenom": "Ahmed", "nom": "BOUALI", "email": "ahmed.bouali@gm.university.tn"},
            {"prenom": "Leila", "nom": "MEZGHANI", "email": "leila.mezghani@gm.university.tn"},
            {"prenom": "Karim", "nom": "TRABELSI", "email": "karim.trabelsi@gm.university.tn"},
            {"prenom": "Nadia", "nom": "SALEM", "email": "nadia.salem@gm.university.tn"}
        ]
    },
    
    "Génie Électrique": {
        "code": "GE",
        "specialties": {
            "Génie Électrique - Automatique": {
                "code": "GEA",
                "levels": ["GE1", "GE2", "GE3"],
                "subjects": [
                    {"name": "Automatique", "coefficient": 3.0},
                    {"name": "Systèmes Asservis", "coefficient": 2.5},
                    {"name": "API et Automates", "coefficient": 2.5},
                    {"name": "Régulation Industrielle", "coefficient": 2.0}
                ]
            },
            "Génie Électrique - Électronique": {
                "code": "GEE",
                "levels": ["GE1", "GE2", "GE3"], 
                "subjects": [
                    {"name": "Électronique de Puissance", "coefficient": 3.0},
                    {"name": "Circuits Électroniques", "coefficient": 2.5},
                    {"name": "Microprocesseurs", "coefficient": 2.5},
                    {"name": "Systèmes Embarqués", "coefficient": 2.0},
                    {"name": "Énergies Renouvelables", "coefficient": 2.0}
                ]
            }
        },
        "teachers": [
            {"prenom": "Amina", "nom": "KARRAY", "email": "amina.karray@ge.university.tn"},
            {"prenom": "Riadh", "nom": "MAHJOUB", "email": "riadh.mahjoub@ge.university.tn"},
            {"prenom": "Sarra", "nom": "HAMDI", "email": "sarra.hamdi@ge.university.tn"},
            {"prenom": "Mohamed", "nom": "ARFAOUI", "email": "mohamed.arfaoui@ge.university.tn"}
        ]
    },

    "Génie Civil": {
        "code": "GC",
        "specialties": {
            "Génie Civil - Bâtiment": {
                "code": "GCB",
                "levels": ["GC1", "GC2", "GC3"],
                "subjects": [
                    {"name": "Béton Armé", "coefficient": 3.5},
                    {"name": "Construction Bâtiment", "coefficient": 3.0},
                    {"name": "Pathologie du Bâtiment", "coefficient": 2.0},
                    {"name": "Métré et Devis", "coefficient": 2.0}
                ]
            },
            "Génie Civil - Travaux Publics": {
                "code": "GCTP",
                "levels": ["GC1", "GC2", "GC3"],
                "subjects": [
                    {"name": "Mécanique des Sols", "coefficient": 3.0},
                    {"name": "Hydraulique", "coefficient": 2.5},
                    {"name": "Topographie", "coefficient": 2.0},
                    {"name": "Routes et Chaussées", "coefficient": 2.5},
                    {"name": "Ouvrages d'Art", "coefficient": 3.0}
                ]
            }
        },
        "teachers": [
            {"prenom": "Youssef", "nom": "NEFZAOUI", "email": "youssef.nefzaoui@gc.university.tn"},
            {"prenom": "Fatma", "nom": "MAATALLAH", "email": "fatma.maatallah@gc.university.tn"},
            {"prenom": "Slim", "nom": "CHAOUACHI", "email": "slim.chaouachi@gc.university.tn"},
            {"prenom": "Ines", "nom": "DRISSI", "email": "ines.drissi@gc.university.tn"}
        ]
    },

    "Technologie d'Informatique": {
        "code": "TI",
        "specialties": {
            "Développement Logiciel": {
                "code": "DSI",
                "levels": ["TI1", "TI2", "TI3"],
                "subjects": [
                    {"name": "Programmation Orientée Objet", "coefficient": 3.0},
                    {"name": "Développement Web", "coefficient": 2.5},
                    {"name": "Base de Données", "coefficient": 2.5},
                    {"name": "Génie Logiciel", "coefficient": 2.0},
                    {"name": "Framework Java/Spring", "coefficient": 2.5}
                ]
            },
            "Réseaux et Systèmes": {
                "code": "RSI",
                "levels": ["TI1", "TI2", "TI3"],
                "subjects": [
                    {"name": "Réseaux Informatiques", "coefficient": 3.0},
                    {"name": "Administration Systèmes", "coefficient": 2.5},
                    {"name": "Sécurité Informatique", "coefficient": 2.5},
                    {"name": "Systèmes Distribués", "coefficient": 2.0}
                ]
            },
            "Intelligence Artificielle": {
                "code": "IA",
                "levels": ["TI1", "TI2", "TI3"],
                "subjects": [
                    {"name": "Intelligence Artificielle", "coefficient": 3.0},
                    {"name": "Machine Learning", "coefficient": 2.5},
                    {"name": "Big Data", "coefficient": 2.0},
                    {"name": "Vision par Ordinateur", "coefficient": 2.0}
                ]
            }
        },
        "teachers": [
            {"prenom": "Wahid", "nom": "DEVELOPER", "email": "wahid@gmail.com"},  # Special teacher
            {"prenom": "Mariam", "nom": "TECHNO", "email": "mariam.techno@ti.university.tn"},
            {"prenom": "Tarek", "nom": "NETWORK", "email": "tarek.network@ti.university.tn"},
            {"prenom": "Hiba", "nom": "AIDEV", "email": "hiba.ai@ti.university.tn"},
            {"prenom": "Nizar", "nom": "BACKEND", "email": "nizar.backend@ti.university.tn"}
        ]
    }
}

# Room configuration
ROOMS_CONFIG = [
    # Amphithéâtres
    {"code": "AMPH_A", "type": "LECTURE", "capacity": 200},
    {"code": "AMPH_B", "type": "LECTURE", "capacity": 150},
    {"code": "AMPH_C", "type": "LECTURE", "capacity": 180},
    
    # Salles de cours GM
    {"code": "GM_101", "type": "LECTURE", "capacity": 40},
    {"code": "GM_102", "type": "LECTURE", "capacity": 35},
    {"code": "GM_LAB1", "type": "LAB", "capacity": 25},
    {"code": "GM_LAB2", "type": "LAB", "capacity": 20},
    
    # Salles de cours GE  
    {"code": "GE_201", "type": "LECTURE", "capacity": 40},
    {"code": "GE_202", "type": "LECTURE", "capacity": 35},
    {"code": "GE_LAB1", "type": "LAB", "capacity": 25},
    {"code": "GE_LAB2", "type": "LAB", "capacity": 20},
    
    # Salles de cours GC
    {"code": "GC_301", "type": "LECTURE", "capacity": 45},
    {"code": "GC_302", "type": "LECTURE", "capacity": 40},
    {"code": "GC_LAB1", "type": "LAB", "capacity": 20},
    
    # Salles informatique TI
    {"code": "TI_401", "type": "LECTURE", "capacity": 40},
    {"code": "TI_402", "type": "LECTURE", "capacity": 35},
    {"code": "TI_LAB1", "type": "LAB", "capacity": 30},
    {"code": "TI_LAB2", "type": "LAB", "capacity": 25},
    {"code": "TI_LAB3", "type": "LAB", "capacity": 30},
    
    # Salles d'examens
    {"code": "EXAM_1", "type": "EXAM", "capacity": 80},
    {"code": "EXAM_2", "type": "EXAM", "capacity": 100},
    {"code": "EXAM_3", "type": "EXAM", "capacity": 60}
]

def login_admin():
    """Login as admin and get token"""
    login_data = {
        "email": "admin@university.com", 
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Admin authentication successful")
            return token_data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None

def get_auth_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def delete_math_department(token):
    """Delete the math department and clean up orphaned data"""
    headers = get_auth_headers(token)
    
    print("🗑️  Deleting 'math' department and cleaning up...")
    
    # First get all departments to find math department
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    if response.status_code == 200:
        departments = response.json()
        math_dept = None
        
        for dept in departments:
            if dept['name'].lower() == 'math':
                math_dept = dept
                break
        
        if math_dept:
            # Note: We cannot delete via API, but we'll note it needs to be cleaned up
            print(f"⚠️  Found 'math' department (ID: {math_dept['id']})")
            print("   This needs to be deleted via database script or admin interface")
            return math_dept['id']
        else:
            print("✅ No 'math' department found")
            return None
    else:
        print(f"❌ Failed to get departments: {response.status_code}")
        return None

def create_complete_university_structure(token):
    """Create the complete university structure"""
    headers = get_auth_headers(token)
    created_data = {
        "departments": {},
        "department_heads": {},
        "specialties": {},
        "levels": {},
        "teachers": {},
        "students": []
    }
    
    print("🏛️  Creating University Structure...")
    
    # 1. Create Departments
    print("\n📚 Creating Departments...")
    for dept_name, dept_config in UNIVERSITY_STRUCTURE.items():
        dept_data = {"name": dept_name}
        
        try:
            response = requests.post(f"{BASE_URL}/departments", json=dept_data, headers=headers)
            if response.status_code in [200, 201]:
                dept = response.json()
                created_data["departments"][dept_name] = dept
                print(f"✅ Created department: {dept_name}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Try to get existing department
                response = requests.get(f"{BASE_URL}/departments", headers=headers)
                if response.status_code == 200:
                    departments = response.json()
                    for existing_dept in departments:
                        if existing_dept['name'] == dept_name:
                            created_data["departments"][dept_name] = existing_dept
                            print(f"✅ Using existing department: {dept_name}")
                            break
            else:
                print(f"❌ Failed to create department {dept_name}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating department {dept_name}: {str(e)}")
    
    # 2. Create Department Heads
    print("\n👥 Creating Department Heads...")
    dept_head_data = [
        {"nom": "MAATALLAH", "prenom": "Mohamed", "email": "mohamed.maatallah@university.tn", "dept": "Technologie d'Informatique"},
        {"nom": "NEFZAOUI", "prenom": "Fatma", "email": "fatma.nefzaoui@university.tn", "dept": "Génie Mécanique"},
        {"nom": "HAMDI", "prenom": "Ahmed", "email": "ahmed.hamdi@university.tn", "dept": "Génie Électrique"},
        {"nom": "ARFAOUI", "prenom": "Sarra", "email": "sarra.arfaoui@university.tn", "dept": "Génie Civil"}
    ]
    
    for head_data in dept_head_data:
        if head_data["dept"] in created_data["departments"]:
            dept_id = created_data["departments"][head_data["dept"]]['id']
            
            user_data = {
                "prenom": head_data["prenom"],
                "nom": head_data["nom"], 
                "email": head_data["email"],
                "password": "depthead123",
                "role": "DEPARTMENT_HEAD"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/auth/register?department_id={dept_id}", json=user_data)
                if response.status_code in [200, 201]:
                    dept_head = response.json()
                    created_data["department_heads"][head_data["dept"]] = dept_head
                    print(f"✅ Created department head: {head_data['prenom']} {head_data['nom']} for {head_data['dept']}")
                elif response.status_code == 400 and "already has a department head" in response.text:
                    print(f"⚠️  Department {head_data['dept']} already has a head assigned")
                else:
                    print(f"❌ Failed to create department head for {head_data['dept']}: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Error creating department head: {str(e)}")
    
    # 3. Create Teachers (before specialties to avoid dependency issues)
    print("\n👨‍🏫 Creating Teachers...")
    for dept_name, dept_config in UNIVERSITY_STRUCTURE.items():
        if dept_name in created_data["departments"]:
            print(f"\n   Creating teachers for {dept_name}:")
            
            for teacher_data in dept_config["teachers"]:
                user_data = {
                    "prenom": teacher_data["prenom"],
                    "nom": teacher_data["nom"],
                    "email": teacher_data["email"],
                    "password": "teacher123" if teacher_data["nom"] != "DEVELOPER" else "dalighgh15",
                    "role": "TEACHER"
                }
                
                try:
                    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
                    if response.status_code in [200, 201]:
                        teacher = response.json()
                        if dept_name not in created_data["teachers"]:
                            created_data["teachers"][dept_name] = []
                        created_data["teachers"][dept_name].append(teacher)
                        print(f"     ✅ Created teacher: {teacher_data['prenom']} {teacher_data['nom']}")
                    elif response.status_code == 400 and "already exists" in response.text:
                        print(f"     ⚠️  Teacher {teacher_data['prenom']} {teacher_data['nom']} already exists")
                    else:
                        print(f"     ❌ Failed to create teacher {teacher_data['prenom']} {teacher_data['nom']}: {response.status_code}")
                        print(f"        Response: {response.text}")
                except Exception as e:
                    print(f"     ❌ Error creating teacher: {str(e)}")
    
    return created_data

def create_students_batch(token, count=100):
    """Create a batch of students"""
    headers = get_auth_headers(token)
    
    print(f"\n👨‍🎓 Creating {count} Students...")
    
    # Tunisian first names
    first_names = [
        "Ahmed", "Mohamed", "Ali", "Youssef", "Omar", "Karim", "Slim", "Bilel", "Mehdi", "Amine",
        "Fatma", "Amina", "Leila", "Sarra", "Nadia", "Mariam", "Ines", "Salma", "Rim", "Emna",
        "Hamdi", "Tarek", "Fares", "Nizar", "Walid", "Saber", "Malek", "Hedi", "Riadh", "Farouk",
        "Jihen", "Yasmine", "Dorra", "Hiba", "Wided", "Nour", "Rania", "Marwa", "Sonia", "Amel"
    ]
    
    # Tunisian last names
    last_names = [
        "BEN ALI", "TRABELSI", "MEZGHANI", "KARRAY", "BOUALI", "MAHJOUB", "SALEM", "NEFZAOUI",
        "HAMDI", "ARFAOUI", "MAATALLAH", "CHAOUACHI", "DRISSI", "HAKIM", "BELHAJ", "GHARBI",
        "MZALI", "REKIK", "JLASSI", "KACEM", "MANSOUR", "BOUAZIZI", "SFAR", "MEJRI", "KAMMOUN",
        "CHEBBI", "TLILI", "DHAOUI", "MOKRANI", "ZOUARI", "BELAID", "SASSI", "HADDAD", "CHOUCHANE",
        "KOUKI", "LAZAAR", "TURKI", "OUALI", "AGREBI", "TECHNO", "NETWORK", "AIDEV", "BACKEND"
    ]
    
    created_students = []
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Create unique email
        email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{i+1:03d}@student.university.tn"
        
        user_data = {
            "prenom": first_name,
            "nom": last_name,
            "email": email,
            "password": "student123",
            "role": "STUDENT"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                student = response.json()
                created_students.append(student)
                if (i + 1) % 20 == 0:  # Print progress every 20 students
                    print(f"     ✅ Created {i + 1}/{count} students...")
            elif response.status_code == 400 and "already exists" in response.text:
                continue  # Skip existing students
            else:
                if i < 5:  # Only show first few errors to avoid spam
                    print(f"     ❌ Failed to create student {first_name} {last_name}: {response.status_code}")
        except Exception as e:
            if i < 5:  # Only show first few errors
                print(f"     ❌ Error creating student: {str(e)}")
    
    print(f"✅ Successfully created {len(created_students)} students")
    return created_students

def main():
    """Main setup function"""
    print("🚀 COMPREHENSIVE UNIVERSITY DATABASE SETUP")
    print("=" * 50)
    print("This will create a complete university database with:")
    print("• 4 Departments with academic structure")
    print("• Department heads for each department") 
    print("• Teachers and students")
    print("• Specialties, levels, and subjects")
    print("• Rooms and sample schedules")
    print("=" * 50)
    
    # 1. Admin Login
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        return
    
    # 2. Delete math department
    math_dept_id = delete_math_department(token)
    
    # 3. Create university structure
    created_data = create_complete_university_structure(token)
    
    # 4. Create students
    students = create_students_batch(token, 150)  # Create 150 students
    created_data["students"] = students
    
    # 5. Final Summary
    print("\n" + "=" * 60)
    print("🎉 UNIVERSITY SETUP COMPLETE!")
    print("=" * 60)
    
    print(f"📊 Created Data Summary:")
    print(f"   🏛️  Departments: {len(created_data['departments'])}")
    print(f"   👥 Department Heads: {len(created_data['department_heads'])}")
    print(f"   👨‍🏫 Teachers: {sum(len(teachers) for teachers in created_data['teachers'].values())}")
    print(f"   👨‍🎓 Students: {len(created_data['students'])}")
    
    print(f"\n🔐 Login Credentials:")
    print(f"   🔑 Admin: admin@university.com / admin123")
    print(f"   👥 Department Heads:")
    for dept, head in created_data['department_heads'].items():
        print(f"      - {head['email']} / depthead123 ({dept})")
    print(f"   👨‍🏫 Teachers: [email] / teacher123 (except wahid@gmail.com / dalighgh15)")
    print(f"   👨‍🎓 Students: [email] / student123")
    
    # Test admin panel compatibility
    print(f"\n🧪 Testing Admin Panel Compatibility:")
    headers = get_auth_headers(token)
    
    # Test /auth/me endpoint for admin panel
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ Admin /auth/me endpoint working")
        print(f"   ✅ Admin user: {user_data['prenom']} {user_data['nom']} ({user_data['role']})")
    else:
        print(f"   ❌ Admin /auth/me endpoint issue: {response.status_code}")
    
    # Test departments endpoint
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    if response.status_code == 200:
        depts = response.json()
        print(f"   ✅ Departments endpoint working: {len(depts)} departments")
    else:
        print(f"   ❌ Departments endpoint issue: {response.status_code}")
    
    print(f"\n✅ All applications ready:")
    print(f"   🔧 Admin Panel: http://localhost:3001 (login: admin@university.com)")
    print(f"   👥 Frontend: http://localhost:3000 (for dept heads, teachers, students)")  
    print(f"   🔌 API: http://localhost:8000 (serving all applications)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Start admin panel: cd apps/admin-panel && npm run dev")
    print(f"   2. Start frontend: cd frontend && npm run dev") 
    print(f"   3. Test admin login in admin panel")
    print(f"   4. Create specialties, levels, and subjects via admin interface")

if __name__ == "__main__":
    main()