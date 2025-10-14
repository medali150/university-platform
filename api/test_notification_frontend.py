"""
Test notification system for frontend debugging
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_notifications():
    print("=" * 60)
    print("TESTING NOTIFICATION SYSTEM")
    print("=" * 60)
    
    # Test 1: Login as student
    print("\n1. Testing login...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "boubaker.fares@university.tn",
                "password": "Test123!"
            }
        )
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Error: {login_response.text}")
            return
            
        login_data = login_response.json()
        print(f"   Response keys: {list(login_data.keys())}")
        
        # Check for token
        token = None
        if "access_token" in login_data:
            token = login_data["access_token"]
        elif "token" in login_data:
            token = login_data["token"]
        else:
            print(f"   Full response: {json.dumps(login_data, indent=2)}")
            return
            
        print(f"   Token: {token[:30]}...")
        
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        return
    
    # Test 2: Get notification stats
    print("\n2. Testing notification stats...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        stats_response = requests.get(
            f"{BASE_URL}/notifications/stats",
            headers=headers
        )
        print(f"   Status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   Stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"   Error: {stats_response.text}")
            
    except Exception as e:
        print(f"   ❌ Stats request failed: {e}")
    
    # Test 3: Get all notifications
    print("\n3. Testing get notifications...")
    try:
        notifs_response = requests.get(
            f"{BASE_URL}/notifications/",
            headers=headers
        )
        print(f"   Status: {notifs_response.status_code}")
        
        if notifs_response.status_code == 200:
            notifs = notifs_response.json()
            print(f"   Count: {len(notifs)}")
            
            if len(notifs) > 0:
                print(f"\n   First notification:")
                print(f"   {json.dumps(notifs[0], indent=2, default=str)}")
            else:
                print(f"   ⚠️ No notifications found")
        else:
            print(f"   Error: {notifs_response.text}")
            
    except Exception as e:
        print(f"   ❌ Get notifications failed: {e}")
    
    # Test 4: Check database directly
    print("\n4. Checking database for notifications...")
    try:
        from prisma import Prisma
        import asyncio
        
        async def check_db():
            prisma = Prisma()
            await prisma.connect()
            
            # Get student ID
            student = await prisma.etudiant.find_first(
                where={"utilisateur": {"email": "boubaker.fares@university.tn"}},
                include={"utilisateur": True}
            )
            
            if student:
                user_id = student.utilisateur.id
                print(f"   Student user ID: {user_id}")
                
                # Count notifications
                notif_count = await prisma.notification.count(
                    where={"userId": user_id}
                )
                print(f"   Notifications in DB: {notif_count}")
                
                # Get notifications
                notifications = await prisma.notification.find_many(
                    where={"userId": user_id},
                    order={"createdAt": "desc"},
                    take=5
                )
                
                for notif in notifications:
                    print(f"\n   Notification:")
                    print(f"     - ID: {notif.id}")
                    print(f"     - Type: {notif.type}")
                    print(f"     - Title: {notif.title}")
                    print(f"     - Message: {notif.message[:50]}...")
                    print(f"     - Read: {notif.isRead}")
                    print(f"     - Created: {notif.createdAt}")
            else:
                print(f"   ⚠️ Student not found")
            
            await prisma.disconnect()
        
        asyncio.run(check_db())
        
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_notifications()
