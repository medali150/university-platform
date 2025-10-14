"""
Simple test: Use existing schedule to create absence and test notification
"""
import asyncio
import requests
from prisma import Prisma
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

async def simple_test():
    print("=" * 70)
    print("SIMPLE ABSENCE NOTIFICATION TEST")
    print("=" * 70)
    
    prisma = Prisma()
    await prisma.connect()
    
    # Step 1: Get ANY schedule
    print("\n1. Finding any existing schedule...")
    schedule = await prisma.emploitemps.find_first(
        include={
            "matiere": True,
            "enseignant": {"include": {"utilisateur": True}},
            "groupe": True
        }
    )
    
    if not schedule:
        print("   ❌ No schedules found in database")
        await prisma.disconnect()
        return
    
    print(f"   ✅ Schedule: {schedule.matiere.nom}")
    print(f"   Teacher: {schedule.enseignant.utilisateur.email}")
    print(f"   Date: {schedule.date}")
    
    # Step 2: Get a student
    student = await prisma.etudiant.find_first(
        where={"utilisateur": {"email": "student1@university.tn"}},
        include={"utilisateur": True}
    )
    
    if not student:
        print("   ❌ Student not found")
        await prisma.disconnect()
        return
    
    print(f"   Student: {student.utilisateur.email}")
    print(f"   User ID: {student.utilisateur.id}")
    
    # Step 3: Check existing absences for this student on this schedule
    existing_absence = await prisma.absence.find_first(
        where={
            "id_etudiant": student.id,
            "id_emploitemps": schedule.id
        }
    )
    
    if existing_absence:
        print(f"\n   ⚠️ Absence already exists for this schedule")
        print(f"   Deleting old absence...")
        await prisma.absence.delete(where={"id": existing_absence.id})
    
    # Step 4: Check notifications BEFORE
    notif_count_before = await prisma.notification.count(
        where={"userId": student.utilisateur.id}
    )
    print(f"\n2. Notifications BEFORE: {notif_count_before}")
    
    # Step 5: Login as teacher
    print("\n3. Logging in as teacher...")
    teacher_email = schedule.enseignant.utilisateur.email
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": teacher_email, "password": "Test123!"}
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        await prisma.disconnect()
        return
    
    token_data = login_response.json()
    token = token_data.get("access_token") or token_data.get("token")
    print(f"   ✅ Logged in")
    
    # Step 6: Create absence via API
    print("\n4. Creating absence via API...")
    headers = {"Authorization": f"Bearer {token}"}
    absence_data = {
        "studentId": student.id,
        "scheduleId": schedule.id,
        "reason": "Test notification - Student was absent"
    }
    
    absence_response = requests.post(
        f"{BASE_URL}/absences/",
        json=absence_data,
        headers=headers
    )
    
    print(f"   Status: {absence_response.status_code}")
    
    if absence_response.status_code != 200:
        print(f"   ❌ Failed: {absence_response.text}")
        await prisma.disconnect()
        return
    
    result = absence_response.json()
    print(f"   ✅ Absence created!")
    print(f"   Absence ID: {result.get('id')}")
    
    # Step 7: Wait a moment and check notifications AFTER
    await asyncio.sleep(1)
    
    print("\n5. Checking notifications AFTER...")
    notif_count_after = await prisma.notification.count(
        where={"userId": student.utilisateur.id}
    )
    print(f"   Notifications AFTER: {notif_count_after}")
    print(f"   New notifications: {notif_count_after - notif_count_before}")
    
    if notif_count_after > notif_count_before:
        print("\n   ✅✅✅ NOTIFICATION WAS CREATED! ✅✅✅\n")
        
        # Get the notification
        notification = await prisma.notification.find_first(
            where={"userId": student.utilisateur.id},
            order={"createdAt": "desc"}
        )
        
        print(f"   Notification Details:")
        print(f"   - Type: {notification.type}")
        print(f"   - Title: {notification.title}")
        print(f"   - Message: {notification.message}")
        print(f"   - Read: {notification.isRead}")
        print(f"   - Created: {notification.createdAt}")
    else:
        print("\n   ❌❌❌ NO NOTIFICATION CREATED! ❌❌❌")
        print("\n   This means the notification system is NOT working.")
        print("   Check the absence_management.py file around line 121-135")
    
    # Step 8: Test frontend API
    print("\n6. Testing Frontend API...")
    
    student_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "student1@university.tn", "password": "Test123!"}
    )
    
    if student_login.status_code == 200:
        student_token = student_login.json().get("access_token") or student_login.json().get("token")
        
        # Get notifications
        notif_response = requests.get(
            f"{BASE_URL}/notifications/",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if notif_response.status_code == 200:
            notifs = notif_response.json()
            print(f"   ✅ API returned {len(notifs)} notifications")
            
            if len(notifs) > 0:
                print(f"\n   Latest notification from API:")
                latest = notifs[0]
                print(f"   - Type: {latest.get('type')}")
                print(f"   - Title: {latest.get('title')}")
                print(f"   - Message: {latest.get('message')[:60]}...")
        else:
            print(f"   ❌ API failed: {notif_response.text}")
    
    await prisma.disconnect()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(simple_test())
