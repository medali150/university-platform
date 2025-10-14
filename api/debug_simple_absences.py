"""
Debug the simple absences endpoint to find the 500 error
"""
import asyncio
from prisma import Prisma

async def debug_simple_absences():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("Testing database query for absences...")
        
        # Try the same query as in simple_absences.py
        absences = await prisma.absence.find_many(
            include={
                "etudiant": {
                    "include": {"utilisateur": True}
                },
                "emploitemps": {
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {"utilisateur": True}
                        },
                        "groupe": True,
                        "salle": True
                    }
                }
            },
            order={"createdAt": "desc"}
        )
        
        print(f"✅ Found {len(absences)} absences")
        
        if absences:
            absence = absences[0]
            print(f"Testing data transformation for absence {absence.id}...")
            
            student_user = absence.etudiant.utilisateur
            teacher_user = absence.emploitemps.enseignant.utilisateur
            
            # Test the transformation logic
            transformed_absence = {
                "id": absence.id,
                "student": {
                    "nom": student_user.nom,
                    "prenom": student_user.prenom,
                    "email": student_user.email
                },
                "subject": {
                    "nom": absence.emploitemps.matiere.nom
                },
                "teacher": {
                    "nom": teacher_user.nom,
                    "prenom": teacher_user.prenom
                },
                "emploitemps": {
                    "date": absence.emploitemps.date.isoformat() if absence.emploitemps.date else None,
                    "heure_debut": absence.emploitemps.heure_debut.strftime("%H:%M:%S") if absence.emploitemps.heure_debut else None,
                    "heure_fin": absence.emploitemps.heure_fin.strftime("%H:%M:%S") if absence.emploitemps.heure_fin else None,
                    "groupe": {
                        "nom": absence.emploitemps.groupe.nom if absence.emploitemps.groupe else "N/A"
                    }
                },
                "motif": absence.motif or "Non spécifié",
                "statut": absence.statut,
                "justification_text": absence.justification_text,
                "createdAt": absence.createdAt.isoformat() if absence.createdAt else None,
                "updatedAt": absence.updatedAt.isoformat() if absence.updatedAt else None
            }
            
            print("✅ Data transformation successful")
            print(f"Sample transformed data: {transformed_absence}")
        else:
            print("No absences found for transformation test")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_simple_absences())