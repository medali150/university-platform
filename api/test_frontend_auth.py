"""
Test frontend authentication and API access
"""
import requests

# Test login to get token
print("Testing login...")
login_data = {
    "email": "wahid@gmail.com", 
    "password": "dalighgh15"
}

response = requests.post("http://localhost:8000/auth/login", json=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"Got token: {token[:30]}...")
    
    # Test absences endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nTesting simple-absences endpoint...")
    response = requests.get("http://localhost:8000/simple-absences/all", headers=headers)
    print(f"Absences status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} absences")
        print("First absence structure:")
        if data:
            absence = data[0]
            print(f"- ID: {absence['id']}")
            print(f"- Student: {absence['student']['prenom']} {absence['student']['nom']}")
            print(f"- Subject: {absence['subject']['nom']}")  
            print(f"- Status: {absence['statut']}")
            print(f"- Date: {absence['emploitemps']['date']}")
    else:
        print(f"Error: {response.text}")
        
    # Test user info endpoint
    print("\nTesting user info...")
    response = requests.get("http://localhost:8000/auth/me", headers=headers)
    print(f"User info status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"User: {user_data.get('nom')} {user_data.get('prenom')}")
        print(f"Role: {user_data.get('role')}")
    else:
        print(f"User info error: {response.text}")
        
else:
    print(f"Login failed: {response.text}")