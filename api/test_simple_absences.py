"""
Test the new simple absences endpoint
"""
import requests
import json

# Get token first
login_data = {
    "email": "wahid@gmail.com",
    "password": "dalighgh15"
}

response = requests.post("http://localhost:8000/auth/login", json=login_data)
token = response.json().get("access_token")

# Test the new simple absences endpoint
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Testing GET /simple-absences/all")
response = requests.get("http://localhost:8000/simple-absences/all", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    absences = response.json()
    print(f"Found {len(absences)} absences")
    
    if absences:
        print(f"\nFirst absence:")
        print(json.dumps(absences[0], indent=2))
        
        # Test status update
        absence_id = absences[0]["id"]
        print(f"\nTesting status update for absence {absence_id}")
        
        status_update = {"status": "approved"}
        update_response = requests.put(
            f"http://localhost:8000/simple-absences/{absence_id}/status",
            json=status_update,
            headers=headers
        )
        print(f"Update status: {update_response.status_code}")
        print(f"Update response: {update_response.text}")
else:
    print(f"Error: {response.text}")