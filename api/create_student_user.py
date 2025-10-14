import requests
from prisma import Prisma
import asyncio
import bcrypt

BASE_URL = "http://localhost:8000"

async def create_student_user():
    prisma = Prisma()
    await prisma.connect()

    # Hash password
    password = "student123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create the student user
    student_user = await prisma.utilisateur.create(
        data={
            "nom": "Etudiant",
            "prenom": "Test",
            "email": "student@example.com",
            "role": "STUDENT",
            "mdp_hash": hashed_password
        }
    )

    # Create the student profile
    student = await prisma.etudiant.create(
        data={
            "nom": "Etudiant",
            "prenom": "Test",
            "email": "student@example.com",
            "numero_etudiant": "STU001",
            "id_specialite": "cmg6pgscn0003bm1oz90f1ut2",  # Informatique specialite
            "groupe": {
                "connect": {"id": "cmgb2nodn0001bmb4ll49wdg2"}  # L3-INFO-G1 group
            },
            "utilisateur": {
                "connect": {"id": student_user.id}
            }
        }
    )

    print(f"Created student user: {student.email}")
    print(f"Password: {password}")
    print(f"Group: L3-INFO-G1")

    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_student_user())