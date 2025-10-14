#!/usr/bin/env python3
"""
Test specialities API response format
"""
import requests
import json

def test_specialities_response():
    """Test specialities API response format"""
    
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {
        "email": "test.depthead@university.com",
        "password": "test123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            # Test specialities endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/department-head/timetable/specialities", headers=headers)
            
            if response.status_code == 200:
                specialities = response.json()
                print(f"✅ Specialities API Response:")
                print(f"   📊 Count: {len(specialities)}")
                print(f"   📋 Response structure:")
                
                if specialities:
                    first_spec = specialities[0]
                    print(f"   🎓 First speciality:")
                    print(f"      • ID: {first_spec.get('id')}")
                    print(f"      • Name: {first_spec.get('nom')}")
                    print(f"      • Department ID: {first_spec.get('id_departement')}")
                    print(f"      • Counts: {first_spec.get('_count', {})}")
                    
                    print(f"\n   📋 All specialities:")
                    for i, spec in enumerate(specialities, 1):
                        count_info = spec.get('_count', {})
                        print(f"      {i}. {spec.get('nom')} (M:{count_info.get('matieres', 0)}, N:{count_info.get('niveaux', 0)}, E:{count_info.get('etudiants', 0)})")
                
                # Save to file for debugging
                with open('specialities_response.json', 'w', encoding='utf-8') as f:
                    json.dump(specialities, f, indent=2, ensure_ascii=False, default=str)
                    
                print(f"\n💾 Response saved to 'specialities_response.json'")
                
            else:
                print(f"❌ Specialities request failed: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specialities_response()