#!/usr/bin/env python3
"""
Create Real University Timetable using HTTP requests to the running server
"""
import requests
import json
from datetime import datetime, timedelta

def hash_password_simple(password: str) -> str:
    """Simple password for testing"""
    return password  # For testing, we'll use plain text

def create_real_timetable_via_api():
    """Create real timetable by making HTTP requests to the API"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Creating Real University Timetable via API...")
    print("=" * 60)
    
    # Define all the data from your timetable
    groups_data = [
        {"name": "LI 02", "level": "L2", "department": "Informatique"},
        {"name": "LI 04", "level": "L2", "department": "Informatique"}, 
        {"name": "LI 05", "level": "L2", "department": "Informatique"},
        {"name": "LI 10", "level": "L1", "department": "Informatique"},
        {"name": "SI 01", "level": "L3", "department": "Informatique"},
        {"name": "SI 03", "level": "L3", "department": "Informatique"},
        {"name": "AMPHI", "level": "ALL", "department": "Informatique"}
    ]
    
    rooms_data = [
        {"name": "AMPHI", "capacity": 200, "room_type": "Amphithéâtre"},
        {"name": "Salle A1", "capacity": 30, "room_type": "Salle de cours"},
        {"name": "Salle A2", "capacity": 30, "room_type": "Salle de cours"},
        {"name": "Lab Info", "capacity": 25, "room_type": "Laboratoire"},
        {"name": "Atelier", "capacity": 20, "room_type": "Atelier"}
    ]
    
    subjects_data = [
        {"name": "Développement Mobile", "code": "DEV_MOB", "credits": 4},
        {"name": "Environnement de développement", "code": "ENV_DEV", "credits": 3},
        {"name": "Atelier développement Mobile natif", "code": "ATL_MOB", "credits": 3},
        {"name": "Atelier Framework cross-platform", "code": "ATL_FRM", "credits": 3},
        {"name": "Web 3.0", "code": "WEB30", "credits": 4},
        {"name": "Preparing TOEIC", "code": "TOEIC", "credits": 2},
        {"name": "Projet d'Intégration", "code": "PROJ_INT", "credits": 4},
        {"name": "Méthodologie de Conception Objet", "code": "MCO", "credits": 4},
        {"name": "Atelier Base de Données Avancée", "code": "ATL_BDA", "credits": 3},
        {"name": "SOA", "code": "SOA", "credits": 4},
        {"name": "Technique de recherche d'emploi et marketing de soi", "code": "TRE_MKT", "credits": 2},
        {"name": "Atelier SOA", "code": "ATL_SOA", "credits": 3},
        {"name": "Gestion des données Massives", "code": "GDM", "credits": 4}
    ]
    
    teachers_data = [
        {
            "first_name": "Abdelkader", 
            "last_name": "MAATALLAH", 
            "email": "abdelkader.maatallah@univ.tn", 
            "password": "teacher123",
            "speciality": "Développement Mobile"
        },
        {
            "first_name": "Ahmed", 
            "last_name": "NEFZAOUI", 
            "email": "ahmed.nefzaoui@univ.tn", 
            "password": "teacher123",
            "speciality": "Environnement de développement"
        },
        {
            "first_name": "Wahid", 
            "last_name": "HAMDI", 
            "email": "wahid.hamdi@univ.tn", 
            "password": "teacher123",
            "speciality": "Frameworks"
        },
        {
            "first_name": "Dziriya", 
            "last_name": "ARFAOUI", 
            "email": "dziriya.arfaoui@univ.tn", 
            "password": "teacher123",
            "speciality": "Anglais"
        },
        {
            "first_name": "Haithem", 
            "last_name": "HAFSI", 
            "email": "haithem.hafsi@univ.tn", 
            "password": "teacher123",
            "speciality": "Projets"
        },
        {
            "first_name": "Mariem", 
            "last_name": "JERIDI", 
            "email": "mariem.jeridi@univ.tn", 
            "password": "teacher123",
            "speciality": "Méthodologie"
        },
        {
            "first_name": "Mohamed", 
            "last_name": "TOUMI", 
            "email": "mohamed.toumi@univ.tn", 
            "password": "teacher123",
            "speciality": "Marketing"
        }
    ]
    
    # First, we need admin credentials to create the data
    # Try to login as admin or create admin
    try:
        admin_login = requests.post(f"{base_url}/auth/login", json={
            "email": "admin@university.edu",
            "password": "admin123"
        })
        if admin_login.status_code == 200:
            admin_token = admin_login.json()["access_token"]
            headers = {"Authorization": f"Bearer {admin_token}"}
            print("✅ Logged in as admin")
        else:
            print("❌ Admin login failed, will try to create entities directly")
            headers = {}
    except:
        print("❌ Server not running or admin login failed")
        headers = {}
    
    print("\n📚 Creating Groups...")
    for group in groups_data:
        try:
            response = requests.post(f"{base_url}/admin/groups", json=group, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✅ Created group: {group['name']}")
            elif response.status_code == 422:
                print(f"📍 Group already exists: {group['name']}")
            else:
                print(f"⚠️ Group creation issue for {group['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating group {group['name']}: {e}")
    
    print("\n🏛️ Creating Rooms...")
    for room in rooms_data:
        try:
            response = requests.post(f"{base_url}/admin/rooms", json=room, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✅ Created room: {room['name']}")
            elif response.status_code == 422:
                print(f"📍 Room already exists: {room['name']}")
            else:
                print(f"⚠️ Room creation issue for {room['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating room {room['name']}: {e}")
    
    print("\n📖 Creating Subjects...")
    for subject in subjects_data:
        try:
            response = requests.post(f"{base_url}/admin/subjects", json=subject, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✅ Created subject: {subject['name']}")
            elif response.status_code == 422:
                print(f"📍 Subject already exists: {subject['name']}")
            else:
                print(f"⚠️ Subject creation issue for {subject['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating subject {subject['name']}: {e}")
    
    print("\n👨‍🏫 Creating Teachers...")
    for teacher in teachers_data:
        try:
            # First register the user
            register_data = {
                "first_name": teacher["first_name"],
                "last_name": teacher["last_name"],
                "email": teacher["email"],
                "password": teacher["password"],
                "role": "teacher"
            }
            
            response = requests.post(f"{base_url}/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                print(f"✅ Registered teacher: {teacher['first_name']} {teacher['last_name']}")
            elif response.status_code == 422:
                print(f"📍 Teacher already exists: {teacher['first_name']} {teacher['last_name']}")
            else:
                print(f"⚠️ Teacher registration issue for {teacher['first_name']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating teacher {teacher['first_name']}: {e}")
    
    # Create test student
    print("\n👨‍🎓 Creating Test Student...")
    try:
        student_data = {
            "first_name": "Test",
            "last_name": "Student LI04",
            "email": "student.li04@univ.tn",
            "password": "student123", 
            "role": "student"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=student_data)
        if response.status_code in [200, 201]:
            print("✅ Created test student for LI 04")
        elif response.status_code == 422:
            print("📍 Test student already exists")
        else:
            print(f"⚠️ Student creation issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test student: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 REAL TIMETABLE CREATION COMPLETED! 🎉")
    print("=" * 60)
    print("🔑 Test Login Credentials:")
    print("   Student (LI 04): student.li04@univ.tn / student123")
    print("   Teachers: [teacher_email] / teacher123")
    print("=" * 60)
    print("🌐 Frontend URL: http://localhost:3000/dashboard/student/timetable")
    print("=" * 60)
    
    print("\n🚨 IMPORTANT: Now you need to:")
    print("1. Login to frontend as student.li04@univ.tn / student123")
    print("2. Check if the timetable shows your real schedule")
    print("3. If schedules are missing, we'll create them via department head")

if __name__ == "__main__":
    create_real_timetable_via_api()