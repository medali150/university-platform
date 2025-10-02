#!/usr/bin/env python3
"""
Fixed version of image upload endpoint with comprehensive debugging
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_teacher
from app.services.cloudinary_service import CloudinaryService
from app.schemas.teacher import TeacherImageUpload
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teacher", tags=["Teacher Profile - Fixed"])

# Create a custom security dependency for debugging
security = HTTPBearer(auto_error=False)

async def debug_get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    prisma: Prisma = Depends(get_prisma)
):
    """Debug version of get_current_user with extensive logging"""
    
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    if not credentials:
        logger.error("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication credentials provided",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    logger.debug(f"Token received: {credentials.credentials[:20]}...")
    
    try:
        from app.core.jwt import decode_token
        payload = decode_token(credentials.credentials)
        logger.debug(f"Token payload: {payload}")
        
        if not payload or payload.get("type") != "access":
            logger.error(f"Invalid token payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type or payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_id = payload.get("sub")
        if not user_id:
            logger.error("No user ID in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - no user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = await prisma.utilisateur.find_unique(where={"id": user_id})
        if not user:
            logger.error(f"User not found for ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logger.debug(f"User authenticated: {user.email}, role: {user.role}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def debug_require_teacher(current_user = Depends(debug_get_current_user)):
    """Debug version of require_teacher with logging"""
    
    logger.debug(f"Checking teacher role for user: {current_user.email}")
    logger.debug(f"User role: {current_user.role}")
    logger.debug(f"User enseignant_id: {current_user.enseignant_id}")
    
    if current_user.role not in ["TEACHER", "DEPARTMENT_HEAD", "ADMIN"]:
        logger.error(f"Access denied for role: {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Teacher access required. Current role: {current_user.role}"
        )
    
    return current_user


@router.post("/profile/upload-image-debug", response_model=TeacherImageUpload)
async def upload_teacher_image_debug(
    request: Request,
    file: UploadFile = File(...),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(debug_require_teacher)
):
    """Debug version of upload teacher image endpoint"""
    
    logger.debug("=== UPLOAD IMAGE DEBUG ===")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Content-Type: {request.headers.get('content-type')}")
    logger.debug(f"Authorization: {request.headers.get('authorization', 'Not provided')[:50]}...")
    logger.debug(f"User: {current_user.email} (ID: {current_user.id})")
    logger.debug(f"Teacher ID: {current_user.enseignant_id}")
    logger.debug(f"File name: {file.filename}")
    logger.debug(f"File content type: {file.content_type}")
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an image. Received: {file.content_type}"
            )
        
        # Validate file size (max 5MB)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        
        logger.debug(f"File size: {len(file_content)} bytes")
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size must be less than 5MB. Current size: {len(file_content)} bytes"
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
        
        logger.debug(f"Teacher found: {teacher.nom} {teacher.prenom}")
        
        # Upload to Cloudinary
        logger.debug("Uploading to Cloudinary...")
        upload_result = await CloudinaryService.upload_image(
            file_content=file_content,
            public_id=f"teacher_{teacher.id}"
        )
        
        logger.debug(f"Cloudinary result: {upload_result}")
        
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
        
        logger.debug(f"Database updated with image URL: {upload_result['url']}")
        
        return TeacherImageUpload(
            success=True,
            message="Image uploaded successfully",
            image_url=upload_result["url"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/auth-check")
async def check_auth(current_user = Depends(debug_get_current_user)):
    """Simple endpoint to test authentication"""
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "enseignant_id": current_user.enseignant_id
        }
    }


@router.get("/teacher-check")
async def check_teacher_auth(current_user = Depends(debug_require_teacher)):
    """Test teacher-specific authentication"""
    return {
        "success": True,
        "message": "Teacher authentication successful",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "enseignant_id": current_user.enseignant_id
        }
    }


print("""
USAGE INSTRUCTIONS:

1. Add this router to your main.py:
   from fixed_image_upload import router as fixed_router
   app.include_router(fixed_router)

2. Test authentication first:
   GET /teacher/auth-check
   GET /teacher/teacher-check

3. Test image upload:
   POST /teacher/profile/upload-image-debug

4. Check the server logs for detailed debugging information.

COMMON FIXES FOR 401 ERRORS:

1. Token expired - login again to get fresh token
2. Wrong Authorization header format - should be "Bearer <token>"
3. CORS issues - check BACKEND_CORS_ORIGINS includes frontend URL
4. Token not found in localStorage - check browser dev tools
5. Multipart form issues - ensure Content-Type is NOT manually set

FRONTEND DEBUG STEPS:

1. Open browser dev tools
2. Check Network tab for the failed request
3. Look at Request Headers - Authorization should be "Bearer <token>"
4. Check Response for detailed error message
5. Verify token in localStorage is not expired
""")