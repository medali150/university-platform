from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Optional, List
from datetime import datetime, date, time
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_teacher
from app.services.cloudinary_service_mock import CloudinaryService
from app.schemas.teacher import DepartmentUpdateRequest, TeacherImageUpload, TeacherProfileUpdate
from app.schemas.absence import TeacherGroupInfo, TeacherGroupDetails, StudentAbsenceInfo, MarkAbsenceRequest, TeacherAbsenceResponse

router = APIRouter(prefix="/teacher", tags=["Teacher Profile"])


@router.get("/profile")
async def get_teacher_profile(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get current teacher's profile with department and specialty information"""
    
    # Find the teacher record for the current user
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id},
        include={
            "departement": {
                "include": {
                    "specialites": {
                        "include": {
                            "niveaux": True
                        }
                    }
                }
            }
        }
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Get subjects taught by this teacher
    subjects = await prisma.matiere.find_many(
        where={"id_enseignant": teacher.id},
        include={
            "niveau": {
                "include": {
                    "specialite": True
                }
            }
        }
    )
    
    # Build profile response
    profile = {
        "teacher_info": {
            "id": teacher.id,
            "nom": teacher.nom,
            "prenom": teacher.prenom,
            "email": teacher.email,
            "image_url": teacher.image_url,
            "createdAt": teacher.createdAt
        },
        "department": {
            "id": teacher.departement.id,
            "nom": teacher.departement.nom,
            "specialties": [
                {
                    "id": spec.id,
                    "nom": spec.nom,
                    "levels": [
                        {
                            "id": level.id,
                            "nom": level.nom
                        } for level in spec.niveaux
                    ]
                } for spec in teacher.departement.specialites
            ]
        },
        "department_head": None,
        "subjects_taught": [
            {
                "id": subject.id,
                "nom": subject.nom,
                "level": {
                    "id": subject.niveau.id,
                    "nom": subject.niveau.nom,
                    "specialty": {
                        "id": subject.niveau.specialite.id,
                        "nom": subject.niveau.specialite.nom
                    }
                }
            } for subject in subjects
        ]
    }
    
    # Get department head info separately - first get the ChefDepartement record
    dept_head_record = await prisma.chefdepartement.find_unique(
        where={"id_departement": teacher.departement.id}
    )
    
    # Then get the user info if department head exists
    if dept_head_record:
        dept_head_user = await prisma.utilisateur.find_unique(
            where={"id": dept_head_record.id_utilisateur}
        )
        
        if dept_head_user:
            profile["department_head"] = {
                "nom": dept_head_user.nom,
                "prenom": dept_head_user.prenom,
                "email": dept_head_user.email
            }
    
    return profile


@router.put("/profile/department")
async def update_teacher_department(
    request: DepartmentUpdateRequest,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Update teacher's department"""
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Verify the new department exists
    department = await prisma.departement.find_unique(
        where={"id": request.new_department_id}
    )
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update teacher's department
    updated_teacher = await prisma.enseignant.update(
        where={"id": teacher.id},
        data={"id_departement": request.new_department_id},
        include={
            "departement": {
                "include": {
                    "specialites": True
                }
            }
        }
    )
    
    return {
        "message": "Department updated successfully",
        "new_department": {
            "id": updated_teacher.departement.id,
            "nom": updated_teacher.departement.nom,
            "specialties": [
                {
                    "id": spec.id,
                    "nom": spec.nom
                } for spec in updated_teacher.departement.specialites
            ]
        }
    }


@router.get("/departments")
async def get_available_departments(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all available departments that teacher can choose from"""
    
    departments = await prisma.departement.find_many(
        include={
            "specialites": {
                "include": {
                    "niveaux": True
                }
            }
        }
    )
    
    # Get department heads separately - first get all ChefDepartement records
    dept_head_records = await prisma.chefdepartement.find_many()
    
    # Create a mapping of department ID to department head user info
    dept_head_map = {}
    for dh_record in dept_head_records:
        # Get the user info for each department head
        dh_user = await prisma.utilisateur.find_unique(
            where={"id": dh_record.id_utilisateur}
        )
        if dh_user:
            dept_head_map[dh_record.id_departement] = {
                "nom": dh_user.nom,
                "prenom": dh_user.prenom,
                "email": dh_user.email
            }
    
    return [
        {
            "id": dept.id,
            "nom": dept.nom,
            "specialties": [
                {
                    "id": spec.id,
                    "nom": spec.nom,
                    "levels_count": len(spec.niveaux)
                } for spec in dept.specialites
            ],
            "department_head": dept_head_map.get(dept.id)
        } for dept in departments
    ]


@router.get("/subjects")
async def get_teacher_subjects(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all subjects taught by the current teacher"""
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    subjects = await prisma.matiere.find_many(
        where={"id_enseignant": teacher.id},
        include={
            "niveau": {
                "include": {
                    "specialite": {
                        "include": {
                            "departement": True
                        }
                    },
                    "groupes": True
                }
            }
        }
    )
    
    return [
        {
            "id": subject.id,
            "nom": subject.nom,
            "level": {
                "id": subject.niveau.id,
                "nom": subject.niveau.nom,
                "groups_count": len(subject.niveau.groupes)
            },
            "specialty": {
                "id": subject.niveau.specialite.id,
                "nom": subject.niveau.specialite.nom
            },
            "department": {
                "id": subject.niveau.specialite.departement.id,
                "nom": subject.niveau.specialite.departement.nom
            }
        } for subject in subjects
    ]


@router.post("/profile/upload-image", response_model=TeacherImageUpload)
async def upload_teacher_image(
    file: UploadFile = File(...),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Upload teacher profile image to Cloudinary"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Upload to Cloudinary
    upload_result = await CloudinaryService.upload_image(
        file_content=file_content,
        public_id=f"teacher_{teacher.id}"
    )
    
    if not upload_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {upload_result.get('error', 'Unknown error')}"
        )
    
    # Update teacher record with image URL
    updated_teacher = await prisma.enseignant.update(
        where={"id": teacher.id},
        data={"image_url": upload_result["url"]}
    )
    
    return TeacherImageUpload(
        success=True,
        message="Image uploaded successfully",
        image_url=upload_result["url"]
    )


@router.delete("/profile/image")
async def delete_teacher_image(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Delete teacher profile image"""
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    if not teacher.image_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No image found to delete"
        )
    
    # Extract public_id from Cloudinary URL
    # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/public_id.jpg
    try:
        public_id = f"teacher_profiles/teacher_{teacher.id}"
        
        # Delete from Cloudinary
        delete_result = await CloudinaryService.delete_image(public_id)
        
        if not delete_result["success"]:
            # Log the error but continue with database update
            print(f"Failed to delete image from Cloudinary: {delete_result.get('error')}")
        
        # Update teacher record to remove image URL
        await prisma.enseignant.update(
            where={"id": teacher.id},
            data={"image_url": None}
        )
        
        return {"message": "Image deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.put("/profile/info")
async def update_teacher_info(
    update_data: TeacherProfileUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Update teacher profile information"""
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Build update data (only include non-None values)
    update_fields = {}
    if update_data.nom is not None:
        update_fields["nom"] = update_data.nom
    if update_data.prenom is not None:
        update_fields["prenom"] = update_data.prenom
    if update_data.email is not None:
        update_fields["email"] = update_data.email
    if update_data.image_url is not None:
        update_fields["image_url"] = update_data.image_url
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update teacher record
    updated_teacher = await prisma.enseignant.update(
        where={"id": teacher.id},
        data=update_fields,
        include={
            "departement": True
        }
    )
    
    return {
        "message": "Profile updated successfully",
        "teacher_info": {
            "id": updated_teacher.id,
            "nom": updated_teacher.nom,
            "prenom": updated_teacher.prenom,
            "email": updated_teacher.email,
            "image_url": updated_teacher.image_url,
            "department": {
                "id": updated_teacher.departement.id,
                "nom": updated_teacher.departement.nom
            }
        }
    }


# ============================================================================
# ABSENCE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/groups", response_model=List[TeacherGroupInfo])
async def get_teacher_groups(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all groups that the teacher teaches"""
    
    # Find the teacher record
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Get all subjects taught by this teacher
    subjects = await prisma.matiere.find_many(
        where={"id_enseignant": teacher.id},
        include={
            "niveau": {
                "include": {
                    "specialite": {
                        "include": {
                            "departement": True
                        }
                    },
                    "groupes": {
                        "include": {
                            "_count": {
                                "select": {
                                    "etudiants": True
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    
    # Extract unique groups from subjects
    groups_map = {}
    for subject in subjects:
        for group in subject.niveau.groupes:
            if group.id not in groups_map:
                groups_map[group.id] = TeacherGroupInfo(
                    id=group.id,
                    nom=group.nom,
                    niveau={
                        "id": subject.niveau.id,
                        "nom": subject.niveau.nom
                    },
                    specialite={
                        "id": subject.niveau.specialite.id,
                        "nom": subject.niveau.specialite.nom,
                        "departement": subject.niveau.specialite.departement.nom
                    },
                    student_count=group._count.etudiants
                )
    
    return list(groups_map.values())


@router.get("/groups/{group_id}/students", response_model=TeacherGroupDetails)
async def get_group_students(
    group_id: str,
    schedule_id: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get all students in a group with their absence status for a specific schedule"""
    
    # Verify teacher has access to this group
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    # Check if teacher teaches this group
    teacher_subjects = await prisma.matiere.find_many(
        where={
            "id_enseignant": current_user.enseignant_id,
            "niveau": {
                "groupes": {
                    "some": {
                        "id": group_id
                    }
                }
            }
        }
    )
    
    if not teacher_subjects:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this group"
        )
    
    # Get group details
    group = await prisma.groupe.find_unique(
        where={"id": group_id},
        include={
            "niveau": {
                "include": {
                    "specialite": True
                }
            },
            "etudiants": True
        }
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Get student absence information
    students_info = []
    for student in group.etudiants:
        absence_info = StudentAbsenceInfo(
            id=student.id,
            nom=student.nom,
            prenom=student.prenom,
            email=student.email,
            is_absent=False,
            absence_id=None
        )
        
        # If schedule_id is provided, check if student is absent for this schedule
        if schedule_id:
            absence = await prisma.absence.find_first(
                where={
                    "id_etudiant": student.id,
                    "id_emploi": schedule_id
                }
            )
            
            if absence:
                absence_info.is_absent = True
                absence_info.absence_id = absence.id
        
        students_info.append(absence_info)
    
    return TeacherGroupDetails(
        id=group.id,
        nom=group.nom,
        niveau={
            "id": group.niveau.id,
            "nom": group.niveau.nom,
            "specialite": {
                "id": group.niveau.specialite.id,
                "nom": group.niveau.specialite.nom
            }
        },
        students=students_info
    )


@router.post("/absence/mark", response_model=TeacherAbsenceResponse)
async def mark_student_absence(
    absence_request: MarkAbsenceRequest,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Mark a student as absent or present for a specific schedule"""
    
    # Verify teacher has access to mark absence for this schedule
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    # Check if the schedule belongs to this teacher
    schedule = await prisma.emploitemps.find_unique(
        where={"id": absence_request.schedule_id},
        include={
            "matiere": True,
            "groupe": True
        }
    )
    
    if not schedule or schedule.id_enseignant != current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this schedule"
        )
    
    # Verify student exists and belongs to the group
    student = await prisma.etudiant.find_unique(
        where={"id": absence_request.student_id}
    )
    
    if not student or student.id_groupe != schedule.id_groupe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in this group"
        )
    
    # Check if absence record already exists
    existing_absence = await prisma.absence.find_first(
        where={
            "id_etudiant": absence_request.student_id,
            "id_emploi": absence_request.schedule_id
        }
    )
    
    if absence_request.is_absent:
        # Mark as absent
        if existing_absence:
            # Update existing absence
            updated_absence = await prisma.absence.update(
                where={"id": existing_absence.id},
                data={
                    "motif": absence_request.motif,
                    "statut": "PENDING"
                }
            )
            return TeacherAbsenceResponse(
                success=True,
                message="Student marked as absent (updated)",
                absence_id=updated_absence.id
            )
        else:
            # Create new absence record
            new_absence = await prisma.absence.create(
                data={
                    "id_etudiant": absence_request.student_id,
                    "id_emploi": absence_request.schedule_id,
                    "motif": absence_request.motif or "Marked absent by teacher",
                    "statut": "PENDING"
                }
            )
            return TeacherAbsenceResponse(
                success=True,
                message="Student marked as absent",
                absence_id=new_absence.id
            )
    else:
        # Mark as present (remove absence)
        if existing_absence:
            await prisma.absence.delete(
                where={"id": existing_absence.id}
            )
            return TeacherAbsenceResponse(
                success=True,
                message="Student marked as present (absence removed)",
                absence_id=None
            )
        else:
            return TeacherAbsenceResponse(
                success=True,
                message="Student was already marked as present",
                absence_id=None
            )


@router.get("/schedule")
async def get_teacher_schedule(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get teacher's schedule for a date range"""
    
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    from datetime import datetime, timedelta
    
    # Set default date range if not provided
    if not start_date:
        today = datetime.now().date()
        start_date = today.isoformat()
    
    if not end_date:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = start_dt + timedelta(days=6)  # Default to one week
        end_date = end_dt.date().isoformat()
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get teacher info
    teacher = await prisma.enseignant.find_unique(
        where={"id": current_user.enseignant_id}
    )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Get schedule for date range
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_enseignant": current_user.enseignant_id,
            "date": {
                "gte": start_dt,
                "lte": end_dt
            }
        },
        include={
            "matiere": True,
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            },
            "salle": True
        },
        order=[{"date": "asc"}, {"heure_debut": "asc"}]
    )
    
    # Format response
    formatted_schedules = []
    for schedule in schedules:
        formatted_schedules.append({
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "heure_debut": schedule.heure_debut.isoformat(),
            "heure_fin": schedule.heure_fin.isoformat(),
            "status": schedule.status,
            "matiere": {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            },
            "groupe": {
                "id": schedule.groupe.id,
                "nom": schedule.groupe.nom,
                "niveau": schedule.groupe.niveau.nom,
                "specialite": schedule.groupe.niveau.specialite.nom
            },
            "salle": {
                "id": schedule.salle.id,
                "code": schedule.salle.code,
                "type": schedule.salle.type
            }
        })
    
    return {
        "schedules": formatted_schedules,
        "teacher_info": {
            "id": teacher.id,
            "nom": teacher.nom,
            "prenom": teacher.prenom,
            "email": teacher.email
        },
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }


@router.get("/schedule/today")
async def get_today_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get today's schedule for the teacher"""
    
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    from datetime import datetime, time
    
    # Get today's date
    today = datetime.now().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    
    # Get today's schedule
    schedules = await prisma.emploitemps.find_many(
        where={
            "id_enseignant": current_user.enseignant_id,
            "date": {
                "gte": start_of_day,
                "lte": end_of_day
            }
        },
        include={
            "matiere": True,
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            },
            "salle": True
        },
        order={"heure_debut": "asc"}
    )
    
    return [
        {
            "id": schedule.id,
            "date": schedule.date.isoformat(),
            "heure_debut": schedule.heure_debut.isoformat(),
            "heure_fin": schedule.heure_fin.isoformat(),
            "matiere": {
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            },
            "groupe": {
                "id": schedule.groupe.id,
                "nom": schedule.groupe.nom,
                "niveau": schedule.groupe.niveau.nom,
                "specialite": schedule.groupe.niveau.specialite.nom
            },
            "salle": {
                "id": schedule.salle.id,
                "code": schedule.salle.code,
                "type": schedule.salle.type
            },
            "status": schedule.status
        } for schedule in schedules
    ]


@router.get("/stats")
async def get_teacher_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get teacher dashboard statistics"""
    
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    # Get today's date in local timezone
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    # Count today's classes
    today_classes = await prisma.emploidutemps.count(
        where={
            "id_enseignant": current_user.enseignant_id,
            "date": {
                "gte": start_of_day,
                "lte": end_of_day
            }
        }
    )
    
    # Count pending absences (this would require an absence management system)
    # For now, return mock data - in a real system, you'd query absence records
    pending_absences = 0
    
    # Count makeup requests (mock data for now)
    makeup_requests = 0
    
    # Count messages (mock data for now)
    messages = 0
    
    return {
        "today_classes": today_classes,
        "pending_absences": pending_absences,
        "makeup_requests": makeup_requests,
        "messages": messages
    }


@router.get("/groups/detailed")
async def get_teacher_groups_detailed(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Get detailed information about all groups the teacher teaches"""
    
    if not current_user.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No teacher record found for this user"
        )
    
    # Get all groups the teacher teaches with detailed information
    groups_data = await prisma.emploidutemps.find_many(
        where={
            "id_enseignant": current_user.enseignant_id
        },
        include={
            "groupe": {
                "include": {
                    "niveau": {
                        "include": {
                            "specialite": {
                                "include": {
                                    "departement": True
                                }
                            }
                        }
                    },
                    "etudiants": {
                        "include": {
                            "utilisateur": True
                        }
                    }
                }
            },
            "matiere": True
        },
        distinct=["id_groupe", "id_matiere"]
    )
    
    # Group the data by group and subject
    groups_map = {}
    
    for schedule in groups_data:
        group_id = schedule.groupe.id
        subject_id = schedule.matiere.id
        
        if group_id not in groups_map:
            groups_map[group_id] = {
                "id": schedule.groupe.id,
                "nom": schedule.groupe.nom,
                "level": schedule.groupe.niveau.nom,
                "specialty": schedule.groupe.niveau.specialite.nom,
                "department": schedule.groupe.niveau.specialite.departement.nom,
                "student_count": len(schedule.groupe.etudiants),
                "students": [
                    {
                        "id": student.utilisateur.id,
                        "nom": student.utilisateur.nom,
                        "prenom": student.utilisateur.prenom,
                        "email": student.utilisateur.email
                    } for student in schedule.groupe.etudiants
                ],
                "subjects": []
            }
        
        # Check if subject already added for this group
        subject_exists = any(s["id"] == subject_id for s in groups_map[group_id]["subjects"])
        if not subject_exists:
            groups_map[group_id]["subjects"].append({
                "id": schedule.matiere.id,
                "nom": schedule.matiere.nom
            })
    
    return {
        "groups": list(groups_map.values()),
        "total_groups": len(groups_map),
        "total_students": sum(group["student_count"] for group in groups_map.values())
    }