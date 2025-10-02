"""
Clean up existing absences and provide fresh test data
"""
import asyncio
from prisma import Prisma

async def clean_and_get_fresh_data():
    """Clean existing absences and get fresh test data"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🧹 Cleaning up test data...")
        print("=" * 50)
        
        # Find teacher
        user = await prisma.user.find_unique(
            where={"login": "souhir"},
            include={"teacher": True}
        )
        
        teacher_id = user.teacher.id
        
        # Get teacher's schedules
        schedules = await prisma.schedule.find_many(
            where={"teacherId": teacher_id},
            include={"subject": True, "group": True}
        )
        
        if not schedules:
            print("❌ No schedules found")
            return
            
        schedule = schedules[0]
        schedule_id = schedule.id
        
        print(f"📅 Using Schedule: {schedule_id}")
        print(f"   Subject: {schedule.subject.name}")
        print(f"   Group: {schedule.group.name}")
        
        # Check for existing absences in this schedule
        existing_absences = await prisma.absence.find_many(
            where={"scheduleId": schedule_id},
            include={"student": {"include": {"user": True}}}
        )
        
        print(f"\n📊 Found {len(existing_absences)} existing absences:")
        for absence in existing_absences:
            print(f"   • Student: {absence.student.user.firstName} {absence.student.user.lastName}")
            print(f"     ID: {absence.id}")
            print(f"     Reason: {absence.reason}")
            print(f"     Status: {absence.status}")
        
        if existing_absences:
            print(f"\n🗑️ Deleting {len(existing_absences)} existing absences...")
            for absence in existing_absences:
                await prisma.absence.delete(where={"id": absence.id})
                print(f"   ✅ Deleted absence {absence.id}")
        
        # Get students in this group
        students = await prisma.student.find_many(
            where={"groupId": schedule.groupId},
            include={"user": True}
        )
        
        if not students:
            print("❌ No students in group")
            return
            
        student = students[0]
        
        print(f"\n🎯 FRESH SWAGGER TEST PAYLOAD:")
        print("=" * 50)
        payload = {
            "studentId": student.id,
            "scheduleId": schedule_id,
            "reason": "Student was absent during class attendance"
        }
        
        import json
        print("```json")
        print(json.dumps(payload, indent=2))
        print("```")
        print("=" * 50)
        print("✅ Ready for testing! No existing absence conflicts.")
        
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(clean_and_get_fresh_data())