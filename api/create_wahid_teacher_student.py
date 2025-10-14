"""
Create Wahid teacher account and a test student for absence notifications
"""
import asyncio
from prisma import Prisma
from datetime import datetime, timedelta
import bcrypt

async def create_wahid_accounts():
    prisma = Prisma()
    await prisma.connect()
    
    print("=" * 70)
    print("CREATING WAHID TEACHER & STUDENT ACCOUNTS")
    print("=" * 70)
    
    try:
        # Step 1: Check if Wahid teacher already exists
        print("\n1. Checking for existing Wahid teacher...")
        existing_user = await prisma.utilisateur.find_unique(
            where={"email": "wahid@gmail.com"}
        )
        
        if existing_user:
            print(f"   ⚠️ User already exists: {existing_user.email}")
            print(f"   Deleting old account...")
            await prisma.utilisateur.delete(where={"id": existing_user.id})
        
        # Also check and delete old Enseignant record
        existing_teacher = await prisma.enseignant.find_unique(
            where={"email": "wahid@gmail.com"}
        )
        
        if existing_teacher:
            print(f"   ⚠️ Teacher record exists, deleting...")
            await prisma.enseignant.delete(where={"id": existing_teacher.id})
        
        # Step 2: Get a department
        print("\n2. Getting department...")
        departement = await prisma.departement.find_first()
        
        if not departement:
            print("   ❌ No department found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Department: {departement.nom}")
        
        # Step 3: Create Wahid teacher
        print("\n3. Creating Wahid teacher...")
        password = "Test123!"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # First create the Enseignant
        enseignant = await prisma.enseignant.create(
            data={
                "nom": "Wahid",
                "prenom": "Test",
                "email": "wahid@gmail.com",
                "id_departement": departement.id
            }
        )
        
        print(f"   ✅ Teacher created: {enseignant.id}")
        
        # Then create the Utilisateur linked to this Enseignant
        teacher_user = await prisma.utilisateur.create(
            data={
                "email": "wahid@gmail.com",
                "mdp_hash": hashed_password,
                "nom": "Wahid",
                "prenom": "Test",
                "role": "TEACHER",
                "enseignant_id": enseignant.id
            }
        )
        
        print(f"   ✅ User created: {teacher_user.email}")
        print(f"   📧 Email: wahid@gmail.com")
        print(f"   🔑 Password: Test123!")
        
        # Step 4: Get a specialite (for student)
        print("\n4. Getting specialite for student...")
        specialite = await prisma.specialite.find_first(
            where={"id_departement": departement.id}
        )
        
        if not specialite:
            print("   ❌ No specialite found")
            await prisma.disconnect()
            return
        
        print(f"   ✅ Specialite: {specialite.nom}")
        
        # Step 5: Get a groupe
        groupe = await prisma.groupe.find_first()
        
        if not groupe:
            print("   ⚠️ No groupe found, creating one...")
            niveau = await prisma.niveau.find_first()
            if not niveau:
                print("   ❌ No niveau found")
                await prisma.disconnect()
                return
            
            groupe = await prisma.groupe.create(
                data={
                    "nom": "Test Group for Wahid",
                    "id_niveau": niveau.id
                }
            )
        
        print(f"   ✅ Groupe: {groupe.nom}")
        
        # Step 6: Check if student already exists
        print("\n5. Creating test student for Wahid...")
        existing_student_user = await prisma.utilisateur.find_unique(
            where={"email": "wahid.student@gmail.com"}
        )
        
        if existing_student_user:
            print(f"   ⚠️ Student already exists")
            print(f"   Deleting old account...")
            await prisma.utilisateur.delete(where={"id": existing_student_user.id})
        
        # Also check for Etudiant with same email
        existing_etudiant = await prisma.etudiant.find_unique(
            where={"email": "wahid.student@gmail.com"}
        )
        
        if existing_etudiant:
            print(f"   ⚠️ Etudiant record exists, deleting...")
            await prisma.etudiant.delete(where={"id": existing_etudiant.id})
        
        # Create student Etudiant first
        etudiant = await prisma.etudiant.create(
            data={
                "nom": "Student",
                "prenom": "Wahid",
                "email": "wahid.student@gmail.com",
                "id_specialite": specialite.id,
                "id_groupe": groupe.id
            }
        )
        
        print(f"   ✅ Etudiant created: {etudiant.id}")
        
        # Create student Utilisateur
        student_user = await prisma.utilisateur.create(
            data={
                "email": "wahid.student@gmail.com",
                "mdp_hash": hashed_password,
                "nom": "Student",
                "prenom": "Wahid",
                "role": "STUDENT",
                "etudiant_id": etudiant.id
            }
        )
        
        print(f"   ✅ Student user created: {student_user.email}")
        print(f"   📧 Email: wahid.student@gmail.com")
        print(f"   🔑 Password: Test123!")
        
        # Step 7: Create a schedule for Wahid to teach
        print("\n6. Creating schedule for Wahid's class...")
        
        # Get a matiere (Matiere has id_specialite and id_enseignant, no id_departement)
        matiere = await prisma.matiere.find_first(
            where={"id_specialite": specialite.id, "id_enseignant": enseignant.id}
        )
        
        if not matiere:
            print("   ⚠️ No matiere found, creating one...")
            matiere = await prisma.matiere.create(
                data={
                    "nom": "Test Subject for Wahid",
                    "id_specialite": specialite.id,
                    "id_enseignant": enseignant.id,
                    "coefficient": 2.0
                }
            )
        
        print(f"   ✅ Matiere: {matiere.nom}")
        
        # Get a salle
        salle = await prisma.salle.find_first()
        
        if not salle:
            print("   ⚠️ No salle found, creating one...")
            salle = await prisma.salle.create(
                data={
                    "nom": "Test Room",
                    "capacite": 30,
                    "type": "COURS"
                }
            )
        
        # Create schedule for today
        today = datetime.now()
        start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = today.replace(hour=12, minute=0, second=0, microsecond=0)
        
        schedule = await prisma.emploitemps.create(
            data={
                "id_enseignant": enseignant.id,
                "id_matiere": matiere.id,
                "id_groupe": groupe.id,
                "id_salle": salle.id,
                "date": today,
                "heure_debut": start_time,
                "heure_fin": end_time
            }
        )
        
        print(f"   ✅ Schedule created: {matiere.nom}")
        print(f"   📅 Date: {schedule.date}")
        print(f"   ⏰ Time: {schedule.heure_debut} - {schedule.heure_fin}")
        
        # Step 8: Print summary
        print("\n" + "=" * 70)
        print("ACCOUNTS CREATED SUCCESSFULLY!")
        print("=" * 70)
        
        print("\n👨‍🏫 TEACHER ACCOUNT (Wahid):")
        print(f"   Email: wahid@gmail.com")
        print(f"   Password: Test123!")
        print(f"   Teacher ID: {enseignant.id}")
        print(f"   User ID: {teacher_user.id}")
        
        print("\n👨‍🎓 STUDENT ACCOUNT:")
        print(f"   Email: wahid.student@gmail.com")
        print(f"   Password: Test123!")
        print(f"   Student ID: {etudiant.id}")
        print(f"   User ID: {student_user.id}")
        
        print("\n📚 SCHEDULE:")
        print(f"   Subject: {matiere.nom}")
        print(f"   Schedule ID: {schedule.id}")
        print(f"   Date: {schedule.date}")
        print(f"   Time: {schedule.heure_debut} - {schedule.heure_fin}")
        
        print("\n📝 TO TEST ABSENCE & NOTIFICATIONS:")
        print("   1. Login as teacher: wahid@gmail.com / Test123!")
        print("   2. Mark student absent (use schedule ID above)")
        print("   3. Login as student: wahid.student@gmail.com / Test123!")
        print("   4. Check notifications page")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_wahid_accounts())
