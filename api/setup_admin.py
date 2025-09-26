#!/usr/bin/env python3
"""
Quick Admin Setup Script
Creates an admin user for testing the CRUD operations
"""

import requests
import json

def create_admin_user():
    """Create admin user if it doesn't exist"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔧 Setting up admin user...")
    
    # Try to register admin user
    admin_data = {
        "firstName": "System",
        "lastName": "Administrator", 
        "email": "admin@university.com",
        "login": "admin",
        "password": "admin123",
        "role": "ADMIN"
    }
    
    # First try to login (in case admin already exists)
    login_data = {"login": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Admin user already exists and can login")
        return response.json()["access_token"]
    
    # Try to register admin
    response = requests.post(f"{base_url}/auth/register", json=admin_data)
    
    if response.status_code in [200, 201]:
        print("✅ Admin user created successfully")
        
        # Now login
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
    else:
        print(f"❌ Failed to create admin user: {response.status_code}")
        print(f"   Response: {response.text}")
        
    return None

def test_admin_endpoints():
    """Test basic admin functionality"""
    base_url = "http://127.0.0.1:8000"
    
    token = create_admin_user()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing admin endpoints...")
    
    # Test dashboard statistics
    response = requests.get(f"{base_url}/admin/dashboard/statistics", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("✅ Dashboard statistics working")
        print(f"   Total users: {stats.get('overview', {}).get('totalUsers', 0)}")
    else:
        print(f"❌ Dashboard failed: {response.status_code}")
    
    # Test student creation
    print("\n📚 Testing student creation...")
    student_data = {
        "firstName": "Test",
        "lastName": "Student",
        "email": "test.student@university.com",
        "login": "test.student",
        "password": "student123",
        "role": "STUDENT"
    }
    
    response = requests.post(f"{base_url}/admin/students/", json=student_data, headers=headers)
    if response.status_code in [200, 201]:
        print("✅ Student creation working")
        student = response.json()
        print(f"   Created: {student['firstName']} {student['lastName']}")
    else:
        print(f"❌ Student creation failed: {response.status_code}")
        print(f"   Response: {response.text}")

def main():
    print("🎓 University Admin Setup & Quick Test")
    print("=" * 50)
    
    try:
        # Test server connectivity
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded but may have issues")
    except requests.exceptions.RequestException:
        print("❌ Server is not running!")
        print("   Please start the server first: uvicorn main:app --reload")
        return
    
    test_admin_endpoints()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Open Swagger UI: http://127.0.0.1:8000/docs")
    print("2. Login with: admin / admin123")
    print("3. Test the admin CRUD endpoints")
    print("4. Run full test: python test_admin_crud.py")

if __name__ == "__main__":
    main()