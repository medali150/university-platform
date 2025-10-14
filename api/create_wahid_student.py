"""
Create test student account: wahid@gmail.com
Then test absence and notification system
"""
import asyncio
import bcrypt
from prisma import Prisma
from datetime import datetime
import requests

BASE_URL = "http://127.0.0.1:8000"

async def setup_test_student():
    print("=" * 70)
    print("CREATING TEST STUDENT: wahid@gmail.com")
    print("=" * 70)
    
    prisma = Prisma()
    await prisma.connect()
    
    # Step 1: Check if user already exists
    print("\n1. Checking if user exists...")
    existing_user = await prisma.utilisateur.find_unique(
        where={"email": "wahid@gmail.com"}
    )
    
    if existing_user:
        print(f"   ⚠️ User already exists with ID: {existing_user.id}")
        
        # Check if they have student profile via the user's etudiant relation
        user_with_student = await prisma.utilisateur.find_unique(
            where={"id": existing_user.id},
            include={"etudiant": True}
        )
        existing_student = user_with_student.etudiant if user_with_student else None
        
        if existing_student:
            print(f"   ✅ Student profile exists: {existing_student.id}")
            student = existing_student
            user = existing_user
        else:
            print("   Creating student profile...")
            # Get a specialite to assign
            specialite = await prisma.specialite.find_first()
            groupe = await prisma.groupe.find_first()
            
            student = await prisma.etudiant.create(
                data={
                    "numero_inscription": f"STU-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "id_utilisateur": existing_user.id,
                    "id_specialite": specialite.id if specialite else None,
                    "id_groupe": groupe.id if groupe else None
                }
            )
            print(f"   ✅ Student profile created: {student.id}")
            user = existing_user
    else:
        print("   User doesn't exist. Creating new user and student...")
        
        # Hash password: Test123!
        password = "Test123!"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Get a specialite and groupe
        specialite = await prisma.specialite.find_first()
        groupe = await prisma.groupe.find_first()
        
        if not specialite or not groupe:
            print("   ❌ Missing specialite or groupe in database")
            await prisma.disconnect()
            return
        
        # Create user
        user = await prisma.utilisateur.create(
            data={
                "email": "wahid@gmail.com",
                "password": hashed_password,
                "nom": "Wahid",
                "prenom": "Test",
                "role": "STUDENT"
            }
        )
        print(f"   ✅ User created: {user.id}")
        
        # Create student profile
        student = await prisma.etudiant.create(
            data={
                "numero_inscription": f"STU-WAHID-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "id_utilisateur": user.id,
                "id_specialite": specialite.id,
                "id_groupe": groupe.id
            }
        )
        print(f"   ✅ Student profile created: {student.id}")
        print(f"   📧 Email: wahid@gmail.com")
        print(f"   🔑 Password: Test123!")
    
    # Step 2: Test login
    print("\n2. Testing login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "wahid@gmail.com",
            "password": "Test123!"
        }
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get("access_token") or token_data.get("token")
        print(f"   ✅ Login successful!")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ❌ Login failed: {login_response.text}")
        await prisma.disconnect()
        return
    
    # Step 3: Check current notifications
    print("\n3. Checking current notifications...")
    notif_count = await prisma.notification.count(
        where={"userId": user.id}
    )
    print(f"   Current notifications: {notif_count}")
    
    # Step 4: Create an absence to trigger notification
    print("\n4. Creating absence to test notification...")
    
    # Get a schedule
    schedule = await prisma.emploitemps.find_first(
        include={
            "matiere": True,
            "enseignant": {"include": {"utilisateur": True}}
        }
    )
    
    if not schedule:
        print("   ❌ No schedule found")
        await prisma.disconnect()
        return
    
    print(f"   Using schedule: {schedule.matiere.nom}")
    print(f"   Teacher: {schedule.enseignant.utilisateur.email}")
    
    # Login as teacher
    teacher_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": schedule.enseignant.utilisateur.email,
            "password": "Test123!"
        }
    )
    
    if teacher_login.status_code != 200:
        print(f"   ❌ Teacher login failed")
        await prisma.disconnect()
        return
    
    teacher_token = teacher_login.json().get("access_token") or teacher_login.json().get("token")
    
    # Create absence
    absence_response = requests.post(
        f"{BASE_URL}/absences/",
        json={
            "studentId": student.id,
            "scheduleId": schedule.id,
            "reason": "Test absence for wahid@gmail.com"
        },
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    print(f"   Status: {absence_response.status_code}")
    
    if absence_response.status_code == 200:
        result = absence_response.json()
        print(f"   ✅ Absence created: {result.get('id')}")
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Check notifications again
        new_notif_count = await prisma.notification.count(
            where={"userId": user.id}
        )
        print(f"\n5. Notifications after absence: {new_notif_count}")
        
        if new_notif_count > notif_count:
            print(f"   ✅ NEW NOTIFICATION CREATED!")
            
            # Get the notification
            notification = await prisma.notification.find_first(
                where={"userId": user.id},
                order={"createdAt": "desc"}
            )
            
            print(f"\n   Notification Details:")
            print(f"   - Type: {notification.type}")
            print(f"   - Title: {notification.title}")
            print(f"   - Message: {notification.message}")
            print(f"   - Read: {notification.isRead}")
            
            # Test frontend API
            print(f"\n6. Testing frontend notification API...")
            notif_api_response = requests.get(
                f"{BASE_URL}/notifications/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if notif_api_response.status_code == 200:
                notifs = notif_api_response.json()
                print(f"   ✅ API returned {len(notifs)} notifications")
                
                if len(notifs) > 0:
                    print(f"\n   Latest from API:")
                    latest = notifs[0]
                    print(f"   - {latest.get('title')}")
                    print(f"   - {latest.get('message')[:70]}...")
            else:
                print(f"   ❌ API failed: {notif_api_response.text}")
        else:
            print(f"   ❌ No new notification created")
    else:
        print(f"   ❌ Failed: {absence_response.text}")
    
    await prisma.disconnect()
    
    print("\n" + "=" * 70)
    print("TEST STUDENT ACCOUNT READY!")
    print("=" * 70)
    print("\n📧 Email: wahid@gmail.com")
    print("🔑 Password: Test123!")
    print("\nYou can now login to the frontend with these credentials")
    print("and check the notifications page!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(setup_test_student())
