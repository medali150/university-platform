"""
Test to see if the issue is with the frontend login/authentication
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_student_login_and_notifs():
    print("=" * 70)
    print("TESTING STUDENT LOGIN & NOTIFICATIONS API")
    print("=" * 70)
    
    # Login as student
    print("\n1. Login as student1...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "student1@university.tn",
            "password": "Test123!"
        }
    )
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed")
        print(f"   Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    print(f"   Response keys: {list(login_data.keys())}")
    
    # Try both possible token field names
    token = login_data.get("access_token") or login_data.get("token")
    
    if not token:
        print(f"   ❌ No token found in response")
        return
    
    print(f"   ✅ Token: {token[:30]}...")
    
    # Test /auth/me endpoint
    print("\n2. Testing /auth/me endpoint...")
    me_response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {me_response.status_code}")
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"   User: {me_data.get('email')}")
        print(f"   Role: {me_data.get('role')}")
    else:
        print(f"   Error: {me_response.text}")
    
    # Test notification stats
    print("\n3. Testing /notifications/stats...")
    stats_response = requests.get(
        f"{BASE_URL}/notifications/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   Total: {stats.get('total')}")
        print(f"   Unread: {stats.get('unread')}")
    else:
        print(f"   Error: {stats_response.text}")
    
    # Test get all notifications
    print("\n4. Testing /notifications/...")
    notifs_response = requests.get(
        f"{BASE_URL}/notifications/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {notifs_response.status_code}")
    if notifs_response.status_code == 200:
        notifs = notifs_response.json()
        print(f"   Count: {len(notifs)}")
        
        if len(notifs) > 0:
            print(f"\n   First notification:")
            n = notifs[0]
            print(f"   - ID: {n.get('id')}")
            print(f"   - Type: {n.get('type')}")
            print(f"   - Title: {n.get('title')}")
            print(f"   - Message: {n.get('message')[:60]}...")
            print(f"   - Read: {n.get('isRead')}")
            print(f"   - Created: {n.get('createdAt')}")
    else:
        print(f"   Error: {notifs_response.text}")
    
    print("\n" + "=" * 70)
    print("If all tests passed, the frontend should work!")
    print("Check browser console for any JavaScript errors.")
    print("=" * 70)

if __name__ == "__main__":
    test_student_login_and_notifs()
