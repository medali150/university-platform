from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from prisma import Prisma
from typing import List
import pandas as pd
import io
from datetime import datetime
import bcrypt

from app.db.prisma_client import get_prisma
from app.core.deps import require_role

router = APIRouter(prefix="/admin/bulk-import", tags=["Admin - Bulk Import"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@router.post("/students")
async def bulk_import_students(
    file: UploadFile = File(...),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN"]))
):
    """
    Bulk import students from Excel file
    
    Expected Excel columns:
    - nom (Last Name) - Required
    - prenom (First Name) - Required
    - email - Required, must be unique
    - groupe_nom (Group Name) - Required, must exist in database
    - password - Optional, default: "Student123"
    
    The student's specialite and niveau are automatically derived from the groupe.
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    # Read Excel file
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read Excel file: {str(e)}"
        )
    
    # Validate required columns
    required_columns = ['nom', 'prenom', 'email', 'groupe_nom']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}. Please download the correct template using the 'Télécharger le Modèle Excel' button."
        )
    
    try:
        
        results = {
            "total": len(df),
            "created": 0,
            "skipped": 0,
            "errors": []
        }
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row['email']):
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Missing email")
                    continue
                
                # Find group by name
                groupe = await prisma.groupe.find_first(
                    where={"nom": str(row['groupe_nom']).strip()}
                )
                
                if not groupe:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Group '{row['groupe_nom']}' not found")
                    continue
                
                # Check if email already exists in utilisateur table
                existing_user = await prisma.utilisateur.find_first(
                    where={"email": str(row['email']).strip().lower()}
                )
                
                if existing_user:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Email '{row['email']}' already exists")
                    continue
                
                # Get password or use default
                password = str(row.get('password', 'Student123')).strip()
                hashed_password = hash_password(password)
                
                # Get the specialite from the groupe
                groupe_with_specialite = await prisma.groupe.find_unique(
                    where={"id": groupe.id},
                    include={
                        "niveau": {
                            "include": {
                                "specialite": True
                            }
                        }
                    }
                )
                
                if not groupe_with_specialite or not groupe_with_specialite.niveau or not groupe_with_specialite.niveau.id_specialite:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Could not find specialite for group '{row['groupe_nom']}'")
                    continue
                
                # Get specialty from niveau
                specialite_id = groupe_with_specialite.niveau.id_specialite
                niveau_id = groupe_with_specialite.niveau.id
                
                # Create user account
                user = await prisma.utilisateur.create(
                    data={
                        "nom": str(row['nom']).strip(),
                        "prenom": str(row['prenom']).strip(),
                        "email": str(row['email']).strip().lower(),
                        "mdp_hash": hashed_password,
                        "role": "STUDENT"
                    }
                )
                
                # Create student profile (matching Prisma schema)
                etudiant = await prisma.etudiant.create(
                    data={
                        "nom": str(row['nom']).strip(),
                        "prenom": str(row['prenom']).strip(),
                        "email": str(row['email']).strip().lower(),
                        "id_groupe": groupe.id,
                        "id_specialite": specialite_id,
                        "id_niveau": niveau_id
                    }
                )
                
                # Link user to student
                await prisma.utilisateur.update(
                    where={"id": user.id},
                    data={"etudiant_id": etudiant.id}
                )
                
                results["created"] += 1
                
            except Exception as e:
                results["skipped"] += 1
                results["errors"].append(f"Row {index + 2}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Import completed. Created: {results['created']}, Skipped: {results['skipped']}",
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.post("/teachers")
async def bulk_import_teachers(
    file: UploadFile = File(...),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN"]))
):
    """
    Bulk import teachers from Excel file
    
    Expected Excel columns:
    - nom (Last Name) - Required
    - prenom (First Name) - Required
    - email - Required, must be unique
    - departement_nom (Department Name) - Required, must exist in database
    - password - Optional, default: "Teacher123"
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    # Read Excel file
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read Excel file: {str(e)}"
        )
    
    # Validate required columns
    required_columns = ['nom', 'prenom', 'email', 'departement_nom']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}. Please download the correct template using the 'Télécharger le Modèle Excel' button."
        )
    
    try:
        results = {
            "total": len(df),
            "created": 0,
            "skipped": 0,
            "errors": []
        }
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row['email']):
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Missing email")
                    continue
                
                # Find department by name
                departement = await prisma.departement.find_first(
                    where={"nom": str(row['departement_nom']).strip()}
                )
                
                if not departement:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Department '{row['departement_nom']}' not found")
                    continue
                
                # Check if email already exists in utilisateur table
                existing_user = await prisma.utilisateur.find_first(
                    where={"email": str(row['email']).strip().lower()}
                )
                
                if existing_user:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Email '{row['email']}' already exists")
                    continue
                
                # Get password or use default
                password = str(row.get('password', 'Teacher123')).strip()
                hashed_password = hash_password(password)
                
                # Create user account
                user = await prisma.utilisateur.create(
                    data={
                        "nom": str(row['nom']).strip(),
                        "prenom": str(row['prenom']).strip(),
                        "email": str(row['email']).strip().lower(),
                        "mdp_hash": hashed_password,
                        "role": "TEACHER"
                    }
                )
                
                # Create teacher profile (matching Prisma schema)
                enseignant = await prisma.enseignant.create(
                    data={
                        "nom": str(row['nom']).strip(),
                        "prenom": str(row['prenom']).strip(),
                        "email": str(row['email']).strip().lower(),
                        "id_departement": departement.id
                    }
                )
                
                # Link user to teacher
                await prisma.utilisateur.update(
                    where={"id": user.id},
                    data={"enseignant_id": enseignant.id}
                )
                
                results["created"] += 1
                
            except Exception as e:
                results["skipped"] += 1
                results["errors"].append(f"Row {index + 2}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Import completed. Created: {results['created']}, Skipped: {results['skipped']}",
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.get("/template/students")
async def download_students_template(
    current_user = Depends(require_role(["ADMIN"]))
):
    """Download Excel template for student bulk import"""
    
    template_data = {
        'nom': ['Dupont', 'Martin', 'Bernard', 'Dubois', 'Moreau'],
        'prenom': ['Jean', 'Marie', 'Pierre', 'Sophie', 'Lucas'],
        'email': ['jean.dupont@student.com', 'marie.martin@student.com', 'pierre.bernard@student.com', 'sophie.dubois@student.com', 'lucas.moreau@student.com'],
        'groupe_nom': ['DSI-3-1', 'DSI-3-2', 'DSI-3-3', 'DSI-3-4', 'DSI-3-5'],
        'password': ['Student123', 'Student123', 'Student123', 'Student123', 'Student123']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=students_template.xlsx'}
    )


@router.get("/template/teachers")
async def download_teachers_template(
    current_user = Depends(require_role(["ADMIN"]))
):
    """Download Excel template for teacher bulk import"""
    
    template_data = {
        'nom': ['Benali', 'Mansouri', 'Khelifi'],
        'prenom': ['Ahmed', 'Fatima', 'Karim'],
        'email': ['ahmed.benali@university.com', 'fatima.mansouri@university.com', 'karim.khelifi@university.com'],
        'departement_nom': ['Informatique', 'Informatique', 'Informatique'],
        'password': ['Teacher123', 'Teacher123', 'Teacher123']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Teachers')
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=teachers_template.xlsx'}
    )
