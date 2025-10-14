"""
Test creating an absence for Wahid's student and check if notification is sent
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_wahid_absence():
    print("=" * 70)
    print("TESTING WAHID ABSENCE & NOTIFICATION SYSTEM")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login as Wahid (teacher)
        print("\n1. Logging in as Wahid (teacher)...")
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
            return
        
        teacher_token = login_response.json()["access_token"]
        print(f"   ✅ Logged in as teacher")
        
        # Step 2: Get the teacher's schedule
        print("\n2. Getting teacher's schedule...")
        schedule_response = await client.get(
            f"{BASE_URL}/schedules/teacher",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        if schedule_response.status_code != 200:
            print(f"   ❌ Failed to get schedule: {schedule_response.status_code}")
            print(f"   Response: {schedule_response.text}")
            return
        
        schedules = schedule_response.json()
        if not schedules or len(schedules) == 0:
            print(f"   ❌ No schedules found for Wahid")
            return
        
        schedule_id = schedules[0]["id"]
        print(f"   ✅ Found schedule: {schedule_id}")
        print(f"   Subject: {schedules[0].get('subjectName', 'N/A')}")
        
        # Step 3: Get student ID
        print("\n3. Getting Wahid's student ID...")
        from prisma import Prisma
        prisma = Prisma()
        await prisma.connect()
        
        student = await prisma.etudiant.find_unique(
            where={"email": "wahid.student@gmail.com"},
            include={"utilisateur": True}
        )
        
        if not student:
            print(f"   ❌ Student not found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Student ID: {student.id}")
        print(f"   Student User ID: {student.utilisateur.id if student.utilisateur else 'NO USER!'}")
        
        # Step 4: Check current notifications for student
        print("\n4. Checking current notifications...")
        notif_before = await prisma.notification.count(
            where={"id_utilisateur": student.utilisateur.id}
        )
        print(f"   Notifications before: {notif_before}")
        
        await prisma.disconnect()
        
        # Step 5: Create absence
        print("\n5. Creating absence...")
        absence_response = await client.post(
            f"{BASE_URL}/absences/",
            headers={"Authorization": f"Bearer {teacher_token}"},
            json={
                "studentId": student.id,
                "scheduleId": schedule_id,
                "reason": "Test absence from Wahid",
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
            return
        
        # Step 6: Check notifications after
        print("\n6. Checking notifications after absence...")
        await asyncio.sleep(1)  # Wait a moment for notification to be created
        
        await prisma.connect()
        notif_after = await prisma.notification.count(
            where={"id_utilisateur": student.utilisateur.id}
        )
        print(f"   Notifications after: {notif_after}")
        print(f"   New notifications: {notif_after - notif_before}")
        
        if notif_after > notif_before:
            print(f"\n   ✅✅✅ NOTIFICATION WAS CREATED! ✅✅✅")
            
            # Get the new notification
            notifications = await prisma.notification.find_many(
                where={"id_utilisateur": student.utilisateur.id},
                order={"date_creation": "desc"},
                take=1
            )
            
            if notifications:
                notif = notifications[0]
                print(f"\n   📧 Notification Details:")
                print(f"   Type: {notif.type}")
                print(f"   Title: {notif.titre}")
                print(f"   Message: {notif.message}")
                print(f"   Read: {notif.lu}")
        else:
            print(f"\n   ❌ NO NOTIFICATION CREATED!")
        
        await prisma.disconnect()
        
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
            print(f"   ❌ Student login failed")
            return
        
        student_token = student_login.json()["access_token"]
        
        notif_api = await client.get(
            f"{BASE_URL}/notifications/",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if notif_api.status_code == 200:
            notifs = notif_api.json()
            print(f"   ✅ API returned {len(notifs)} notifications")
            if len(notifs) > 0:
                print(f"   Latest: {notifs[0].get('title')}")
        else:
            print(f"   ❌ API failed: {notif_api.status_code}")
        
        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_wahid_absence())
