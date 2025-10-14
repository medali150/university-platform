"""
Complete test: Create absence and verify notification is sent
"""
import asyncio
import requests
from prisma import Prisma
from datetime import datetime, date

BASE_URL = "http://127.0.0.1:8000"

async def test_complete_flow():
    print("=" * 70)
    print("COMPLETE ABSENCE NOTIFICATION TEST")
    print("=" * 70)
    
    prisma = Prisma()
    await prisma.connect()
    
    # Step 1: Get a teacher
    print("\n1. Finding a teacher...")
    teacher = await prisma.enseignant.find_first(
        include={"utilisateur": True}
    )
    
    if not teacher:
        print("   ❌ No teacher found")
        await prisma.disconnect()
        return
    
    print(f"   ✅ Teacher: {teacher.utilisateur.email}")
    teacher_email = teacher.utilisateur.email
    
    # Step 2: Get a student
    print("\n2. Finding a student...")
    student = await prisma.etudiant.find_first(
        where={"utilisateur": {"email": "student1@university.tn"}},
        include={"utilisateur": True}
    )
    
    if not student:
        print("   ❌ Student not found")
        await prisma.disconnect()
        return
    
    print(f"   ✅ Student: {student.utilisateur.email}")
    print(f"   User ID: {student.utilisateur.id}")
    student_email = student.utilisateur.email
    student_user_id = student.utilisateur.id
    
    # Step 3: Find a schedule for today
    print("\n3. Finding today's schedule...")
    today = datetime.now().date()
    
    schedule = await prisma.emploitemps.find_first(
        where={
            "date": datetime.combine(today, datetime.min.time()),
            "id_enseignant": teacher.id
        },
        include={
            "matiere": True,
            "groupe": True,
            "salle": True,
            "enseignant": {"include": {"utilisateur": True}}
        }
    )
    
    if not schedule:
        print(f"   ⚠️ No schedule found for today ({today})")
        print("   Creating a test schedule...")
        
        # Get a subject
        matiere = await prisma.matiere.find_first()
        groupe = await prisma.groupe.find_first()
        salle = await prisma.salle.find_first()
        
        if not (matiere and groupe and salle):
            print("   ❌ Missing required data (matiere, groupe, or salle)")
            await prisma.disconnect()
            return
        
        schedule = await prisma.emploitemps.create(
            data={
                "id_enseignant": teacher.id,
                "id_matiere": matiere.id,
                "id_groupe": groupe.id,
                "id_salle": salle.id,
                "date": datetime.combine(today, datetime.min.time()),
                "heure_debut": "08:00",
                "heure_fin": "10:00",
                "jour_semaine": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][today.weekday()]
            },
            include={
                "matiere": True,
                "groupe": True,
                "salle": True,
                "enseignant": {"include": {"utilisateur": True}}
            }
        )
        print(f"   ✅ Created schedule: {schedule.matiere.nom}")
    else:
        print(f"   ✅ Schedule: {schedule.matiere.nom} at {schedule.heure_debut}")
    
    # Step 4: Login as teacher
    print("\n4. Logging in as teacher...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": teacher_email, "password": "Test123!"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            await prisma.disconnect()
            return
        
        token = login_response.json().get("access_token") or login_response.json().get("token")
        print(f"   ✅ Logged in successfully")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        await prisma.disconnect()
        return
    
    # Step 5: Check notifications BEFORE creating absence
    print("\n5. Checking notifications BEFORE absence...")
    notif_count_before = await prisma.notification.count(
        where={"userId": student_user_id}
    )
    print(f"   Student notifications: {notif_count_before}")
    
    # Step 6: Mark student absent
    print("\n6. Marking student absent...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        absence_data = {
            "studentId": student.id,
            "scheduleId": schedule.id,
            "reason": "Test absence for notification system"
        }
        
        absence_response = requests.post(
            f"{BASE_URL}/absences/",
            json=absence_data,
            headers=headers
        )
        
        print(f"   Status: {absence_response.status_code}")
        
        if absence_response.status_code == 200:
            result = absence_response.json()
            print(f"   ✅ Absence created: {result.get('id')}")
            absence_id = result.get('id')
        else:
            print(f"   ❌ Failed: {absence_response.text}")
            await prisma.disconnect()
            return
    except Exception as e:
        print(f"   ❌ Error creating absence: {e}")
        await prisma.disconnect()
        return
    
    # Step 7: Check notifications AFTER creating absence
    print("\n7. Checking notifications AFTER absence...")
    await asyncio.sleep(1)  # Give it a moment
    
    notif_count_after = await prisma.notification.count(
        where={"userId": student_user_id}
    )
    print(f"   Student notifications: {notif_count_after}")
    print(f"   New notifications: {notif_count_after - notif_count_before}")
    
    if notif_count_after > notif_count_before:
        print("\n   ✅ NOTIFICATION CREATED!")
        
        # Get the notification
        notification = await prisma.notification.find_first(
            where={"userId": student_user_id},
            order={"createdAt": "desc"}
        )
        
        print(f"\n   Notification Details:")
        print(f"   - ID: {notification.id}")
        print(f"   - Type: {notification.type}")
        print(f"   - Title: {notification.title}")
        print(f"   - Message: {notification.message}")
        print(f"   - Related ID: {notification.relatedId}")
        print(f"   - Read: {notification.isRead}")
        print(f"   - Created: {notification.createdAt}")
    else:
        print("\n   ❌ NO NOTIFICATION CREATED!")
        print("   The notification system may not be working properly.")
    
    # Step 8: Test frontend API
    print("\n8. Testing frontend API...")
    
    # Login as student
    try:
        student_login = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": student_email, "password": "Test123!"}
        )
        
        if student_login.status_code == 200:
            student_token = student_login.json().get("access_token") or student_login.json().get("token")
            print(f"   ✅ Student logged in")
            
            # Get notifications via API
            notif_response = requests.get(
                f"{BASE_URL}/notifications/",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            
            if notif_response.status_code == 200:
                notifs = notif_response.json()
                print(f"   ✅ API returned {len(notifs)} notifications")
                
                if len(notifs) > 0:
                    print(f"\n   First notification:")
                    print(f"   {notifs[0]}")
            else:
                print(f"   ❌ API failed: {notif_response.text}")
        else:
            print(f"   ❌ Student login failed: {student_login.text}")
    except Exception as e:
        print(f"   ❌ Frontend API test error: {e}")
    
    await prisma.disconnect()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
