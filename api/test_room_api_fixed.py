"""
Quick test of room occupancy endpoint after datetime fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# First login to get a token
print("1. Logging in as department head...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "admin@example.com",
        "password": "admin123"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful, got token")

# Test room occupancy endpoint
print("\n2. Testing room occupancy endpoint...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{BASE_URL}/room-occupancy/rooms",
    headers=headers,
    params={"week_offset": 0}
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Room occupancy endpoint working!")
    data = response.json()
    print(f"\nResponse structure:")
    print(f"  - success: {data.get('success')}")
    print(f"  - data length: {len(data.get('data', []))}")
    print(f"  - week_info: {data.get('week_info')}")
    
    if data.get('data'):
        room = data['data'][0]
        print(f"\nFirst room:")
        print(f"  - roomId: {room.get('roomId')}")
        print(f"  - roomName: {room.get('roomName')}")
        print(f"  - capacity: {room.get('capacity')}")
        print(f"  - type: {room.get('type')}")
        print(f"  - Has occupancies: {bool(room.get('occupancies'))}")
else:
    print(f"❌ Room occupancy endpoint failed!")
    print(f"Response: {response.text}")

# Test room details endpoint
if response.status_code == 200 and data.get('data'):
    print("\n3. Testing room details endpoint...")
    room_id = data['data'][0]['roomId']
    details_response = requests.get(
        f"{BASE_URL}/room-occupancy/rooms/{room_id}/details",
        headers=headers
    )
    
    print(f"Status: {details_response.status_code}")
    if details_response.status_code == 200:
        print("✅ Room details endpoint working!")
        details = details_response.json()
        print(f"Room details: {json.dumps(details, indent=2)}")
    else:
        print(f"❌ Room details endpoint failed: {details_response.text}")

# Test statistics endpoint
print("\n4. Testing statistics endpoint...")
stats_response = requests.get(
    f"{BASE_URL}/room-occupancy/statistics",
    headers=headers,
    params={"week_offset": 0}
)

print(f"Status: {stats_response.status_code}")
if stats_response.status_code == 200:
    print("✅ Statistics endpoint working!")
    stats = stats_response.json()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
else:
    print(f"❌ Statistics endpoint failed: {stats_response.text}")

print("\n" + "="*50)
print("Testing complete!")
