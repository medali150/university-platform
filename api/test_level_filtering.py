#!/usr/bin/env python3
"""
Test script to verify level filtering functionality
"""

import requests
import json

def test_level_filtering():
    """Test level filtering in subjects API"""
    
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
        
        # Get available levels
        print("\n📚 Getting available levels...")
        levels_response = requests.get(
            "http://localhost:8000/department-head/subjects/helpers/levels",
            headers=headers
        )
        
        if levels_response.status_code != 200:
            print(f"❌ Get levels failed: {levels_response.status_code}")
            return
        
        levels_data = levels_response.json()
        levels = levels_data.get('levels', [])
        
        print(f"✅ Got {len(levels)} levels:")
        for level in levels:
            print(f"  - {level.get('name')} (ID: {level.get('id')})")
        
        if not levels:
            print("❌ No levels available for testing")
            return
        
        # Test filtering with each level
        for level in levels:
            print(f"\n🔍 Testing filter for level: {level.get('name')} (ID: {level.get('id')})")
            
            filter_response = requests.get(
                f"http://localhost:8000/department-head/subjects/?page=1&pageSize=10&levelId={level.get('id')}",
                headers=headers
            )
            
            print(f"Status: {filter_response.status_code}")
            
            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                subjects = filter_data.get('data', [])
                total = filter_data.get('total', 0)
                
                print(f"✅ Found {total} subjects for level '{level.get('name')}'")
                
                if subjects:
                    for subject in subjects:
                        subject_level = subject.get('level', {}).get('name')
                        print(f"  - {subject.get('name')} (Level: {subject_level})")
            else:
                print(f"❌ Filter failed: {filter_response.text}")
        
        # Test with all subjects (no filter)
        print(f"\n📋 Testing with no filter (all subjects)...")
        all_response = requests.get(
            f"http://localhost:8000/department-head/subjects/?page=1&pageSize=100",
            headers=headers
        )
        
        if all_response.status_code == 200:
            all_data = all_response.json()
            all_subjects = all_data.get('data', [])
            total = all_data.get('total', 0)
            
            print(f"✅ Found {total} total subjects:")
            
            # Group by level for analysis
            by_level = {}
            for subject in all_subjects:
                level_name = subject.get('level', {}).get('name', 'Unknown')
                level_id = subject.get('levelId')
                if level_name not in by_level:
                    by_level[level_name] = {'count': 0, 'level_id': level_id}
                by_level[level_name]['count'] += 1
            
            for level_name, info in by_level.items():
                print(f"  - {level_name}: {info['count']} subjects (ID: {info['level_id']})")
        else:
            print(f"❌ Get all subjects failed: {all_response.text}")
            
    except requests.exceptions.ConnectionError:       
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_level_filtering()