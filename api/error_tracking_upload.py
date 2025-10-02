#!/usr/bin/env python3
"""
Enhanced error tracking for image upload endpoint
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Request
from typing import Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_teacher
import traceback
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teacher", tags=["Teacher Profile - Error Tracking"])


@router.post("/profile/upload-image-safe")
async def upload_teacher_image_safe(
    request: Request,
    file: UploadFile = File(...),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_teacher)
):
    """Safe version of upload with comprehensive error tracking"""
    
    try:
        logger.info("=== STARTING IMAGE UPLOAD ===")
        logger.info(f"User: {current_user.email} (ID: {current_user.id})")
        logger.info(f"Teacher ID: {current_user.enseignant_id}")
        logger.info(f"File: {file.filename}, Type: {file.content_type}")
        
        # Step 1: File validation
        logger.info("Step 1: File validation")
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an image. Received: {file.content_type}"
            )
        
        # Step 2: File size check
        logger.info("Step 2: File size check")
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        logger.info(f"File size: {len(file_content)} bytes")
        
        if len(file_content) > MAX_FILE_SIZE:
            logger.error(f"File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size must be less than 5MB. Current size: {len(file_content)} bytes"
            )
        
        # Step 3: Teacher record check
        logger.info("Step 3: Teacher record validation")
        if not current_user.enseignant_id:
            logger.error("No enseignant_id found for user")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No teacher record found for this user"
            )
        
        teacher = await prisma.enseignant.find_unique(
            where={"id": current_user.enseignant_id}
        )
        
        if not teacher:
            logger.error(f"Teacher not found for ID: {current_user.enseignant_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher profile not found"
            )
        
        logger.info(f"Teacher found: {teacher.nom} {teacher.prenom}")
        
        # Step 4: Cloudinary upload
        logger.info("Step 4: Cloudinary upload")
        try:
            from app.services.cloudinary_service import CloudinaryService
            
            upload_result = await CloudinaryService.upload_image(
                file_content=file_content,
                public_id=f"teacher_{teacher.id}"
            )
            
            logger.info(f"Cloudinary result: {upload_result}")
            
            if not upload_result.get("success"):
                logger.error(f"Cloudinary upload failed: {upload_result}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {upload_result.get('error', 'Unknown error')}"
                )
            
        except ImportError as e:
            logger.error(f"CloudinaryService import failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image upload service not available"
            )
        except Exception as e:
            logger.error(f"Cloudinary upload error: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(e)}"
            )
        
        # Step 5: Database update
        logger.info("Step 5: Database update")
        try:
            updated_teacher = await prisma.enseignant.update(
                where={"id": teacher.id},
                data={"image_url": upload_result["url"]}
            )
            logger.info(f"Database updated successfully. New image URL: {upload_result['url']}")
            
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            logger.error(traceback.format_exc())
            
            # Try to clean up uploaded image
            try:
                await CloudinaryService.delete_image(f"teacher_{teacher.id}")
            except:
                pass
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update database: {str(e)}"
            )
        
        logger.info("=== IMAGE UPLOAD SUCCESSFUL ===")
        
        # Step 6: Return response
        from app.schemas.teacher import TeacherImageUpload
        return TeacherImageUpload(
            success=True,
            message="Image uploaded successfully",
            image_url=upload_result["url"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in image upload: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/debug/test-components")
async def test_components():
    """Test all components individually"""
    
    results = {
        "database": False,
        "cloudinary_service": False,
        "teacher_schema": False,
        "environment": {}
    }
    
    # Test database
    try:
        prisma = Prisma()
        await prisma.connect()
        await prisma.utilisateur.find_first()
        await prisma.disconnect()
        results["database"] = True
    except Exception as e:
        results["database"] = f"Error: {str(e)}"
    
    # Test Cloudinary service
    try:
        from app.services.cloudinary_service import CloudinaryService
        results["cloudinary_service"] = True
    except Exception as e:
        results["cloudinary_service"] = f"Error: {str(e)}"
    
    # Test teacher schema
    try:
        from app.schemas.teacher import TeacherImageUpload
        results["teacher_schema"] = True
    except Exception as e:
        results["teacher_schema"] = f"Error: {str(e)}"
    
    # Test environment
    import os
    env_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    for var in env_vars:
        results["environment"][var] = bool(os.getenv(var))
    
    return results


print("""
USAGE INSTRUCTIONS:

1. Add this router to main.py:
   from error_tracking_upload import router as error_router
   app.include_router(error_router)

2. Test components first:
   GET /teacher/debug/test-components

3. Use the safe upload endpoint:
   POST /teacher/profile/upload-image-safe

4. Check server logs for detailed step-by-step information.

This will help identify exactly where the 500 error occurs.
""")