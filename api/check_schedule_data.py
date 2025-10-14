#!/usr/bin/env python3

import requests
import json

def test_schedule_data():
    """Test what schedule data exists for the student's group"""
    
    print("=== Checking Schedule Data ===")
    
    # Login as student  
    login_data = {
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    }
    
    login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get debug info to see student's group
    debug_response = requests.get("http://localhost:8000/student/debug", headers=headers)
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        student_info = debug_data["student"]
        group_info = debug_data["group"]
        
        print(f"Student: {student_info['prenom']} {student_info['nom']}")
        print(f"Student ID: {student_info['id']}")
        print(f"Group: {group_info['nom']}")
        print(f"Group ID: {student_info['id_groupe']}")
        print()
        
        # The issue is likely that there are no emploitemps (schedule) records
        # for this student's group, or the relationships are null
        # Let's create a simple test schedule endpoint that doesn't crash
        
        print("This suggests the schedule query is failing.")
        print("Possible issues:")
        print("1. No emploitemps records for group:", group_info['nom'])
        print("2. Missing relationships (matiere, enseignant, salle)")
        print("3. Date/time parsing issues")
        print()
        print("Need to create a safe schedule endpoint that handles missing data.")
        
    else:
        print(f"Debug failed: {debug_response.text}")

if __name__ == "__main__":
    test_schedule_data()