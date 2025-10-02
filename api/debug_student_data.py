#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')

from app.db.prisma_client import get_prisma

async def debug_students():
    """Debug student data structure"""
    prisma = get_prisma()
    
    try:
        # Connect to database
        await prisma.connect()
        
        # Get all students with full info
        students = await prisma.student.find_many(
            include={
                "user": True,
                "specialty": {
                    "include": {
                        "department": True
                    }
                },
                "group": {
                    "include": {
                        "level": True
                    }
                }
            }
        )
        
        print("=== STUDENT DATA STRUCTURE DEBUG ===")
        print(f"Total students found: {len(students)}")
        
        for i, student in enumerate(students):
            print(f"\n--- Student {i+1} ---")
            print(f"Student Record ID: {student.id}")
            print(f"User ID: {student.userId}")
            if student.user:
                print(f"User Name: {student.user.firstName} {student.user.lastName}")
                print(f"User Email: {student.user.email}")
                print(f"User Login: {student.user.login}")
            else:
                print("NO USER DATA!")
            
            if student.specialty:
                print(f"Specialty: {student.specialty.name}")
                if student.specialty.department:
                    print(f"Department: {student.specialty.department.name}")
            
            if student.group:
                print(f"Group: {student.group.name}")
                if student.group.level:
                    print(f"Level: {student.group.level.name}")
        
        print("\n=== API RESPONSE STRUCTURE ===")
        # Simulate what the API would return
        result = []
        for student in students:
            if student.user:
                user_data = {
                    "id": student.user.id,
                    "studentRecordId": student.id,  # This is what we added
                    "firstName": student.user.firstName,
                    "lastName": student.user.lastName,
                    "email": student.user.email,
                    "login": student.user.login,
                    "role": student.user.role,
                    "createdAt": student.user.createdAt,
                    "updatedAt": student.user.updatedAt,
                    "studentInfo": {
                        "id": student.id,
                        "specialty": student.specialty.name if student.specialty else None,
                        "department": student.specialty.department.name if student.specialty and student.specialty.department else None,
                        "level": student.group.level.name if student.group and student.group.level else None,
                        "group": student.group.name if student.group else None
                    }
                }
                result.append(user_data)
        
        print("API would return:")
        for item in result:
            print(f"  User ID: {item['id']} -> Student Record ID: {item['studentRecordId']} ({item['firstName']} {item['lastName']})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_students())