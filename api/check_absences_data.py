import asyncio
from app.db.prisma_client import get_prisma

async def check_absences():
    prisma = await get_prisma()
    try:
        count = await prisma.absence.count()
        print(f"Total absences: {count}")
        
        if count > 0:
            # Check what statuses exist
            absences = await prisma.absence.find_many()
            statuses = [abs.statut for abs in absences]
            unique_statuses = set(statuses)
            print(f"Existing statuses: {unique_statuses}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_absences())