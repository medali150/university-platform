"""
Find valid student and schedule IDs for absence testing
"""
import asyncio
from prisma import Prisma

async def find_valid_test_data():
    """Find valid student and schedule IDs for testing"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Finding valid test data...")
        print("=" * 50)
        
        # Find teacher by login
        user = await prisma.user.find_unique(
            where={"login": "souhir"},
            include={"teacher": True}
        )
        
        if not user or not user.teacher:
            print("❌ Teacher 'souhir' not found")
            return
        
        teacher_id = user.teacher.id
        print(f"✅ Teacher ID: {teacher_id}")
        print(f"   Name: {user.firstName} {user.lastName}")
        
        # Find schedules for this teacher
        schedules = await prisma.schedule.find_many(
            where={"teacherId": teacher_id},
            include={
                "subject": True,
                "group": True,
                "room": True
            }
        )
        
        if not schedules:
            print("❌ No schedules found for this teacher")
            return
            
        print(f"\n📅 Found {len(schedules)} schedules:")
        for i, schedule in enumerate(schedules):
            print(f"   {i+1}. {schedule.subject.name} - Group: {schedule.group.name}")
            print(f"      ID: {schedule.id}")
            print(f"      Date: {schedule.date}")
        
        # Use first schedule
        schedule = schedules[0]
        schedule_id = schedule.id
        group_id = schedule.groupId
        
        print(f"\n📋 Using Schedule: {schedule.id}")
        print(f"   Subject: {schedule.subject.name}")
        print(f"   Group: {schedule.group.name}")
        print(f"   Group ID: {group_id}")
        
        # Find students in this group
        students = await prisma.student.find_many(
            where={"groupId": group_id},
            include={"user": True}
        )
        
        if not students:
            print("❌ No students found in this group")
            
            # Let's check if there are any students at all
            all_students = await prisma.student.find_many(
                include={"user": True, "group": True}
            )
            
            print(f"\n📊 Total students in database: {len(all_students)}")
            if all_students:
                print("Available students:")
                for student in all_students[:5]:  # Show first 5
                    print(f"   • {student.user.firstName} {student.user.lastName}")
                    print(f"     ID: {student.id}")
                    print(f"     Group: {student.group.name if student.group else 'No group'}")
                    print(f"     Group ID: {student.groupId}")
                    print()
                    
                # Use the first available student for testing
                test_student = all_students[0]
                print(f"🧪 SWAGGER TEST PAYLOAD (using any available student):")
                print("=" * 50)
                payload = {
                    "studentId": test_student.id,
                    "scheduleId": schedule_id,
                    "reason": "Student was absent during class attendance"
                }
                print("```json")
                import json
                print(json.dumps(payload, indent=2))
                print("```")
                print("⚠️ Note: This student might not be in the teacher's group, so it might fail validation")
            return
        
        print(f"\n👥 Found {len(students)} students in group:")
        for i, student in enumerate(students):
            print(f"   {i+1}. {student.user.firstName} {student.user.lastName}")
            print(f"      ID: {student.id}")
            print(f"      Email: {student.user.email}")
        
        # Use first student
        student = students[0]
        
        print(f"\n🎯 FINAL SWAGGER TEST PAYLOAD:")
        print("=" * 50)
        payload = {
            "studentId": student.id,
            "scheduleId": schedule_id,
            "reason": "Student was absent during class attendance"
        }
        print("```json")
        import json
        print(json.dumps(payload, indent=2))
        print("```")
        print("=" * 50)
        
        return payload
        
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(find_valid_test_data())