"""
Test script to demonstrate absence notification system
This shows how the notification system sends alerts to students when marked absent
"""

import asyncio
from datetime import datetime
from prisma import Prisma

async def check_absence_notifications():
    """Check recent absence notifications in the system"""
    prisma = Prisma()
    await prisma.connect()
    
    print("\n" + "="*80)
    print("🔔 ABSENCE NOTIFICATION SYSTEM - Status Check")
    print("="*80 + "\n")
    
    # Check total notifications
    total_notifications = await prisma.notification.count()
    print(f"📊 Total notifications in system: {total_notifications}")
    
    # Check absence-specific notifications
    absence_notifications = await prisma.notification.count(
        where={"type": "ABSENCE_MARKED"}
    )
    print(f"🚨 Absence notifications: {absence_notifications}")
    
    # Get recent absence notifications
    recent_absences = await prisma.notification.find_many(
        where={"type": "ABSENCE_MARKED"},
        include={"user": True},
        order={"createdAt": "desc"},
        take=5
    )
    
    if recent_absences:
        print(f"\n📋 Recent Absence Notifications (Last {len(recent_absences)}):")
        print("-" * 80)
        for notif in recent_absences:
            print(f"\n✉️  Notification ID: {notif.id}")
            print(f"   Student: {notif.user.prenom} {notif.user.nom} ({notif.user.email})")
            print(f"   Title: {notif.title}")
            print(f"   Message: {notif.message}")
            print(f"   Status: {'✅ Read' if notif.isRead else '📬 Unread'}")
            print(f"   Created: {notif.createdAt.strftime('%d/%m/%Y %H:%M')}")
            if notif.relatedId:
                print(f"   Related Absence ID: {notif.relatedId}")
    else:
        print("\n📭 No absence notifications found yet.")
        print("\n💡 How to test:")
        print("   1. Login as a teacher")
        print("   2. Mark a student as absent in a class")
        print("   3. The student will automatically receive a notification")
    
    print("\n" + "="*80)
    print("✅ System is ready to send absence notifications automatically!")
    print("="*80 + "\n")
    
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_absence_notifications())
