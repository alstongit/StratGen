from typing import Dict, Any
import uuid
from services.pollinations_service import get_pollinations_service
from utils.gemini_client import gemini_client

class ImageAgent:
    """
    Agent responsible for generating images for social media posts.
    Uses Gemini to create SHORT prompts and Pollinations.ai to generate images.
    """
    
    def __init__(self):
        self.pollinations = get_pollinations_service()
        print("✅ ImageAgent initialized")
    
    async def generate_image(
        self,
        campaign_id: str,
        campaign_draft: Dict[str, Any],
        copy_content: Dict[str, Any],
        day_number: int
    ) -> Dict[str, Any]:
        """
        Generate an image for a specific post.
        
        Args:
            campaign_id: UUID of the campaign
            campaign_draft: The campaign draft JSON
            copy_content: The copy content for this post
            day_number: Which day this is for
        
        Returns:
            Dict with image data including image_url
        """
        try:
            print(f"\n🎨 Generating image for Day {day_number}...")
            
            # Get post caption (NOT post_text - that field doesn't exist)
            caption = copy_content.get("caption", "")
            
            # Generate SHORT image prompt using Gemini
            image_prompt = await self._create_image_prompt(
                campaign_draft=campaign_draft,
                post_caption=caption,
                day_number=day_number
            )
            
            print(f"📝 Clean image prompt: {image_prompt}")
            
            # Generate image using Pollinations
            image_data = await self.pollinations.generate_image(
                prompt=image_prompt,
                width=1024,
                height=1024
            )
            
            print(f"✅ Pollinations URL: {image_data['image_url']}")
            print(f"💡 Using Pollinations URL directly (works in browser!)")
            
            return image_data
        
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _create_image_prompt(
        self,
        campaign_draft: Dict[str, Any],
        post_caption: str,
        day_number: int
    ) -> str:
        """Create a SHORT image generation prompt using Gemini"""
        try:
            title = campaign_draft.get("title", "campaign")
            color_scheme = campaign_draft.get("color_scheme", [])
            
            # Get first color
            primary_color = color_scheme[0] if color_scheme else "vibrant"
            
            prompt = f"""Create a VERY SHORT image prompt (max 60 characters) for this social media post.

Campaign: {title}
Post Caption: {post_caption[:150]}
Primary Color: {primary_color}

Requirements:
- Maximum 60 characters total
- Only describe the main visual subject
- Include style keyword (modern/vibrant/minimal)
- Include primary color
- NO text/words in image
- NO markdown formatting

Example: "modern tech workspace, blue tones, minimal"

Return ONLY the short prompt, nothing else."""

            response = gemini_client.generate_content(prompt)
            image_prompt = response.text.strip().strip('"').strip("'").strip('`')
            
            # Remove any markdown
            image_prompt = image_prompt.replace("**", "").replace("*", "")
            
            # Ensure it's REALLY short
            if len(image_prompt) > 80:
                words = image_prompt.split()[:8]
                image_prompt = " ".join(words)
            
            print(f"✅ Generated prompt ({len(image_prompt)} chars): {image_prompt}")
            
            return image_prompt
        
        except Exception as e:
            print(f"⚠️ Error creating image prompt, using fallback: {e}")
            title_short = campaign_draft.get("title", "campaign")[:30]
            return f"{title_short} modern vibrant"

# Global instance
_image_agent = None

def get_image_agent() -> ImageAgent:
    """Get or create ImageAgent instance"""
    global _image_agent
    if _image_agent is None:
        _image_agent = ImageAgent()
    return _image_agent