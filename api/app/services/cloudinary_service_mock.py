"""
Mock Cloudinary service for testing without real credentials
This allows testing the image upload flow without Cloudinary
"""

from typing import Optional
import os
import hashlib
import time

class MockCloudinaryService:
    """Mock service for testing image uploads without real Cloudinary"""
    
    @staticmethod
    async def upload_image(file_content: bytes, public_id: Optional[str] = None) -> dict:
        """
        Mock image upload - simulates successful upload
        
        Args:
            file_content: The image file content as bytes
            public_id: Optional custom public ID for the image
            
        Returns:
            Dictionary containing mock upload result with URL and public_id
        """
        try:
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)
            
            # Generate a fake hash for the "uploaded" image
            file_hash = hashlib.md5(file_content).hexdigest()[:12]
            
            # Create mock public_id
            if not public_id:
                public_id = f"mock_upload_{int(time.time())}"
            
            mock_public_id = f"teacher_profiles/{public_id}"
            
            # Generate mock Cloudinary URL
            mock_url = f"https://res.cloudinary.com/demo/image/upload/v{int(time.time())}/{mock_public_id}.jpg"
            
            return {
                "success": True,
                "url": mock_url,
                "public_id": mock_public_id,
                "width": 400,
                "height": 400,
                "mock": True  # Indicator that this is a mock upload
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def delete_image(public_id: str) -> dict:
        """
        Mock image deletion - simulates successful deletion
        
        Args:
            public_id: The public ID of the image to delete
            
        Returns:
            Dictionary containing mock deletion result
        """
        try:
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "result": "ok",
                "mock": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_image_url(public_id: str, transformations: Optional[dict] = None) -> str:
        """
        Get mock image URL
        
        Args:
            public_id: The public ID of the image
            transformations: Optional transformations to apply
            
        Returns:
            Mock image URL
        """
        try:
            return f"https://res.cloudinary.com/demo/image/upload/w_200,h_200,c_fill,g_face,q_auto,f_jpg/{public_id}.jpg"
        except Exception:
            return ""


# Determine which service to use based on environment
def get_cloudinary_service():
    """Factory function to get the appropriate Cloudinary service"""
    
    # Check if real Cloudinary credentials are available
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY") 
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    # Use mock service if credentials are missing or contain placeholder values
    if (not cloud_name or not api_key or not api_secret or
        "your_" in api_key.lower() or "your_" in api_secret.lower() or
        api_key == "_RCDYxjOOd8xxvqkRjX78TrGd9Q"):
        
        print("⚠️ Using Mock Cloudinary Service (no real credentials)")
        return MockCloudinaryService
    
    try:
        # Try to use real Cloudinary service
        from app.services.cloudinary_service_real import RealCloudinaryService
        print("✅ Using Real Cloudinary Service")
        return RealCloudinaryService
    except ImportError:
        print("⚠️ Using Mock Cloudinary Service (real service not available)")
        return MockCloudinaryService


# Export the service
CloudinaryService = get_cloudinary_service()