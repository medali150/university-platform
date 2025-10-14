"""
Test notifications endpoint to verify data structure
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

# Common test credentials found in setup scripts
TEST_CREDENTIALS = {
    "email": "chef.dept1@university.tn",  # Department Head
    "password": "Test123!"
}

def test_notifications():
    print("🧪 Testing Notifications Endpoint\n")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1️⃣  Attempting login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=TEST_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            print("\n💡 Please update TEST_CREDENTIALS in the script with valid credentials")
            return
        
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful!")
        print(f"   User: {data.get('user', {}).get('email', 'N/A')}")
        print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test /notifications/stats
    print("\n2️⃣  Testing /notifications/stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/stats", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Response structure:")
            print(f"      - total: {stats.get('total')} (type: {type(stats.get('total')).__name__})")
            print(f"      - unread: {stats.get('unread')} (type: {type(stats.get('unread')).__name__})")
            
            # Check for unexpected fields
            expected_fields = {'total', 'unread'}
            actual_fields = set(stats.keys())
            unexpected = actual_fields - expected_fields
            if unexpected:
                print(f"   ⚠️  Unexpected fields: {unexpected}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Test /notifications/
    print("\n3️⃣  Testing /notifications/ endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Received {len(notifications)} notifications")
            
            if notifications:
                print(f"\n   📋 First notification structure:")
                notif = notifications[0]
                required_fields = ['id', 'userId', 'type', 'title', 'message', 'isRead', 'createdAt']
                optional_fields = ['relatedId']
                
                for field in required_fields:
                    value = notif.get(field)
                    print(f"      - {field}: {repr(value)[:50]} (type: {type(value).__name__})")
                
                for field in optional_fields:
                    if field in notif:
                        value = notif.get(field)
                        print(f"      - {field}: {repr(value)[:50]} (type: {type(value).__name__})")
                
                # Check for unexpected fields
                expected = set(required_fields + optional_fields)
                actual = set(notif.keys())
                unexpected = actual - expected
                if unexpected:
                    print(f"\n   ⚠️  Unexpected fields in notification: {unexpected}")
            else:
                print(f"   ℹ️  No notifications found (this is normal for a new user)")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Test with unread_only filter
    print("\n4️⃣  Testing /notifications/?unread_only=true...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/?unread_only=true", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Received {len(notifications)} unread notifications")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!\n")
    print("📝 Summary:")
    print("   - If you see data above, the API is working correctly")
    print("   - If you see authentication errors, update TEST_CREDENTIALS")
    print("   - Check that field names match frontend expectations:")
    print("     • userId (not user_id)")
    print("     • isRead (not is_read)")
    print("     • createdAt (not created_at)")
    print("     • relatedId (not related_id)")

if __name__ == "__main__":
    test_notifications()
