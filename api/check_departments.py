import asyncio
import sys
sys.path.append('.')

from prisma import Prisma

async def check_departments():
    prisma = Prisma()
    await prisma.connect()
    
    departments = await prisma.departement.find_many()
    
    if departments:
        print("Existing departments:")
        for dept in departments:
            print(f"  - {dept.nom} (ID: {dept.id})")
    else:
        print("No departments found in database!")
    
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_departments())
