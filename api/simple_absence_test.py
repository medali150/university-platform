"""
Simple test to get absences
"""
import requests

# Get token first
login_data = {
    "email": "wahid@gmail.com",
    "password": "dalighgh15"
}

response = requests.post("http://localhost:8000/auth/login", json=login_data)
token = response.json().get("access_token")

# Test the absences endpoint with curl equivalent
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Testing GET /absences/")
response = requests.get("http://localhost:8000/absences/", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")