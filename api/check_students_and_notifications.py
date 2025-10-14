"""
Check available students and their credentials
"""
import asyncio
from prisma import Prisma

async def check_students():
    prisma = Prisma()
    await prisma.connect()
    
    print("=" * 60)
    print("CHECKING AVAILABLE STUDENTS")
    print("=" * 60)
    
    # Get all students
    students = await prisma.etudiant.find_many(
        include={"utilisateur": True, "specialite": True},
        take=5
    )
    
    print(f"\nFound {len(students)} students:\n")
    
    for i, student in enumerate(students, 1):
        print(f"{i}. {student.utilisateur.prenom} {student.utilisateur.nom}")
        print(f"   Email: {student.utilisateur.email}")
        print(f"   User ID: {student.utilisateur.id}")
        print(f"   Specialite: {student.specialite.nom if student.specialite else 'N/A'}")
        print()
    
    # Check if there are any notifications
    print("\n" + "=" * 60)
    print("CHECKING NOTIFICATIONS")
    print("=" * 60)
    
    all_notifs = await prisma.notification.find_many(
        order={"createdAt": "desc"},
        take=10
    )
    
    print(f"\nTotal notifications in database: {await prisma.notification.count()}")
    
    if all_notifs:
        print(f"\nLast {len(all_notifs)} notifications:")
        for notif in all_notifs:
            user = await prisma.utilisateur.find_unique(where={"id": notif.userId})
            print(f"\n- {notif.type}: {notif.title}")
            print(f"  User: {user.email if user else 'Unknown'}")
            print(f"  Message: {notif.message[:80]}...")
            print(f"  Read: {notif.isRead}")
            print(f"  Created: {notif.createdAt}")
    else:
        print("\n⚠️ No notifications found in database")
    
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_students())
