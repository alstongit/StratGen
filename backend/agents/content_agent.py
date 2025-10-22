from agno.agent import Agent
from agno.models.google import Gemini
from typing import Dict, Any, List
import json
import os

# Ensure GOOGLE_API_KEY is available
if not os.getenv("GOOGLE_API_KEY"):
    try:
        from config.settings import settings
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    except Exception as e:
        print(f"❌ Could not load API key: {e}")

CONTENT_SYSTEM_PROMPT = """You are an expert social media copywriter and content strategist.

Your role is to create engaging, platform-optimized social media posts that drive engagement and conversions.

When given a campaign strategy and day number, you will:
1. Create compelling captions that match the brand voice and target audience
2. Include relevant hashtags (5-10) that maximize reach
3. Add a clear call-to-action (CTA)
4. Write platform-specific copy (Instagram vs Twitter format)
5. Include emojis strategically for better engagement
6. Create a punchy headline/hook
7. Write a detailed description for context

CRITICAL: Respond with ONLY a valid JSON object. No explanations, no markdown.

Required JSON structure:
{
    "platform": "instagram",
    "caption": "Full post caption with emojis and line breaks",
    "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3"],
    "cta": "Clear call to action",
    "headline": "Attention-grabbing headline",
    "description": "Detailed post description/context"
}

Guidelines:
- Instagram: 125-150 characters for caption, use emojis, 5-10 hashtags
- Twitter: 200-280 characters, 2-3 hashtags
- Keep tone consistent with brand voice
- Focus on benefits, not features
- Create urgency when appropriate
- Be authentic and conversational
"""

class ContentAgent:
    """Agent responsible for generating social media post copy/captions."""
    
    def __init__(self):
        """Initialize Agno AI content agent."""
        try:
            self.agent = Agent(
                model=Gemini(id="gemini-2.0-flash-lite"),
                instructions=CONTENT_SYSTEM_PROMPT,
                markdown=False,
                structured_outputs=True
            )
            print("✅ ContentAgent initialized")
        except Exception as e:
            print(f"❌ Failed to initialize ContentAgent: {e}")
            raise
    
    async def generate_post_copy(
        self,
        campaign_draft: Dict[str, Any],
        day_number: int,
        day_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate social media post copy for a specific day.
        
        Args:
            campaign_draft: The final draft JSON with campaign strategy
            day_number: Which day this post is for (1, 2, 3, etc.)
            day_info: Day-specific info from posting_schedule (time, content_type)
            
        Returns:
            Copy content dict with caption, hashtags, CTA, etc.
        """
        try:
            print(f"📝 Generating copy for Day {day_number}...")
            
            # Extract campaign details
            title = campaign_draft.get("title", "Campaign")
            target_audience = campaign_draft.get("target_audience", "General audience")
            platforms = campaign_draft.get("platforms", ["instagram"])
            content_themes = campaign_draft.get("content_themes", [])
            additional_details = campaign_draft.get("additional_details", "")
            
            # Get primary platform
            primary_platform = platforms[0] if platforms else "instagram"
            
            # Get day-specific details
            content_type = day_info.get("content_type", "announcement")
            post_time = day_info.get("time", "12:00 PM")
            
            # Build prompt
            prompt = f"""Create a {primary_platform} post for Day {day_number} of this campaign:

CAMPAIGN: {title}

TARGET AUDIENCE:
{target_audience}

CONTENT THEMES:
{', '.join(content_themes)}

DAY {day_number} DETAILS:
- Content Type: {content_type}
- Scheduled Time: {post_time}

STRATEGY NOTES:
{additional_details}

Create engaging copy that:
1. Matches the content type ({content_type})
2. Resonates with the target audience
3. Aligns with content themes
4. Is optimized for {primary_platform}
5. Drives engagement and action

Return ONLY the JSON object with caption, hashtags, CTA, headline, and description."""

            # Generate response
            response = self.agent.run(prompt, stream=False)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📥 Raw response: {response_text[:150]}...")
            
            # Parse JSON
            copy_data = self._parse_json_response(response_text)
            
            # Add platform and validate
            copy_data["platform"] = primary_platform
            copy_data = self._validate_copy(copy_data, primary_platform)
            
            print(f"✅ Copy generated for Day {day_number}")
            print(f"   Caption: {copy_data['caption'][:80]}...")
            
            return copy_data
        
        except Exception as e:
            print(f"❌ Error generating copy for Day {day_number}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response."""
        try:
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response: {e}")
    
    def _validate_copy(self, copy_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate and fix copy structure."""
        # Ensure required fields
        required_fields = {
            "platform": platform,
            "caption": "Check out our latest campaign!",
            "hashtags": ["#Campaign", "#Marketing"],
            "cta": "Learn more!",
            "headline": "Exciting News",
            "description": "Campaign announcement"
        }
        
        for field, default in required_fields.items():
            if field not in copy_data or not copy_data[field]:
                copy_data[field] = default
        
        # Ensure hashtags is a list
        if not isinstance(copy_data.get("hashtags"), list):
            copy_data["hashtags"] = ["#Marketing"]
        
        # Ensure hashtags start with #
        copy_data["hashtags"] = [
            f"#{tag}" if not tag.startswith("#") else tag
            for tag in copy_data["hashtags"]
        ]
        
        return copy_data

# Global instance
_content_agent = None

def get_content_agent() -> ContentAgent:
    """Get or create ContentAgent instance."""
    global _content_agent
    if _content_agent is None:
        _content_agent = ContentAgent()
    return _content_agent