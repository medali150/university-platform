#!/usr/bin/env python3
"""
Get working payloads for the department head user
"""
import asyncio
from prisma import Prisma

async def get_working_payloads():
    """Get the working payloads for Swagger testing"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🎯 WORKING SWAGGER PAYLOADS")
        print("="*80)
        
        # Get user info
        user = await prisma.user.find_unique(
            where={"email": "hathemhafsi@gmail.com"},
            include={
                "departmentHead": {"include": {"department": True}},
                "teacher": True
            }
        )
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 User: {user.firstName} {user.lastName}")
        print(f"🏢 Department: {user.departmentHead.department.name}")
        
        # Get resources for this department
        subjects = await prisma.subject.find_many(
            where={
                "level": {
                    "specialty": {
                        "departmentId": user.departmentHead.departmentId
                    }
                }
            },
            take=1
        )
        
        groups = await prisma.group.find_many(
            where={
                "level": {
                    "specialty": {
                        "departmentId": user.departmentHead.departmentId
                    }
                }
            },
            take=1
        )
        
        teachers = await prisma.teacher.find_many(
            where={"departmentId": user.departmentHead.departmentId},
            take=1
        )
        
        rooms = await prisma.room.find_many(take=1)
        
        print(f"\n📊 Available Resources:")
        print(f"   📚 Subjects: {len(subjects)}")
        print(f"   👥 Groups: {len(groups)}")
        print(f"   👨‍🏫 Teachers: {len(teachers)}")
        print(f"   🏢 Rooms: {len(rooms)}")
        
        if subjects and groups and teachers and rooms:
            print(f"\n1️⃣ LOGIN PAYLOAD (use in /auth/login):")
            print(f"─"*50)
            print(f'{{')
            print(f'  "login": "hathemhafsi@gmail.com",')
            print(f'  "password": "dslighgh15"')
            print(f'}}')
            
            print(f"\n2️⃣ SCHEDULE CREATION PAYLOAD (use in POST /schedules/):")
            print(f"─"*50)
            print(f'{{')
            print(f'  "date": "2025-10-04T10:00:00.000Z",')
            print(f'  "startTime": "2025-10-04T10:00:00.000Z",')
            print(f'  "endTime": "2025-10-04T12:00:00.000Z",')
            print(f'  "roomId": "{rooms[0].id}",')
            print(f'  "subjectId": "{subjects[0].id}",')
            print(f'  "groupId": "{groups[0].id}",')
            print(f'  "teacherId": "{teachers[0].id}",')
            print(f'  "status": "PLANNED"')
            print(f'}}')
            
            print(f"\n📋 Resource Details:")
            print(f"   Subject: {subjects[0].name}")
            print(f"   Group: {groups[0].name}")
            print(f"   Teacher ID: {teachers[0].id}")
            print(f"   Room: {rooms[0].code}")
            
            print(f"\n🔧 USAGE INSTRUCTIONS:")
            print(f"─"*50)
            print(f"1. Open Swagger UI at: http://localhost:8000/docs")
            print(f"2. Use LOGIN PAYLOAD in /auth/login endpoint")
            print(f"3. Copy the access_token from response")
            print(f"4. Click 'Authorize' button and enter: Bearer YOUR_TOKEN")
            print(f"5. Use SCHEDULE PAYLOAD in POST /schedules/ endpoint")
            print(f"6. Should get 201 Created response")
            
            print(f"\n" + "="*80)
            print(f"🎉 READY TO TEST!")
            
        else:
            print(f"❌ Missing resources")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(get_working_payloads())