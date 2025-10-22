import aiohttp
from typing import Dict, Any
import urllib.parse

class PollinationsService:
    """Service for generating images using Pollinations.ai"""
    
    def __init__(self):
        # Use image.pollinations.ai directly (the actual image endpoint)
        self.base_url = "https://image.pollinations.ai/prompt"
        print("✅ PollinationsService initialized")
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Generate an image using Pollinations.ai
        
        Args:
            prompt: Text description of the image (keep it short!)
            width: Image width (default 1024)
            height: Image height (default 1024)
        
        Returns:
            Dict with image_url
        """
        try:
            # Clean and shorten prompt - Pollinations works best with short prompts
            clean_prompt = prompt.strip()
            
            # Remove any special formatting
            clean_prompt = clean_prompt.replace("**", "").replace("*", "")
            clean_prompt = clean_prompt.replace("\n", " ").replace("\r", " ")
            
            # Limit to 100 characters for best results
            if len(clean_prompt) > 100:
                clean_prompt = clean_prompt[:97] + "..."
            
            # URL encode the prompt
            encoded_prompt = urllib.parse.quote(clean_prompt)
            
            # Build clean URL: image.pollinations.ai/prompt/<prompt>
            image_url = f"{self.base_url}/{encoded_prompt}"
            
            print(f"🎨 Generated Pollinations URL: {image_url}")
            
            # Return the URL - Pollinations generates on-demand
            return {
                "image_url": image_url,
                "prompt": clean_prompt,
                "width": width,
                "height": height
            }
        
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise

# Global instance
_pollinations_service = None

def get_pollinations_service() -> PollinationsService:
    """Get or create PollinationsService instance"""
    global _pollinations_service
    if _pollinations_service is None:
        _pollinations_service = PollinationsService()
    return _pollinations_service