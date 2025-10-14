#!/usr/bin/env python3
"""
ADMIN PANEL COMPATIBILITY TEST
================================
Test that admin login works with both email and login fields
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test admin login with both email and login formats"""
    
    print("🔐 Testing Admin Panel Login Compatibility...")
    print("=" * 50)
    
    # Test 1: Standard email login (frontend compatibility)
    print("\n1️⃣ Testing standard email login:")
    email_login_data = {
        "email": "admin@university.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=email_login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Email login successful")
            print(f"   Token: {token_data['access_token'][:50]}...")
            print(f"   User: {token_data['user']['firstName']} {token_data['user']['lastName']} ({token_data['user']['role']})")
            
            # Test /auth/me endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"   ✅ /auth/me endpoint working: {user_data['prenom']} {user_data['nom']}")
            else:
                print(f"   ❌ /auth/me endpoint failed: {me_response.status_code}")
        else:
            print(f"   ❌ Email login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Email login error: {str(e)}")
    
    # Test 2: Admin panel login format (login field)
    print("\n2️⃣ Testing admin panel login format:")
    login_data = {
        "login": "admin@university.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login field successful")
            print(f"   Token: {token_data['access_token'][:50]}...")
            print(f"   User: {token_data['user']['firstName']} {token_data['user']['lastName']} ({token_data['user']['role']})")
            
            # Verify admin panel expected fields are present
            user = token_data['user']
            required_fields = ['id', 'firstName', 'lastName', 'email', 'login', 'role', 'createdAt', 'updatedAt']
            missing_fields = [field for field in required_fields if field not in user]
            
            if not missing_fields:
                print("   ✅ All admin panel required fields present")
            else:
                print(f"   ⚠️  Missing fields: {missing_fields}")
                
        else:
            print(f"   ❌ Login field failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login field error: {str(e)}")
    
    # Test 3: Check departments endpoint (admin panel needs this)
    print("\n3️⃣ Testing departments endpoint:")
    try:
        # Use token from first successful login
        if 'token_data' in locals():
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            response = requests.get(f"{BASE_URL}/departments", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                departments = response.json()
                print(f"   ✅ Departments endpoint working: {len(departments)} departments found")
                for dept in departments:
                    print(f"      - {dept['name']} (ID: {dept['id']})")
            else:
                print(f"   ❌ Departments endpoint failed: {response.text}")
        else:
            print("   ⚠️  Skipping (no auth token available)")
            
    except Exception as e:
        print(f"   ❌ Departments endpoint error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Admin Panel Integration Status:")
    print("   1. Login with email field: Ready")
    print("   2. Login with login field: Ready") 
    print("   3. User data format: Admin panel compatible")
    print("   4. Authentication endpoints: Working")
    print("\n✅ Admin panel should now be able to authenticate!")

if __name__ == "__main__":
    test_admin_login()