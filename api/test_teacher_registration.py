import requests
import json

API_BASE = "http://localhost:8000"

# Test teacher registration with department as query parameter
teacher_data = {
    "nom": "TestTeacher",
    "prenom": "Test",  
    "email": "testteacher3@university.com",
    "password": "test123",
    "role": "TEACHER"
}

department_id = "cmgf7np350000bmb0jj5odswj"  # math department
url = f"{API_BASE}/auth/register?department_id={department_id}"

print("Testing teacher registration with department as query parameter...")
print("URL:", url)
print("Payload:", json.dumps(teacher_data, indent=2))

try:
    response = requests.post(url, json=teacher_data)
    print(f"Status: {response.status_code}")
    print("Response:", response.json())
except Exception as e:
    print(f"Error: {e}")