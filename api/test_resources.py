import requests
import json

# Test the resource endpoints and see what data is available
print("=== Testing Department Head Data Fetching ===\n")

# 1. Login first
print("1. Logging in...")
login_response = requests.post('http://localhost:8000/auth/login', json={
    'login': 'depthead', 
    'password': 'depthead123'
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful!")
    
    # 2. Test each resource endpoint
    endpoints = [
        ('Subjects', 'http://localhost:8000/schedules/resources/subjects'),
        ('Teachers', 'http://localhost:8000/schedules/resources/teachers'),
        ('Groups', 'http://localhost:8000/schedules/resources/groups'),
        ('Rooms', 'http://localhost:8000/schedules/resources/rooms'),
        ('Schedules', 'http://localhost:8000/schedules/')
    ]
    
    for name, url in endpoints:
        print(f"\n2.{endpoints.index((name, url))+1} Testing {name}...")
        try:
            response = requests.get(url, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data count: {len(data)}")
                if len(data) > 0:
                    print(f"   Sample data: {json.dumps(data[0], indent=2)[:200]}...")
                else:
                    print(f"   ⚠️ No data found for {name}")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print(f"\n=== Summary ===")
    print("If any resource has 0 items, that's why the dropdowns are empty!")
    print("We need to add sample data to the database.")
        
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")