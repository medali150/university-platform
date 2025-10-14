"""
Test script for Subject coefficient functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_subject_coefficient():
    """Test the new coefficient field in subjects CRUD operations"""
    
    print("🧪 Testing Subject Coefficient Functionality\n")
    
    # Try to get a token first
    token = None
    try:
        # Try to login as department head
        login_data = {
            "username": "boubakeur.rabhi@university.tn",
            "password": "password123"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login successful")
        else:
            print(f"⚠️ Login failed: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"⚠️ Login error: {str(e)}")
        return
    
    if not token:
        print("❌ No authentication token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n1. Testing GET subjects - checking coefficient field...")
    try:
        response = requests.get(f"{BASE_URL}/department-head/subjects/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            subjects = data.get('subjects', [])
            print(f"✅ Retrieved {len(subjects)} subjects")
            
            # Check if coefficient field exists
            if subjects:
                first_subject = subjects[0]
                if 'coefficient' in first_subject:
                    print(f"✅ Coefficient field present: {first_subject['coefficient']}")
                else:
                    print(f"❌ Coefficient field missing in subject response")
                    print(f"   Available fields: {list(first_subject.keys())}")
        else:
            print(f"❌ Failed to get subjects: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting subjects: {str(e)}")
    
    print("\n2. Testing GET helper data...")
    try:
        # Get levels and teachers for creating a subject
        levels_response = requests.get(f"{BASE_URL}/department-head/subjects/helpers/levels", headers=headers)
        teachers_response = requests.get(f"{BASE_URL}/department-head/subjects/helpers/teachers", headers=headers)
        
        if levels_response.status_code == 200 and teachers_response.status_code == 200:
            levels_data = levels_response.json()
            teachers_data = teachers_response.json()
            
            levels = levels_data.get('levels', [])
            teachers = teachers_data.get('teachers', [])
            
            print(f"✅ Retrieved {len(levels)} levels and {len(teachers)} teachers")
            
            if levels:
                level_id = levels[0]['id']
                print(f"   Using level: {levels[0]['name']}")
            else:
                print("❌ No levels available for testing")
                return
                
        else:
            print(f"❌ Failed to get helper data")
            return
            
    except Exception as e:
        print(f"❌ Error getting helper data: {str(e)}")
        return
    
    print("\n3. Testing CREATE subject with coefficient...")
    try:
        create_data = {
            "name": f"Test Subject Coefficient {datetime.now().strftime('%H%M%S')}",
            "coefficient": 2.5,
            "levelId": level_id
        }
        
        response = requests.post(
            f"{BASE_URL}/department-head/subjects/",
            headers=headers,
            json=create_data
        )
        
        if response.status_code == 200:
            subject_data = response.json()
            created_subject_id = subject_data['id']
            print(f"✅ Subject created with coefficient: {subject_data.get('coefficient')}")
            print(f"   Subject ID: {created_subject_id}")
            print(f"   Subject name: {subject_data.get('name')}")
        else:
            print(f"❌ Failed to create subject: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating subject: {str(e)}")
        return
    
    print("\n4. Testing UPDATE subject coefficient...")
    try:
        update_data = {
            "name": f"Updated Test Subject {datetime.now().strftime('%H%M%S')}",
            "coefficient": 3.0
        }
        
        response = requests.put(
            f"{BASE_URL}/department-head/subjects/{created_subject_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            updated_subject = response.json()
            print(f"✅ Subject updated with new coefficient: {updated_subject.get('coefficient')}")
            print(f"   New name: {updated_subject.get('name')}")
        else:
            print(f"❌ Failed to update subject: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error updating subject: {str(e)}")
    
    print("\n5. Testing coefficient validation...")
    try:
        # Try to create subject with invalid coefficient (0)
        invalid_data = {
            "name": "Invalid Coefficient Test",
            "coefficient": 0,
            "levelId": level_id
        }
        
        response = requests.post(
            f"{BASE_URL}/department-head/subjects/",
            headers=headers,
            json=invalid_data
        )
        
        if response.status_code == 400:
            print(f"✅ Validation working: Invalid coefficient rejected")
        else:
            print(f"⚠️ Validation may not be working: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing validation: {str(e)}")
    
    print("\n6. Cleaning up - deleting test subject...")
    try:
        response = requests.delete(
            f"{BASE_URL}/department-head/subjects/{created_subject_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Test subject deleted successfully")
        else:
            print(f"⚠️ Failed to delete test subject: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error deleting subject: {str(e)}")
    
    print("\n🎯 Coefficient functionality testing complete!")

if __name__ == "__main__":
    print(f"📚 Subject Coefficient Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    test_subject_coefficient()
    
    print("="*60)