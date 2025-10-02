#!/usr/bin/env python3
"""
Test registration endpoint
"""

import requests
import json

def test_registration():
    """Test user registration"""
    
    # Test data
    test_user = {
        "nom": "Test",
        "prenom": "User",
        "email": "test.user@university.com",
        "password": "password123",
        "role": "STUDENT"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("❌ Registration failed!")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the API is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login Status Code: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Registration and Login...")
    
    # Test registration
    result = test_registration()
    
    if result:
        # Test login with the registered user
        print("\n🔐 Testing login...")
        login_result = test_login("test.user@university.com", "password123")
        
        if login_result:
            print("🎉 Both registration and login work perfectly!")
        else:
            print("⚠️ Registration works but login failed")
    else:
        print("❌ Registration failed, skipping login test")