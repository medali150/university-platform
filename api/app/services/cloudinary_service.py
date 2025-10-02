"""
Cloudinary configuration for image uploads
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional
import os

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "your_cloud_name"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "your_api_key"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "your_api_secret")
)

class CloudinaryService:
    """Service for handling Cloudinary operations"""
    
    @staticmethod
    async def upload_image(file_content: bytes, public_id: Optional[str] = None) -> dict:
        """
        Upload image to Cloudinary
        
        Args:
            file_content: The image file content as bytes
            public_id: Optional custom public ID for the image
            
        Returns:
            Dictionary containing upload result with URL and public_id
        """
        try:
            upload_options = {
                "folder": "teacher_profiles",  # Organize images in folders
                "resource_type": "image",
                "format": "jpg",  # Convert to JPG for consistency
                "transformation": [
                    {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},  # Square crop focused on face
                    {"quality": "auto"}  # Automatic quality optimization
                ]
            }
            
            if public_id:
                upload_options["public_id"] = f"teacher_profiles/{public_id}"
            
            result = cloudinary.uploader.upload(
                file_content,
                **upload_options
            )
            
            return {
                "success": True,
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result.get("width"),
                "height": result.get("height")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def delete_image(public_id: str) -> dict:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: The public ID of the image to delete
            
        Returns:
            Dictionary containing deletion result
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_image_url(public_id: str, transformations: Optional[dict] = None) -> str:
        """
        Get optimized image URL with transformations
        
        Args:
            public_id: The public ID of the image
            transformations: Optional transformations to apply
            
        Returns:
            Optimized image URL
        """
        try:
            if transformations:
                url = cloudinary.CloudinaryImage(public_id).build_url(**transformations)
            else:
                # Default transformations for profile images
                url = cloudinary.CloudinaryImage(public_id).build_url(
                    width=200,
                    height=200,
                    crop="fill",
                    gravity="face",
                    quality="auto",
                    format="jpg"
                )
            return url
        except Exception:
            return ""