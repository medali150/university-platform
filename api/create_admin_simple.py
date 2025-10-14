#!/usr/bin/env python3
"""
Simple script to create an admin user and then set up the database
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_admin():
    """Create admin user"""
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
            return True
        else:
            print(f"❌ Failed to create admin user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

def login_admin():
    """Login and get token"""
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

if __name__ == "__main__":
    print("🚀 Creating Admin User")
    print("=" * 30)
    
    if create_admin():
        token = login_admin()
        if token:
            print(f"\n✅ Admin setup successful!")
            print(f"📋 You can now:")
            print(f"   1. Use the token: {token[:20]}...")
            print(f"   2. Run the database setup script")
            print(f"   3. Create departments and specialties")
        else:
            print(f"❌ Admin login failed")
    else:
        print(f"❌ Admin creation failed")