from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from prisma import Prisma
from typing import List
import pandas as pd
import io
from datetime import datetime
import bcrypt
import logging

from app.db.prisma_client import get_prisma
from app.core.deps import require_role

# Setup logging
logger = logging.getLogger(__name__)

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
    
    logger.info(f"Starting bulk import for students. File: {file.filename}")
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    # Read Excel file
    try:
        contents = await file.read()
        logger.info(f"File read successfully. Size: {len(contents)} bytes")
        df = pd.read_excel(io.BytesIO(contents))
        logger.info(f"Excel parsed successfully. Rows: {len(df)}, Columns: {list(df.columns)}")
    except Exception as e:
        logger.error(f"Failed to read Excel file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read Excel file: {str(e)}"
        )
    
    # Validate required columns
    required_columns = ['nom', 'prenom', 'email', 'groupe_nom']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"Missing columns: {missing_columns}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}. Required columns are: {', '.join(required_columns)}. Your file has: {', '.join(df.columns)}"
        )
    
    try:
        
        results = {
            "total": len(df),
            "created": 0,
            "skipped": 0,
            "errors": []
        }
        
        logger.info(f"Processing {len(df)} rows...")
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row['email']) or pd.isna(row['nom']) or pd.isna(row['prenom']):
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Missing required fields (nom, prenom, or email)")
                    continue
                
                # Find group by name
                groupe_nom = str(row['groupe_nom']).strip()
                logger.info(f"Row {index + 2}: Looking for group '{groupe_nom}'")
                
                groupe = await prisma.groupe.find_first(
                    where={"nom": groupe_nom}
                )
                
                if not groupe:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {index + 2}: Group '{groupe_nom}' not found")
                    logger.warning(f"Group '{groupe_nom}' not found")
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
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN"]))
):
    """Download Excel template for student bulk import"""
    
    # Get actual groups from database
    groups = await prisma.groupe.find_many(
        take=5,
        include={
            "niveau": {
                "include": {
                    "specialite": True
                }
            }
        }
    )
    
    # Use real group names or fallback to examples
    group_names = [group.nom for group in groups] if groups else ['L3 GL Groupe 1', 'L3 GL Groupe 2']
    
    # Ensure we have at least 5 examples
    while len(group_names) < 5:
        group_names.append(group_names[0] if group_names else 'L3 GL Groupe 1')
    
    template_data = {
        'nom': ['Dupont', 'Martin', 'Bernard', 'Dubois', 'Moreau'],
        'prenom': ['Jean', 'Marie', 'Pierre', 'Sophie', 'Lucas'],
        'email': ['jean.dupont@student.com', 'marie.martin@student.com', 'pierre.bernard@student.com', 'sophie.dubois@student.com', 'lucas.moreau@student.com'],
        'groupe_nom': group_names[:5],
        'password': ['Student123', 'Student123', 'Student123', 'Student123', 'Student123']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
        
        # Add a help sheet with available groups
        if groups:
            help_data = {
                'Available Groups': [g.nom for g in groups],
                'Niveau': [g.niveau.nom if g.niveau else 'N/A' for g in groups],
                'Spécialité': [g.niveau.specialite.nom if g.niveau and g.niveau.specialite else 'N/A' for g in groups]
            }
            help_df = pd.DataFrame(help_data)
            help_df.to_excel(writer, index=False, sheet_name='Available Groups')
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=students_template.xlsx'}
    )


@router.get("/template/teachers")
async def download_teachers_template(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN"]))
):
    """Download Excel template for teacher bulk import"""
    
    # Get actual departments from database
    departments = await prisma.departement.find_many(take=5)
    
    # Use real department names or fallback to examples
    dept_names = [dept.nom for dept in departments] if departments else ['Informatique', 'Mathématiques', 'Physique']
    
    # Ensure we have at least 3 examples
    while len(dept_names) < 3:
        dept_names.append(dept_names[0] if dept_names else 'Informatique')
    
    template_data = {
        'nom': ['Benali', 'Mansouri', 'Khelifi'],
        'prenom': ['Ahmed', 'Fatima', 'Karim'],
        'email': ['ahmed.benali@university.com', 'fatima.mansouri@university.com', 'karim.khelifi@university.com'],
        'departement_nom': dept_names[:3],
        'password': ['Teacher123', 'Teacher123', 'Teacher123']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Teachers')
        
        # Add a help sheet with available departments
        if departments:
            help_data = {
                'Available Departments': [d.nom for d in departments]
            }
            help_df = pd.DataFrame(help_data)
            help_df.to_excel(writer, index=False, sheet_name='Available Departments')
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=teachers_template.xlsx'}
    )
