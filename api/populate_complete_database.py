"""
Complete Database Population Script using REST API
Creates a full dataset with all necessary data for testing the absence system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login_admin():
    """Login as admin to get auth token"""
    print("🔐 Logging in as admin...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@univ.dz",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Logged in as {data['user']['firstName']} {data['user']['lastName']}")
        return data["access_token"]
    else:
        print("  ❌ Admin login failed. Creating admin user...")
        # Try to create admin
        reg_response = requests.post(
            f"{BASE_URL}/auth/register?role=ADMIN",
            json={
                "firstName": "System",
                "lastName": "Administrator",
                "email": "admin@univ.dz",
                "login": "admin",
                "password": "admin123"
            }
        )
        if reg_response.status_code == 200:
            # Try login again
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "admin@univ.dz",
                "password": "admin123"
            })
            if response.status_code == 200:
                data = response.json()
                return data["access_token"]
        
        print("  ❌ Could not get admin access. Please ensure the API is running.")
        return None

def populate_database():
    print("=" * 80)
    print("🚀 COMPLETE DATABASE POPULATION")
    print("=" * 80)
    print()
    
    # Get admin token
    token = login_admin()
    if not token:
        print("\n❌ Cannot continue without admin access")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Statistics
    stats = {
        "departments": 0,
        "specialties": 0,
        "levels": 0,
        "groups": 0,
        "classrooms": 0,
        "subjects": 0,
        "teachers": 0,
        "students": 0
    }
    
    try:
        # ============= DEPARTMENTS =============
        print("\n📚 Creating Departments...")
        departments = []
        dept_data = [
            {"name": "Informatique", "code": "INFO"},
            {"name": "Génie Civil", "code": "GC"},
            {"name": "Génie Mécanique", "code": "GM"},
            {"name": "Génie Électrique", "code": "GE"},
        ]
        
        # Get existing departments
        try:
            resp = requests.get(f"{BASE_URL}/departments", headers=headers)
            if resp.status_code == 200:
                existing_depts = resp.json()
                print(f"  Found {len(existing_depts)} existing departments")
                departments = existing_depts
                stats["departments"] = len(departments)
        except:
            pass
        
        for dept in dept_data:
            # Check if exists
            exists = any(d.get("code") == dept["code"] for d in departments)
            if not exists:
                resp = requests.post(f"{BASE_URL}/admin/departments", json=dept, headers=headers)
                if resp.status_code in [200, 201]:
                    new_dept = resp.json()
                    departments.append(new_dept)
                    stats["departments"] += 1
                    print(f"  ✅ Created: {dept['name']}")
                else:
                    print(f"  ⚠️  Could not create {dept['name']}: {resp.status_code}")
            else:
                print(f"  ✓ Exists: {dept['name']}")
        
        # ============= LEVELS (NIVEAUX) =============
        print("\n📊 Creating Levels (Niveaux)...")
        levels = []
        level_data = [
            {"name": "1ère Année", "code": "L1", "ordre": 1},
            {"name": "2ème Année", "code": "L2", "ordre": 2},
            {"name": "3ème Année", "code": "L3", "ordre": 3},
            {"name": "Master 1", "code": "M1", "ordre": 4},
            {"name": "Master 2", "code": "M2", "ordre": 5},
        ]
        
        # Get existing levels
        try:
            resp = requests.get(f"{BASE_URL}/niveaux", headers=headers)
            if resp.status_code == 200:
                existing_levels = resp.json()
                print(f"  Found {len(existing_levels)} existing levels")
                levels = existing_levels
                stats["levels"] = len(levels)
        except:
            pass
        
        for level in level_data:
            exists = any(l.get("code") == level["code"] for l in levels)
            if not exists:
                resp = requests.post(f"{BASE_URL}/admin/niveaux", json=level, headers=headers)
                if resp.status_code in [200, 201]:
                    new_level = resp.json()
                    levels.append(new_level)
                    stats["levels"] += 1
                    print(f"  ✅ Created: {level['name']} ({level['code']})")
                else:
                    print(f"  ⚠️  Could not create {level['name']}: {resp.status_code}")
            else:
                print(f"  ✓ Exists: {level['name']}")
        
        # ============= SPECIALTIES =============
        print("\n🎓 Creating Specialties...")
        specialties = []
        
        if len(departments) < 2:
            print("  ⚠️  Not enough departments to create specialties")
        else:
            specialty_data = [
                # Informatique specialties
                {"name": "Réseaux et Télécommunications", "code": "RT", "departmentId": departments[0]["id"]},
                {"name": "Génie Logiciel", "code": "GL", "departmentId": departments[0]["id"]},
                {"name": "Intelligence Artificielle", "code": "IA", "departmentId": departments[0]["id"]},
                # Génie Civil specialties
                {"name": "Bâtiment", "code": "BAT", "departmentId": departments[1]["id"]},
                {"name": "Travaux Publics", "code": "TP", "departmentId": departments[1]["id"]},
            ]
            
            # Get existing specialties
            try:
                resp = requests.get(f"{BASE_URL}/specialities", headers=headers)
                if resp.status_code == 200:
                    existing_specs = resp.json()
                    print(f"  Found {len(existing_specs)} existing specialties")
                    specialties = existing_specs
                    stats["specialties"] = len(specialties)
            except:
                pass
            
            for spec in specialty_data:
                exists = any(s.get("code") == spec["code"] for s in specialties)
                if not exists:
                    resp = requests.post(f"{BASE_URL}/admin/specialities", json=spec, headers=headers)
                    if resp.status_code in [200, 201]:
                        new_spec = resp.json()
                        specialties.append(new_spec)
                        stats["specialties"] += 1
                        print(f"  ✅ Created: {spec['name']}")
                    else:
                        print(f"  ⚠️  Could not create {spec['name']}: {resp.status_code}")
                else:
                    print(f"  ✓ Exists: {spec['name']}")
        
        # ============= GROUPS =============
        print("\n👥 Creating Groups...")
        groups = []
        
        if len(departments) < 2 or len(specialties) < 2 or len(levels) < 3:
            print("  ⚠️  Not enough base data to create groups")
        else:
            # Get existing groups
            try:
                resp = requests.get(f"{BASE_URL}/groupes", headers=headers)
                if resp.status_code == 200:
                    existing_groups = resp.json()
                    print(f"  Found {len(existing_groups)} existing groups")
                    groups = existing_groups
                    stats["groups"] = len(groups)
            except:
                pass
            
            # Create groups for first 2 specialties and first 3 levels
            for spec in specialties[:2]:
                for level in levels[:3]:
                    for group_num in [1, 2]:
                        group_data = {
                            "name": f"{spec['code']}-{level['code']}-G{group_num}",
                            "code": f"{spec['code']}{level['code']}G{group_num}",
                            "departmentId": spec["departmentId"],
                            "specialityId": spec["id"],
                            "niveauId": level["id"],
                        }
                        
                        exists = any(g.get("code") == group_data["code"] for g in groups)
                        if not exists:
                            resp = requests.post(f"{BASE_URL}/admin/groupes", json=group_data, headers=headers)
                            if resp.status_code in [200, 201]:
                                new_group = resp.json()
                                groups.append(new_group)
                                stats["groups"] += 1
                                print(f"  ✅ Created: {group_data['name']}")
                            else:
                                print(f"  ⚠️  Could not create {group_data['name']}: {resp.status_code}")
                        else:
                            print(f"  ✓ Exists: {group_data['name']}")
        
        # ============= CLASSROOMS =============
        print("\n🏫 Creating Classrooms (Salles)...")
        classrooms = []
        classroom_data = [
            {"name": "Amphi A", "code": "AMPH-A", "type": "Amphithéâtre", "capacity": 200, "building": "Bâtiment A"},
            {"name": "Amphi B", "code": "AMPH-B", "type": "Amphithéâtre", "capacity": 180, "building": "Bâtiment A"},
            {"name": "Salle 101", "code": "S-101", "type": "Salle de cours", "capacity": 40, "building": "Bâtiment A"},
            {"name": "Salle 102", "code": "S-102", "type": "Salle de cours", "capacity": 40, "building": "Bâtiment A"},
            {"name": "Salle 103", "code": "S-103", "type": "Salle de cours", "capacity": 35, "building": "Bâtiment A"},
            {"name": "Salle 201", "code": "S-201", "type": "Salle de cours", "capacity": 40, "building": "Bâtiment B"},
            {"name": "Labo Info 1", "code": "LAB-INFO-1", "type": "Laboratoire", "capacity": 30, "building": "Bâtiment C"},
            {"name": "Labo Info 2", "code": "LAB-INFO-2", "type": "Laboratoire", "capacity": 30, "building": "Bâtiment C"},
            {"name": "TD 301", "code": "TD-301", "type": "Salle de TD", "capacity": 30, "building": "Bâtiment C"},
            {"name": "TD 302", "code": "TD-302", "type": "Salle de TD", "capacity": 30, "building": "Bâtiment C"},
        ]
        
        # Get existing classrooms
        try:
            resp = requests.get(f"{BASE_URL}/salles", headers=headers)
            if resp.status_code == 200:
                existing_rooms = resp.json()
                print(f"  Found {len(existing_rooms)} existing classrooms")
                classrooms = existing_rooms
                stats["classrooms"] = len(classrooms)
        except:
            pass
        
        for room in classroom_data:
            exists = any(r.get("code") == room["code"] for r in classrooms)
            if not exists:
                resp = requests.post(f"{BASE_URL}/admin/salles", json=room, headers=headers)
                if resp.status_code in [200, 201]:
                    new_room = resp.json()
                    classrooms.append(new_room)
                    stats["classrooms"] += 1
                    print(f"  ✅ Created: {room['name']} ({room['type']})")
                else:
                    print(f"  ⚠️  Could not create {room['name']}: {resp.status_code}")
            else:
                print(f"  ✓ Exists: {room['name']}")
        
        # ============= SUBJECTS =============
        print("\n📖 Creating Subjects (Matières)...")
        subjects = []
        
        if len(departments) < 1:
            print("  ⚠️  No departments available")
        else:
            subject_data = [
                {"name": "Programmation Python", "code": "PROG-PY", "coefficient": 3.0, "departmentId": departments[0]["id"]},
                {"name": "Base de Données", "code": "BDD", "coefficient": 3.0, "departmentId": departments[0]["id"]},
                {"name": "Réseaux Informatiques", "code": "RES-INFO", "coefficient": 2.5, "departmentId": departments[0]["id"]},
                {"name": "Systèmes d'Exploitation", "code": "SYS-EXP", "coefficient": 2.5, "departmentId": departments[0]["id"]},
                {"name": "Génie Logiciel", "code": "GL", "coefficient": 3.0, "departmentId": departments[0]["id"]},
                {"name": "Intelligence Artificielle", "code": "IA", "coefficient": 3.0, "departmentId": departments[0]["id"]},
                {"name": "Mathématiques", "code": "MATH", "coefficient": 4.0, "departmentId": departments[0]["id"]},
                {"name": "Physique", "code": "PHY", "coefficient": 3.0, "departmentId": departments[0]["id"]},
            ]
            
            # Get existing subjects
            try:
                resp = requests.get(f"{BASE_URL}/matieres", headers=headers)
                if resp.status_code == 200:
                    existing_subjects = resp.json()
                    print(f"  Found {len(existing_subjects)} existing subjects")
                    subjects = existing_subjects
                    stats["subjects"] = len(subjects)
            except:
                pass
            
            for subj in subject_data:
                exists = any(s.get("code") == subj["code"] for s in subjects)
                if not exists:
                    resp = requests.post(f"{BASE_URL}/admin/matieres", json=subj, headers=headers)
                    if resp.status_code in [200, 201]:
                        new_subj = resp.json()
                        subjects.append(new_subj)
                        stats["subjects"] += 1
                        print(f"  ✅ Created: {subj['name']}")
                    else:
                        print(f"  ⚠️  Could not create {subj['name']}: {resp.status_code}")
                else:
                    print(f"  ✓ Exists: {subj['name']}")
        
        # ============= STUDENTS =============
        print("\n👨‍🎓 Creating Students...")
        
        if len(groups) < 3:
            print("  ⚠️  Not enough groups to create students")
        else:
            student_counter = 1
            students_per_group = 5
            
            for group in groups[:6]:  # First 6 groups
                for i in range(1, students_per_group + 1):
                    student_data = {
                        "firstName": f"Étudiant{student_counter}",
                        "lastName": f"Nom{student_counter}",
                        "email": f"student{student_counter}@univ.dz",
                        "login": f"student{student_counter}",
                        "password": "student123"
                    }
                    
                    resp = requests.post(
                        f"{BASE_URL}/auth/register?role=STUDENT&department_id={group['departmentId']}&specialty_id={group['specialityId']}&level_id={group['niveauId']}&group_id={group['id']}",
                        json=student_data
                    )
                    
                    if resp.status_code in [200, 201]:
                        stats["students"] += 1
                        if student_counter % 10 == 0:
                            print(f"  ✅ Created {student_counter} students...")
                    elif resp.status_code == 400 and "already exists" in resp.text:
                        stats["students"] += 1
                    else:
                        print(f"  ⚠️  Could not create student{student_counter}: {resp.status_code}")
                    
                    student_counter += 1
            
            print(f"  📊 Total students: {stats['students']}")
        
        # ============= TEACHERS =============
        print("\n👨‍🏫 Creating Teachers...")
        
        if len(departments) < 1 or len(specialties) < 1:
            print("  ⚠️  No departments/specialties available")
        else:
            teacher_data = [
                {"firstName": "Ahmed", "lastName": "Benali", "email": "ahmed.benali@univ.dz", "login": "abenali"},
                {"firstName": "Fatima", "lastName": "Zohra", "email": "fatima.zohra@univ.dz", "login": "fzohra"},
                {"firstName": "Mohamed", "lastName": "Khaled", "email": "mohamed.khaled@univ.dz", "login": "mkhaled"},
            ]
            
            for teacher in teacher_data:
                teacher["password"] = "teacher123"
                
                resp = requests.post(
                    f"{BASE_URL}/auth/register?role=TEACHER&department_id={departments[0]['id']}&specialty_id={specialties[0]['id']}",
                    json=teacher
                )
                
                if resp.status_code in [200, 201]:
                    stats["teachers"] += 1
                    print(f"  ✅ Created: {teacher['firstName']} {teacher['lastName']}")
                elif resp.status_code == 400 and "already exists" in resp.text:
                    stats["teachers"] += 1
                    print(f"  ✓ Exists: {teacher['firstName']} {teacher['lastName']}")
                else:
                    print(f"  ⚠️  Could not create {teacher['firstName']}: {resp.status_code}")
        
        # ============= SUMMARY =============
        print("\n" + "="*80)
        print("📊 DATABASE POPULATION SUMMARY")
        print("="*80)
        print(f"✅ Departments: {stats['departments']}")
        print(f"✅ Specialties: {stats['specialties']}")
        print(f"✅ Levels (Niveaux): {stats['levels']}")
        print(f"✅ Groups: {stats['groups']}")
        print(f"✅ Classrooms (Salles): {stats['classrooms']}")
        print(f"✅ Subjects (Matières): {stats['subjects']}")
        print(f"✅ Teachers: {stats['teachers']}")
        print(f"✅ Students: {stats['students']}")
        print("="*80)
        
        print("\n📝 SAMPLE LOGIN CREDENTIALS:")
        print("="*80)
        print("👨‍🏫 Teachers:")
        print("   Email: ahmed.benali@univ.dz | Password: teacher123")
        print("   Email: fatima.zohra@univ.dz | Password: teacher123")
        print("\n👨‍🎓 Students:")
        print("   Email: student1@univ.dz to student30@univ.dz")
        print("   Password: student123")
        print("="*80)
        
        print("\n✅ Database population completed!")
        print("🎯 You can now test the absence system with students assigned to:")
        print("   - Departments")
        print("   - Specialties")
        print("   - Levels (Niveaux)")
        print("   - Groups")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure the API server is running on http://localhost:8000")
    print("   Run: cd api && uvicorn main:app --reload\n")
    
    input("Press Enter to continue...")
    populate_database()
