#!/usr/bin/env python3
"""
Debug script to check subjects pagination
"""

import requests
import json

def debug_subjects():
    """Debug subjects pagination"""
    
    try:
        # Login as department head
        print("🔐 Logging in as department head...")
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={
                "email": "test.depthead@university.com",
                "password": "test123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful!")
        
        # Test different pagination parameters
        for page_size in [10, 50, 1000]:
            print(f"\n📚 Testing pageSize={page_size}...")
            subjects_response = requests.get(
                f"http://localhost:8000/department-head/subjects/?page=1&pageSize={page_size}",
                headers=headers
            )
            
            print(f"Status: {subjects_response.status_code}")
            
            if subjects_response.status_code == 200:
                subjects_data = subjects_response.json()
                print(f"Total: {subjects_data.get('total', 0)}")
                print(f"Data count: {len(subjects_data.get('data', []))}")
                print(f"Page: {subjects_data.get('page', 0)}")
                print(f"TotalPages: {subjects_data.get('totalPages', 0)}")
                
                if subjects_data.get('data'):
                    first_subject = subjects_data['data'][0]
                    print(f"First subject: {first_subject.get('name', 'No name')} (ID: {first_subject.get('id', 'No ID')})")
                
            else:
                print(f"Error: {subjects_response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_subjects()