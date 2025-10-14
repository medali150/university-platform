#!/usr/bin/env python3
"""
Simple test to verify schedule editing functionality
"""
import requests
import json

def test_schedule_edit():
    """Test the edit functionality by getting schedules and checking the data structure"""
    
    base_url = "http://localhost:8000"
    
    # Login with test credentials
    login_data = {
        "email": "test.depthead@university.com",
        "password": "test123"
    }
    
    print("🔐 Logging in...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get schedules to check data structure
            print("\n📋 Getting schedules to check data structure...")
            
            schedules_resp = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
            
            if schedules_resp.status_code == 200:
                schedules = schedules_resp.json()
                print(f"✅ Retrieved {len(schedules)} schedules")
                
                if schedules:
                    # Check the first schedule structure
                    schedule = schedules[0]
                    print(f"\n🔍 Analyzing first schedule structure:")
                    print(f"   ID: {schedule.get('id', 'MISSING')}")
                    print(f"   Date: {schedule.get('date', 'MISSING')}")
                    print(f"   Start Time: {schedule.get('heure_debut', 'MISSING')}")
                    print(f"   End Time: {schedule.get('heure_fin', 'MISSING')}")
                    
                    # Check nested relationships
                    matiere = schedule.get('matiere', {})
                    if matiere:
                        print(f"   Subject ID: {matiere.get('id', 'MISSING')}")
                        print(f"   Subject Name: {matiere.get('nom', 'MISSING')}")
                        specialite = matiere.get('specialite', {})
                        if specialite:
                            print(f"   Specialty ID: {specialite.get('id', 'MISSING')}")
                            print(f"   Specialty Name: {specialite.get('nom', 'MISSING')}")
                        else:
                            print("   ⚠️ WARNING: No specialite data in subject")
                    else:
                        print("   ❌ ERROR: No matiere data")
                    
                    groupe = schedule.get('groupe', {})
                    if groupe:
                        print(f"   Group ID: {groupe.get('id', 'MISSING')}")
                        print(f"   Group Name: {groupe.get('nom', 'MISSING')}")
                    else:
                        print("   ❌ ERROR: No groupe data")
                    
                    enseignant = schedule.get('enseignant', {})
                    if enseignant:
                        print(f"   Teacher ID: {enseignant.get('id', 'MISSING')}")
                    else:
                        print("   ❌ ERROR: No enseignant data")
                    
                    salle = schedule.get('salle', {})
                    if salle:
                        print(f"   Room ID: {salle.get('id', 'MISSING')}")
                    else:
                        print("   ❌ ERROR: No salle data")
                    
                    # Print full structure for debugging
                    print(f"\n📄 Full schedule structure:")
                    print(json.dumps(schedule, indent=2, default=str))
                    
                else:
                    print("❌ No schedules found")
            else:
                print(f"❌ Failed to get schedules - Status: {schedules_resp.status_code}")
                print(f"   Response: {schedules_resp.text}")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_schedule_edit()