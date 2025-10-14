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
    department_id: Optional[str] = Query(None, description="Department ID for DEPARTMENT_HEAD and TEACHER roles"),
    specialty_id: Optional[str] = Query(None, description="Specialty ID for STUDENT role"),
    group_id: Optional[str] = Query(None, description="Group ID for STUDENT role"),
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
        
        # Initialize default values
        default_department = None
        default_specialty = None
        default_group = None
        
        # Validate role-specific requirements
        if user_data.role == "TEACHER":
            # Teachers require department selection
            if not department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department ID is required for TEACHER role"
                )
            
            # Verify the selected department exists
            selected_department = await prisma.departement.find_unique(
                where={"id": department_id}
            )
            if not selected_department:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Selected department not found"
                )
        
        elif user_data.role == "STUDENT":
            # For students, validate specialty and group if provided
            if specialty_id:
                selected_specialty = await prisma.specialite.find_unique(
                    where={"id": specialty_id}
                )
                if not selected_specialty:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected specialty not found"
                    )
            
            if group_id:
                selected_group = await prisma.groupe.find_unique(
                    where={"id": group_id}
                )
                if not selected_group:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected group not found"
                    )
            
            # If no specialty/group provided, get defaults
            if not specialty_id or not group_id:
                default_specialty = await prisma.specialite.find_first()
                default_group = await prisma.groupe.find_first()
                
                if not specialty_id and not default_specialty:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No specialties found in the system. Please contact administrator."
                    )
                
                if not group_id and not default_group:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No groups found in the system. Please contact administrator."
                    )
        
        elif user_data.role == "TEACHER":
            # Teachers require department selection
            if not department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department ID is required for TEACHER role"
                )
        elif user_data.role == "DEPARTMENT_HEAD":
            # Department heads require department selection
            if not department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department ID is required for DEPARTMENT_HEAD role"
                )
        elif user_data.role == "ADMIN":
            # Admin roles don't need additional data
            pass
        
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
                # Determine specialty and group IDs
                final_specialty_id = specialty_id or (default_specialty.id if 'default_specialty' in locals() else None)
                final_group_id = group_id or (default_group.id if 'default_group' in locals() else None)
                
                if not final_specialty_id or not final_group_id:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not determine specialty or group for student"
                    )
                
                # Create student record
                student = await prisma.etudiant.create(
                    data={
                        "nom": user_data.nom,
                        "prenom": user_data.prenom,
                        "email": user_data.email,
                        "id_groupe": final_group_id,
                        "id_specialite": final_specialty_id
                    }
                )
                # Update user with student relation
                new_user = await prisma.utilisateur.update(
                    where={"id": new_user.id},
                    data={"etudiant_id": student.id}
                )
                role_record_created = True
                
            elif user_data.role == "TEACHER":
                # Verify the selected department exists
                selected_department = await prisma.departement.find_unique(
                    where={"id": department_id}
                )
                if not selected_department:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected department not found"
                    )
                
                # Create teacher record with selected department
                teacher = await prisma.enseignant.create(
                    data={
                        "nom": user_data.nom,
                        "prenom": user_data.prenom,
                        "email": user_data.email,
                        "id_departement": department_id
                    }
                )
                # Update user with teacher relation
                new_user = await prisma.utilisateur.update(
                    where={"id": new_user.id},
                    data={"enseignant_id": teacher.id}
                )
                role_record_created = True
                
            elif user_data.role == "DEPARTMENT_HEAD":
                # Verify the selected department exists
                selected_department = await prisma.departement.find_unique(
                    where={"id": department_id}
                )
                if not selected_department:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected department not found"
                    )
                
                # Check if this department already has a head
                existing_head = await prisma.chefdepartement.find_unique(
                    where={"id_departement": department_id}
                )
                if existing_head:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Department '{selected_department.nom}' already has a department head assigned"
                    )
                
                # Create department head record
                dept_head = await prisma.chefdepartement.create(
                    data={
                        "id_utilisateur": new_user.id,
                        "id_departement": department_id
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


@router.post("/login")
async def login(user_credentials: UserLogin, prisma: Prisma = Depends(get_prisma)):
    """Login user and return JWT tokens - Compatible with both frontend and admin panel"""
    
    # Get the email/login identifier
    identifier = user_credentials.email or user_credentials.login
    
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or login is required"
        )
    
    # Find user by email (both email and login map to email field)
    user = await prisma.utilisateur.find_unique(where={"email": identifier})
    
    if not user or not verify_password(user_credentials.password, user.mdp_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Simple response without complex models
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "prenom": user.prenom,
            "nom": user.nom,
            "role": user.role,
            # Admin panel compatibility
            "firstName": user.prenom,
            "lastName": user.nom,
            "login": user.email,
            "createdAt": user.createdAt.isoformat() if hasattr(user, 'createdAt') and user.createdAt else None,
            "updatedAt": user.updatedAt.isoformat() if hasattr(user, 'updatedAt') and user.updatedAt else None
        }
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


@router.get("/available-departments")
async def get_available_departments(prisma: Prisma = Depends(get_prisma)):
    """Get departments that don't have a department head assigned yet"""
    try:
        # Get all departments
        all_departments = await prisma.departement.find_many()
        
        # Get departments that already have heads
        occupied_departments = await prisma.chefdepartement.find_many(
            include={"departement": True}
        )
        occupied_dept_ids = {head.id_departement for head in occupied_departments}
        
        # Filter available departments
        available_departments = [
            {"id": dept.id, "nom": dept.nom}
            for dept in all_departments
            if dept.id not in occupied_dept_ids
        ]
        
        return {
            "available_departments": available_departments,
            "total_departments": len(all_departments),
            "occupied_departments": len(occupied_departments),
            "available_count": len(available_departments)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching available departments: {str(e)}"
        )


@router.get("/departments") 
async def get_all_departments(prisma: Prisma = Depends(get_prisma)):
    """Get all departments for teacher registration"""
    try:
        print("DEBUG: Attempting to fetch departments...")
        departments = await prisma.departement.find_many()
        print(f"DEBUG: Found {len(departments)} departments")
        
        # Simplify response
        dept_list = [{"id": dept.id, "nom": dept.nom} for dept in departments]
        return {"departments": dept_list}
    except Exception as e:
        print(f"DEBUG: Error in get_all_departments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching departments: {str(e)}"
        )


@router.get("/specialties")
async def get_specialties(department_id: Optional[str] = Query(None), prisma: Prisma = Depends(get_prisma)):
    """Get specialties, optionally filtered by department"""
    try:
        if department_id:
            specialties = await prisma.specialite.find_many(
                where={"id_departement": department_id},
                select={"id": True, "nom": True, "id_departement": True},
                include={"departement": {"select": {"nom": True}}}
            )
        else:
            specialties = await prisma.specialite.find_many(
                select={"id": True, "nom": True, "id_departement": True},
                include={"departement": {"select": {"nom": True}}}
            )
        return {"specialties": specialties}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching specialties: {str(e)}"
        )


@router.get("/groups")
async def get_groups(specialty_id: Optional[str] = Query(None), prisma: Prisma = Depends(get_prisma)):
    """Get groups, optionally filtered by specialty"""
    try:
        if specialty_id:
            groups = await prisma.groupe.find_many(
                where={"id_niveau": {"in": [niveau.id for niveau in await prisma.niveau.find_many(where={"id_specialite": specialty_id})]}},
                select={"id": True, "nom": True},
                include={"niveau": {"select": {"nom": True, "specialite": {"select": {"nom": True}}}}}
            )
        else:
            groups = await prisma.groupe.find_many(
                select={"id": True, "nom": True},
                include={"niveau": {"select": {"nom": True, "specialite": {"select": {"nom": True}}}}}
            )
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching groups: {str(e)}"
        )