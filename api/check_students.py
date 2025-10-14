import asyncio
from app.config.database import get_prisma

async def check_student_users():
    prisma = get_prisma()
    await prisma.connect()

    # Check for users with STUDENT role
    student_users = await prisma.utilisateur.find_many(
        where={"role": "STUDENT"},
        include={"etudiant": True}
    )
    
    print(f"Found {len(student_users)} student users:")
    for user in student_users:
        print(f"  - {user.nom} {user.prenom} ({user.email}) - Role: {user.role}")
        if user.etudiant:
            print(f"    Student profile exists")
        else:
            print(f"    No student profile")

    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_student_users())