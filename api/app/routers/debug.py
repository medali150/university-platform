from fastapi import APIRouter, Depends
from prisma import Prisma
from app.db.prisma_client import get_prisma

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/users")
async def get_all_users(prisma: Prisma = Depends(get_prisma)):
    """Get all users with their role-specific data for debugging"""
    users = await prisma.utilisateur.find_many(
        include={
            "enseignant": True,
            "etudiant": True,
            "administrateur": True,
            "chefDepartement": True
        }
    )
    
    result = []
    for user in users:
        user_data = {
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "role": user.role,
            "createdAt": user.createdAt,
            "role_specific_data": None
        }
        
        if user.enseignant:
            user_data["role_specific_data"] = {
                "type": "enseignant",
                "id": user.enseignant.id,
                "nom": user.enseignant.nom,
                "prenom": user.enseignant.prenom,
                "email": user.enseignant.email
            }
        elif user.etudiant:
            user_data["role_specific_data"] = {
                "type": "etudiant", 
                "id": user.etudiant.id,
                "nom": user.etudiant.nom,
                "prenom": user.etudiant.prenom,
                "email": user.etudiant.email
            }
        elif user.administrateur:
            user_data["role_specific_data"] = {
                "type": "administrateur",
                "id": user.administrateur.id,
                "niveau": user.administrateur.niveau
            }
        elif user.chefDepartement:
            user_data["role_specific_data"] = {
                "type": "chefDepartement",
                "id": user.chefDepartement.id
            }
        
        result.append(user_data)
    
    return {
        "total_users": len(result),
        "users": result
    }

@router.get("/schema-info")
async def get_schema_info(prisma: Prisma = Depends(get_prisma)):
    """Get database schema information"""
    try:
        # Count records in each table
        user_count = await prisma.utilisateur.count()
        student_count = await prisma.etudiant.count()
        teacher_count = await prisma.enseignant.count()
        admin_count = await prisma.administrateur.count()
        dept_head_count = await prisma.chefdepartement.count()
        subject_count = await prisma.matiere.count()
        department_count = await prisma.departement.count()
        specialty_count = await prisma.specialite.count()
        level_count = await prisma.niveau.count()
        group_count = await prisma.groupe.count()
        room_count = await prisma.salle.count()
        
        return {
            "database_status": "connected",
            "schema_version": "without_login_field",
            "table_counts": {
                "utilisateur": user_count,
                "etudiant": student_count,
                "enseignant": teacher_count,
                "administrateur": admin_count,
                "chefdepartement": dept_head_count,
                "matiere": subject_count,
                "departement": department_count,
                "specialite": specialty_count,
                "niveau": level_count,
                "groupe": group_count,
                "salle": room_count
            }
        }
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e)
        }