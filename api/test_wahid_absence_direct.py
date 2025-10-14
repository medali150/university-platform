"""
Test creating an absence for Wahid's student - direct approach
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_wahid_absence():
    print("=" * 70)
    print("TESTING WAHID ABSENCE & NOTIFICATION SYSTEM")
    print("=" * 70)
    
    from prisma import Prisma
    prisma = Prisma()
    await prisma.connect()
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get schedule ID from database
        print("\n1. Getting Wahid's schedule from database...")
        teacher = await prisma.enseignant.find_unique(
            where={"email": "wahid@gmail.com"}
        )
        
        if not teacher:
            print("   ❌ Teacher not found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Teacher ID: {teacher.id}")
        
        schedule = await prisma.emploitemps.find_first(
            where={"id_enseignant": teacher.id},
            include={"matiere": True}
        )
        
        if not schedule:
            print("   ❌ No schedule found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Schedule ID: {schedule.id}")
        print(f"   Subject: {schedule.matiere.nom}")
        
        # Step 2: Get student
        print("\n2. Getting Wahid's student...")
        student = await prisma.etudiant.find_unique(
            where={"email": "wahid.student@gmail.com"},
            include={"utilisateur": True}
        )
        
        if not student:
            print(f"   ❌ Student not found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Student ID: {student.id}")
        if student.utilisateur:
            print(f"   ✅ Student User ID: {student.utilisateur.id}")
        else:
            print(f"   ❌ Student has NO utilisateur!")
            await prisma.disconnect()
            return
        
        # Step 3: Check current notifications
        print("\n3. Checking current notifications...")
        notif_before = await prisma.notification.count(
            where={"userId": student.utilisateur.id}
        )
        print(f"   Notifications before: {notif_before}")
        
        # Step 4: Login as teacher
        print("\n4. Logging in as Wahid (teacher)...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "wahid@gmail.com",
                "password": "Test123!"
            }
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            await prisma.disconnect()
            return
        
        teacher_token = login_response.json()["access_token"]
        print(f"   ✅ Logged in as teacher")
        
        # Step 5: Create absence
        print("\n5. Creating absence...")
        absence_response = await client.post(
            f"{BASE_URL}/absences/",
            headers={"Authorization": f"Bearer {teacher_token}"},
            json={
                "studentId": student.id,
                "scheduleId": schedule.id,
                "reason": "Test absence for notification",
                "status": "unjustified"
            }
        )
        
        print(f"   Status: {absence_response.status_code}")
        if absence_response.status_code == 200:
            result = absence_response.json()
            print(f"   ✅ Absence created!")
            print(f"   Absence ID: {result.get('id')}")
            print(f"   Notification sent: {result.get('notification_sent')}")
        else:
            print(f"   ❌ Failed: {absence_response.text}")
            await prisma.disconnect()
            return
        
        # Step 6: Check notifications after
        print("\n6. Checking notifications after absence...")
        await asyncio.sleep(1)  # Wait a moment
        
        notif_after = await prisma.notification.count(
            where={"userId": student.utilisateur.id}
        )
        print(f"   Notifications after: {notif_after}")
        print(f"   New notifications: {notif_after - notif_before}")
        
        if notif_after > notif_before:
            print(f"\n   ✅✅✅ NOTIFICATION WAS CREATED! ✅✅✅")
            
            # Get the new notification
            notifications = await prisma.notification.find_many(
                where={"userId": student.utilisateur.id},
                order={"createdAt": "desc"},
                take=1
            )
            
            if notifications:
                notif = notifications[0]
                print(f"\n   📧 Notification Details:")
                print(f"   Type: {notif.type}")
                print(f"   Title: {notif.title}")
                print(f"   Message: {notif.message}")
                print(f"   Read: {notif.isRead}")
        else:
            print(f"\n   ❌ NO NOTIFICATION CREATED!")
            print(f"\n   🔍 Let me check if there's an error in the logs...")
        
        # Step 7: Test student can see notification via API
        print("\n7. Testing student can access notification via API...")
        student_login = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "wahid.student@gmail.com",
                "password": "Test123!"
            }
        )
        
        if student_login.status_code != 200:
            print(f"   ❌ Student login failed: {student_login.text}")
            await prisma.disconnect()
            return
        
        student_token = student_login.json()["access_token"]
        print(f"   ✅ Student logged in")
        
        notif_api = await client.get(
            f"{BASE_URL}/notifications/",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if notif_api.status_code == 200:
            notifs = notif_api.json()
            print(f"   ✅ API returned {len(notifs)} notifications")
            if len(notifs) > 0:
                print(f"\n   📱 Latest notification:")
                print(f"   Title: {notifs[0].get('title')}")
                print(f"   Message: {notifs[0].get('message')}")
                print(f"   Type: {notifs[0].get('type')}")
        else:
            print(f"   ❌ API failed: {notif_api.status_code}")
            print(f"   Response: {notif_api.text}")
        
    await prisma.disconnect()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_wahid_absence())
