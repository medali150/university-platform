"""
User Verification Script
Checks if wahid@gmail.com exists and verifies their role/permissions
"""
import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "wahid@gmail.com"
PASSWORD = "dalighgh15"

def check_user_exists():
    """Verify user credentials and role"""
    print("🔍 Checking User Credentials...")
    print(f"Email: {EMAIL}")
    print(f"Password: [HIDDEN]")
    print()
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            
            print("✅ USER FOUND AND AUTHENTICATED!")
            print("=" * 40)
            print(f"ID: {user.get('id')}")
            print(f"Email: {user.get('email')}")
            print(f"First Name: {user.get('prenom')}")
            print(f"Last Name: {user.get('nom')}")
            print(f"Role: {user.get('role')}")
            print(f"Created At: {user.get('createdAt')}")
            
            # Check role-specific IDs
            if user.get('etudiant_id'):
                print(f"Student ID: {user.get('etudiant_id')}")
            if user.get('enseignant_id'):
                print(f"Teacher ID: {user.get('enseignant_id')}")
            if user.get('chef_departement_id'):
                print(f"Department Head ID: {user.get('chef_departement_id')}")
            
            print("\n🎯 RECOMMENDED TESTS BASED ON ROLE:")
            role = user.get('role')
            
            if role == "STUDENT":
                print("- View personal absences")
                print("- Justify absences")
                print("- View personal schedule")
                
            elif role == "TEACHER":
                print("- View/create absences for students")
                print("- View teaching groups")
                print("- View teaching schedule")
                print("- Mark student absences")
                
            elif role == "DEPARTMENT_HEAD":
                print("- Review and approve/reject absences")
                print("- View department statistics") 
                print("- Manage department absences")
                
            elif role == "ADMIN":
                print("- Full access to all absence functions")
                print("- View system statistics")
                print("- Manage all absences")
            
            return True, user
            
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED!")
            print("Possible reasons:")
            print("- Incorrect password")
            print("- User account disabled")
            print("- Email not found")
            
        else:
            print(f"❌ UNEXPECTED ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
        return False, None
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("Make sure the API server is running on http://localhost:8000")
        print("Start the server with: uvicorn main:app --reload")
        return False, None
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def check_server_status():
    """Check if API server is running"""
    print("🌐 Checking API Server Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running!")
            return True
    except:
        pass
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running!")
            return True
    except:
        pass
    
    print("❌ API Server is not responding!")
    print("Please start the server with: uvicorn main:app --reload")
    return False

if __name__ == "__main__":
    print("🚀 User Verification for Absence System")
    print("=" * 50)
    
    # Check server first
    if check_server_status():
        print()
        # Check user
        success, user = check_user_exists()
        
        if success:
            print(f"\n✅ User verification completed successfully!")
            print(f"Ready to run absence system tests for: {user.get('role')} role")
            print(f"\nNext steps:")
            print(f"1. Run quick test: python quick_test_wahid.py")
            print(f"2. Run full test: python test_absence_system_wahid.py")
        else:
            print(f"\n❌ User verification failed!")
            print(f"Please check credentials or user setup.")
    else:
        print(f"\n❌ Cannot proceed without API server!")