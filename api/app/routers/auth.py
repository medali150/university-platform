from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer
from typing import List, Optional
from prisma import Prisma
from datetime import timedelta

from app.db.prisma_client import get_prisma
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate, 
    department_id: Optional[str] = Query(None, description="Department ID for DEPARTMENT_HEAD role"),
    prisma: Prisma = Depends(get_prisma)
):
    """Register a new user and create corresponding role-specific record"""
    try:
        # Check if user already exists
        existing = await prisma.utilisateur.find_unique(where={"email": user_data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Get default data for role-specific tables
        default_department = await prisma.departement.find_first()
        default_specialty = await prisma.specialite.find_first()
        default_group = await prisma.groupe.find_first()
        
        if not default_department or not default_specialty or not default_group:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default department, specialty, or group not found. Please contact administrator."
            )
        
        # Create user first
        new_user = await prisma.utilisateur.create(
            data={
                "prenom": user_data.prenom,
                "nom": user_data.nom,
                "email": user_data.email,
                "mdp_hash": hashed_password,
                "role": user_data.role
            }
        )
        
        # Create role-specific record based on user role
        role_record_created = False
        try:
            if user_data.role == "STUDENT":
                # Create student record
                student = await prisma.etudiant.create(
                    data={
                        "nom": user_data.nom,
                        "prenom": user_data.prenom,
                        "email": user_data.email,
                        "id_groupe": default_group.id,
                        "id_specialite": default_specialty.id
                    }
                )
                # Update user with student relation
                new_user = await prisma.utilisateur.update(
                    where={"id": new_user.id},
                    data={"etudiant_id": student.id}
                )
                role_record_created = True
                
            elif user_data.role == "TEACHER":
                # Create teacher record
                teacher = await prisma.enseignant.create(
                    data={
                        "nom": user_data.nom,
                        "prenom": user_data.prenom,
                        "email": user_data.email,
                        "id_departement": default_department.id
                    }
                )
                # Update user with teacher relation
                new_user = await prisma.utilisateur.update(
                    where={"id": new_user.id},
                    data={"enseignant_id": teacher.id}
                )
                role_record_created = True
                
            elif user_data.role == "DEPARTMENT_HEAD":
                # For department heads, require specific department selection
                selected_department_id = department_id or default_department.id
                
                # Verify the selected department exists
                selected_department = await prisma.departement.find_unique(
                    where={"id": selected_department_id}
                )
                if not selected_department:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected department not found"
                    )
                
                # Create department head record
                dept_head = await prisma.chefdepartement.create(
                    data={
                        "id_utilisateur": new_user.id,
                        "id_departement": selected_department_id
                    }
                )
                role_record_created = True
                
            elif user_data.role == "ADMIN":
                # Create admin record
                admin = await prisma.administrateur.create(
                    data={
                        "id_utilisateur": new_user.id,
                        "niveau": "ADMIN"
                    }
                )
                role_record_created = True
                
        except Exception as role_error:
            # If role-specific record creation fails, delete the user to maintain consistency
            try:
                await prisma.utilisateur.delete(where={"id": new_user.id})
            except:
                pass  # User might already be deleted
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create role-specific record: {str(role_error)}"
            )
        
        if not role_record_created:
            # Clean up user if no role record was created
            try:
                await prisma.utilisateur.delete(where={"id": new_user.id})
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {user_data.role}"
            )
        
        return new_user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error in registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, prisma: Prisma = Depends(get_prisma)):
    """Login user and return JWT tokens"""
    user = await prisma.utilisateur.find_unique(where={"email": user_credentials.email})
    
    if not user or not verify_password(user_credentials.password, user.mdp_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(prisma: Prisma = Depends(get_prisma)):
    """Get all users"""
    users = await prisma.utilisateur.find_many()
    return users