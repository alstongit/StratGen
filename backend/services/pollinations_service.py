import httpx
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import os

class PollinationsService:
    """Service for generating images using Pollinations.ai"""
    
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        
    async def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Pollinations.ai
        
        Args:
            prompt: Text description of the image
            width: Image width in pixels (default: 1080)
            height: Image height in pixels (default: 1080)
            seed: Random seed for reproducibility (optional)
            
        Returns:
            Dict with image URL and metadata
        """
        try:
            # Build Pollinations URL
            # Format: https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&seed={s}
            encoded_prompt = prompt.replace(" ", "%20")
            url = f"{self.base_url}/{encoded_prompt}"
            
            params = {
                "width": width,
                "height": height
            }
            
            if seed:
                params["seed"] = seed
            
            # Build full URL with params
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_str}"
            
            print(f"🎨 Generating image with Pollinations.ai...")
            print(f"   Prompt: {prompt[:100]}...")
            
            # Pollinations.ai returns the image directly
            # We just need to verify it's accessible
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.head(full_url)
                response.raise_for_status()
            
            print(f"✅ Image generated successfully")
            
            return {
                "url": full_url,
                "prompt": prompt,
                "width": width,
                "height": height,
                "seed": seed,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def download_image(
        self,
        image_url: str
    ) -> bytes:
        """
        Download image from Pollinations.ai
        
        Args:
            image_url: Full Pollinations.ai image URL
            
        Returns:
            Image bytes
        """
        try:
            print(f"⬇️ Downloading image from Pollinations.ai...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                image_bytes = response.content
                
            print(f"✅ Image downloaded ({len(image_bytes)} bytes)")
            
            return image_bytes
        
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            raise

# Create global instance
_pollinations_service = None

def get_pollinations_service() -> PollinationsService:
    """Get or create PollinationsService instance"""
    global _pollinations_service
    if _pollinations_service is None:
        _pollinations_service = PollinationsService()
    return _pollinations_service