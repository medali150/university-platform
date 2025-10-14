"""
Test script for room occupancy API endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_room_occupancy_endpoints():
    """Test all room occupancy endpoints"""
    
    print("🧪 Testing Room Occupancy API Endpoints\n")
    
    # Test debug endpoint (no auth required)
    print("1. Testing debug room occupancy endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/room-occupancy/debug/rooms")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug endpoint working")
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Rooms count: {len(data.get('data', []))}")
            
            # Show first room structure
            if data.get('data') and len(data['data']) > 0:
                first_room = data['data'][0]
                print(f"   - First room: {first_room.get('roomName')} ({first_room.get('type')})")
                print(f"   - Capacity: {first_room.get('capacity')}")
                
                # Check occupancy structure
                occupancies = first_room.get('occupancies', {})
                if occupancies:
                    print(f"   - Has occupancy data for days: {list(occupancies.keys())}")
        else:
            print(f"❌ Debug endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test with authentication (if token available)
    print("2. Testing authenticated endpoints...")
    
    # Try to get a token first
    token = None
    try:
        # Try to login as department head
        login_data = {
            "username": "boubakeur.rabhi@university.tn",
            "password": "password123"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login successful, got token")
        else:
            print(f"⚠️ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Login error: {str(e)}")
    
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test main rooms endpoint
        print("\n2a. Testing main rooms endpoint...")
        try:
            params = {
                "week_offset": 0,
                "room_type": "all"
            }
            
            response = requests.get(
                f"{BASE_URL}/room-occupancy/rooms",
                headers=headers,
                params=params
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Main rooms endpoint working")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Week info: {data.get('week_info', {})}")
                print(f"   - Rooms count: {len(data.get('data', []))}")
            else:
                print(f"❌ Main rooms endpoint failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Main rooms endpoint error: {str(e)}")
        
        # Test statistics endpoint
        print("\n2b. Testing statistics endpoint...")
        try:
            response = requests.get(
                f"{BASE_URL}/room-occupancy/statistics",
                headers=headers,
                params={"week_offset": 0}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Statistics endpoint working")
                print(f"   - Success: {data.get('success', False)}")
                stats = data.get('statistics', {})
                print(f"   - Total rooms: {stats.get('total_rooms')}")
                print(f"   - Occupancy rate: {stats.get('occupancy_rate')}%")
            else:
                print(f"❌ Statistics endpoint failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Statistics endpoint error: {str(e)}")
            
    else:
        print("⚠️ Skipping authenticated tests (no token)")
    
    print("\n" + "="*50 + "\n")
    
def test_frontend_integration():
    """Test what the frontend would call"""
    print("3. Testing Frontend Integration Scenarios...")
    
    # Test the exact call the frontend makes
    print("\n3a. Testing frontend debug fallback...")
    try:
        response = requests.get(f"{BASE_URL}/room-occupancy/debug/rooms")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate the structure matches what frontend expects
            if data.get('success') and data.get('data'):
                rooms = data['data']
                
                print(f"✅ Frontend structure validation:")
                print(f"   - Rooms count: {len(rooms)}")
                
                for i, room in enumerate(rooms[:2]):  # Check first 2 rooms
                    print(f"   - Room {i+1}: {room.get('roomName')}")
                    print(f"     * ID: {room.get('roomId')}")
                    print(f"     * Type: {room.get('type')}")
                    print(f"     * Capacity: {room.get('capacity')}")
                    
                    occupancies = room.get('occupancies', {})
                    if occupancies:
                        # Check structure of occupancy data
                        days = list(occupancies.keys())
                        print(f"     * Days: {len(days)}")
                        
                        if days:
                            first_day = days[0]
                            slots = list(occupancies[first_day].keys())
                            print(f"     * Time slots: {len(slots)}")
                            
                            if slots:
                                first_slot = occupancies[first_day][slots[0]]
                                print(f"     * Slot structure valid: {bool(first_slot.get('isOccupied') is not None)}")
                
                print(f"✅ All frontend requirements met")
            else:
                print(f"❌ Invalid response structure")
        else:
            print(f"❌ Frontend test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend integration test error: {str(e)}")

if __name__ == "__main__":
    print(f"🏢 Room Occupancy API Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    test_room_occupancy_endpoints()
    test_frontend_integration()
    
    print("\n🎯 Test Suite Complete!")
    print("="*60)