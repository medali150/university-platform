#!/usr/bin/env python3
"""
Quick fix for missing teacher and get final payloads
"""
import asyncio
from prisma import Prisma

async def fix_and_get_payloads():
    """Fix the teacher issue and get working payloads"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔧 FIXING DEPARTMENT RESOURCES")
        print("="*50)
        
        # Get user
        user = await prisma.user.find_unique(
            where={"email": "hathemhafsi@gmail.com"},
            include={
                "departmentHead": {"include": {"department": True}},
                "teacher": True
            }
        )
        
        print(f"👤 User: {user.firstName} {user.lastName}")
        print(f"🏢 Department: {user.departmentHead.department.name}")
        
        # Ensure teacher record exists and belongs to the right department
        if not user.teacher or user.teacher.departmentId != user.departmentHead.departmentId:
            if user.teacher:
                print("🔄 Updating existing teacher record...")
                await prisma.teacher.update(
                    where={"id": user.teacher.id},
                    data={"departmentId": user.departmentHead.departmentId}
                )
            else:
                print("👨‍🏫 Creating teacher record...")
                await prisma.teacher.create(
                    data={
                        "userId": user.id,
                        "departmentId": user.departmentHead.departmentId
                    }
                )
        
        # Get resources
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
        
        print(f"\n📊 Resources Check:")
        print(f"   📚 Subjects: {len(subjects)}")
        print(f"   👥 Groups: {len(groups)}")
        print(f"   👨‍🏫 Teachers: {len(teachers)}")
        print(f"   🏢 Rooms: {len(rooms)}")
        
        if subjects and groups and teachers and rooms:
            print(f"\n" + "="*60)
            print(f"🎯 FINAL WORKING PAYLOADS")
            print(f"="*60)
            
            print(f"\n1️⃣ LOGIN (use in /auth/login):")
            print(f'{{')
            print(f'  "login": "hathemhafsi@gmail.com",')
            print(f'  "password": "dslighgh15"')
            print(f'}}')
            
            print(f"\n2️⃣ SCHEDULE CREATION (use in POST /schedules/):")
            print(f'{{')
            print(f'  "date": "2025-10-04T08:00:00.000Z",')
            print(f'  "startTime": "2025-10-04T08:00:00.000Z",')
            print(f'  "endTime": "2025-10-04T10:00:00.000Z",')
            print(f'  "roomId": "{rooms[0].id}",')
            print(f'  "subjectId": "{subjects[0].id}",')
            print(f'  "groupId": "{groups[0].id}",')
            print(f'  "teacherId": "{teachers[0].id}",')
            print(f'  "status": "PLANNED"')
            print(f'}}')
            
            print(f"\n📋 What these IDs represent:")
            print(f"   Subject: {subjects[0].name}")
            print(f"   Group: {groups[0].name}")
            print(f"   Teacher: {teachers[0].id}")
            print(f"   Room: {rooms[0].code}")
            
            print(f"\n🚀 STEPS TO TEST IN SWAGGER:")
            print(f"1. Go to http://localhost:8000/docs")
            print(f"2. Use LOGIN payload in /auth/login")
            print(f"3. Copy access_token from response")
            print(f"4. Click Authorize, enter: Bearer YOUR_TOKEN")
            print(f"5. Use SCHEDULE payload in POST /schedules/")
            print(f"6. Should get 201 Created! ✅")
            
        else:
            print(f"❌ Still missing some resources")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_and_get_payloads())