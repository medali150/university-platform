#!/usr/bin/env python3
"""
Database setup script using HTTP requests to the running API server
This script creates 4 departments with complete data structure
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def create_admin_user():
    """Create an admin user for authentication"""
    admin_data = {
        "prenom": "System",
        "nom": "Administrator",
        "email": "admin@university.com",
        "password": "admin123",
        "role": "ADMIN"
    }
    
    print("=== Creating Admin User ===")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code in [200, 201]:
            admin = response.json()
            print(f"✅ Created admin user: {admin['prenom']} {admin['nom']}")
            return admin
        else:
            print(f"❌ Failed to create admin user: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return None

def login_admin():
    """Login as admin and get access token"""
    login_data = {
        "email": "admin@university.com",
        "password": "admin123"
    }
    
    print("=== Logging in as Admin ===")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Admin login successful")
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

def create_departments(token):
    """Create the 4 departments"""
    departments = [
        {"name": "Génie Mécanique"},
        {"name": "Génie Électrique"}, 
        {"name": "Génie Civil"},
        {"name": "Technologie d'Informatique"}
    ]
    
    headers = get_auth_headers(token)
    created_departments = []
    print("=== Creating Departments ===")
    
    for dept_data in departments:
        try:
            response = requests.post(f"{BASE_URL}/departments", json=dept_data, headers=headers)
            if response.status_code in [200, 201]:
                dept = response.json()
                created_departments.append(dept)
                print(f"✅ Created department: {dept['name']} (ID: {dept['id']})")
            else:
                print(f"❌ Failed to create department {dept_data['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating department {dept_data['name']}: {str(e)}")
    
    return created_departments

def create_specialties(departments, token):
    """Create specialties for each department"""
    specialties_by_dept = {
        "Génie Mécanique": [
            "Mécanique Générale", "Énergétique", "Construction Mécanique"
        ],
        "Génie Électrique": [
            "Électronique", "Électrotechnique", "Automatique"
        ],
        "Génie Civil": [
            "Structure", "Géotechnique", "Hydraulique"
        ],
        "Technologie d'Informatique": [
            "Développement Web", "Réseaux et Sécurité", "Intelligence Artificielle"
        ]
    }
    
    headers = get_auth_headers(token)
    created_specialties = []
    print("\n=== Creating Specialties ===")
    
    for dept in departments:
        dept_name = dept['name']  # Use 'name' field from API response
        if dept_name in specialties_by_dept:
            for spec_name in specialties_by_dept[dept_name]:
                spec_data = {
                    "name": spec_name,
                    "departmentId": dept['id']
                }
                try:
                    response = requests.post(f"{BASE_URL}/specialties", json=spec_data, headers=headers)
                    if response.status_code in [200, 201]:
                        spec = response.json()
                        created_specialties.append(spec)
                        print(f"✅ Created specialty: {spec['name']} in {dept_name}")
                    else:
                        print(f"❌ Failed to create specialty {spec_name}: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error creating specialty {spec_name}: {str(e)}")
    
    return created_specialties

def create_levels(specialties, token):
    """Create levels for each specialty"""
    level_names = ["1ère Année", "2ème Année", "3ème Année"]
    
    headers = get_auth_headers(token)
    created_levels = []
    print("\n=== Creating Levels ===")
    
    for spec in specialties:
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
    
    return created_levels

def check_database_status():
    """Check if the database has the required tables and data"""
    print("=== Checking Database Status ===")
    
    try:
        # Check health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Database status: {health_data['status']}")
            print(f"   Users count: {health_data.get('users_count', 'unknown')}")
        
        # Check available departments
        response = requests.get(f"{BASE_URL}/auth/available-departments")
        if response.status_code == 200:
            dept_data = response.json()
            print(f"✅ Departments: {dept_data['total_departments']} total")
            print(f"   Available for assignment: {dept_data['available_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database status: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Database Setup")
    print("=" * 50)
    
    # Check if server is running
    if not check_database_status():
        print("❌ Server not accessible. Make sure the API server is running.")
        return
    
    # Create admin user and login
    admin_user = create_admin_user()
    if not admin_user:
        print("❌ Failed to create admin user. Trying to login with existing admin...")
    
    token = login_admin()
    if not token:
        print("❌ Failed to authenticate. Cannot proceed with setup.")
        return
    
    # Create departments
    departments = create_departments(token)
    if not departments:
        print("❌ No departments created. Aborting setup.")
        return
    
    # Create specialties
    specialties = create_specialties(departments, token)
    if not specialties:
        print("❌ No specialties created. Cannot proceed with levels.")
        return
    
    # Create levels
    levels = create_levels(specialties, token)
    
    # Final status check
    print("\n" + "=" * 50)
    print("📊 Final Database Status")
    check_database_status()
    
    print(f"\n✅ Setup completed!")
    print(f"   Created {len(departments)} departments")
    print(f"   Created {len(specialties)} specialties") 
    print(f"   Created {len(levels)} levels")
    
    if departments:
        print(f"\n🎯 You can now register department heads for these departments:")
        for dept in departments:
            print(f"   - {dept['name']} (ID: {dept['id']})")

if __name__ == "__main__":
    main()