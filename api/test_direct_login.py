"""
Test direct login call to see exact request/response
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    print("="*80)
    print("TESTING LOGIN ENDPOINT")
    print("="*80)
    
    # Test credentials
    test_data = [
        {"email": "teacher1@university.tn", "password": "Test123!"},
        {"email": "chef.dept1@university.tn", "password": "Test123!"},
        {"email": "student1@university.tn", "password": "Test123!"}
    ]
    
    for credentials in test_data:
        print(f"\n📧 Testing: {credentials['email']}")
        print(f"📝 Payload: {json.dumps(credentials, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=credentials,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LOGIN SUCCESSFUL!")
                print(f"   User: {data['user']['prenom']} {data['user']['nom']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Token: {data['access_token'][:50]}...")
            else:
                print(f"❌ LOGIN FAILED!")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response: {response.text}")
        
        except Exception as e:
            print(f"❌ REQUEST FAILED: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_login()
