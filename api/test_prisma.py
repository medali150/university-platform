import asyncio
from prisma import Prisma

async def test_student_query():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Test basic student query without include
        print("Testing basic student query...")
        students = await prisma.student.find_many()
        print(f"Found {len(students)} students")
        
        if students:
            # Test with include
            print("Testing student query with user include...")
            student_with_user = await prisma.student.find_first(
                include={"user": True}
            )
            print(f"Student with user: {student_with_user}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_student_query())