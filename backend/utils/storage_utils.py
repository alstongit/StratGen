from config.supabase_client import get_admin_supabase_client
from typing import Optional
import uuid

class StorageUtils:
    """Utility functions for Supabase Storage operations"""
    
    def __init__(self):
        self.supabase = get_admin_supabase_client()
        self.bucket_name = "campaign-images"
    
    async def upload_image(
        self,
        image_bytes: bytes,
        campaign_id: str,
        filename: str
    ) -> str:
        """
        Upload image to Supabase Storage
        
        Args:
            image_bytes: Image data as bytes
            campaign_id: Campaign ID for folder organization
            filename: Name for the file (e.g., "day_1.jpg")
            
        Returns:
            Public URL of uploaded image
        """
        try:
            # Create path: campaign-images/{campaign_id}/{filename}
            file_path = f"{campaign_id}/{filename}"
            
            print(f"📤 Uploading image to Supabase Storage...")
            print(f"   Path: {file_path}")
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=image_bytes,
                file_options={
                    "content-type": "image/jpeg",
                    "upsert": "true"  # Overwrite if exists
                }
            )
            
            # Get public URL
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            
            print(f"✅ Image uploaded successfully")
            print(f"   URL: {public_url}")
            
            return public_url
        
        except Exception as e:
            print(f"❌ Error uploading image: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_image_url(self, campaign_id: str, filename: str) -> str:
        """Get public URL for an image in storage"""
        file_path = f"{campaign_id}/{filename}"
        return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
    
    async def delete_image(self, campaign_id: str, filename: str) -> bool:
        """Delete image from storage"""
        try:
            file_path = f"{campaign_id}/{filename}"
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            print(f"✅ Image deleted: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting image: {e}")
            return False

# Global instance
_storage_utils = None

def get_storage_utils() -> StorageUtils:
    """Get or create StorageUtils instance"""
    global _storage_utils
    if _storage_utils is None:
        _storage_utils = StorageUtils()
    return _storage_utils