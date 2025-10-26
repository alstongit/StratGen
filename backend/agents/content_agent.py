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

Your role is to create platform-optimized social media posts.

CRITICAL: Respond with ONLY a valid JSON object. No explanations, no markdown.

Required JSON structure (only these fields):
{
    "platform": "instagram",
    "caption": "Full post caption with emojis and line breaks",
    "description": "Short description/context (optional longer form)",
    "hashtags": ["#Hashtag1", "#Hashtag2"]
}

Guidelines:
- Instagram caption length: ~125-150 chars recommended (but include full caption)
- Provide 3-10 relevant hashtags (as a JSON array). Ensure each hashtag starts with '#'.
- Do NOT include extra fields (headline, cta, etc.). If you must, ignore them — return only the fields above.
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
            prompt = f"""Create a {primary_platform} post for Day {day_number}.

Return ONLY a JSON object with these keys: caption, description, hashtags, platform.

CAMPAIGN: {title}
TARGET AUDIENCE: {target_audience}
THEMES: {', '.join(content_themes)}

DAY DETAILS:
- Content Type: {content_type}
- Time: {post_time}

Instruction: produce an engaging caption and a short description/context. Provide 3-10 hashtags as a JSON array. Do NOT return other keys (headline, cta, etc.). Return ONLY JSON.
"""

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
    
    async def regenerate_post_copy(
        self,
        campaign_draft: Dict[str, Any],
        day_number: int,
        old_content: Dict[str, Any],
        user_instruction: str,
        fields_to_modify: List[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate or modify copy for a specific day using the final draft, previous content,
        a short instruction, and optionally a list of specific fields to modify.
        If fields_to_modify is provided, instruct the model to only update those fields
        and preserve all others.
        """
        title = campaign_draft.get("title", "Campaign")
        platforms = campaign_draft.get("platforms", ["instagram"])
        primary_platform = platforms[0] if platforms else "instagram"
        content_themes = campaign_draft.get("content_themes", [])
        # Build a clear targeted prompt
        fields_note = ""
        if fields_to_modify and len(fields_to_modify) > 0:
            fields_note = f"ONLY modify these fields: {', '.join(fields_to_modify)}. Keep other fields unchanged."
        else:
            fields_note = "You may modify caption, description, and/or hashtags as needed."

        prompt = f"""Regenerate the {primary_platform} copy for Day {day_number}.
{fields_note}
Apply this instruction: "{user_instruction}"
Return ONLY the full JSON object with keys: caption, description, hashtags, platform.
PREVIOUS COPY:
{json.dumps(old_content)}
"""
        try:
            response = self.agent.run(prompt, stream=False)
            response_text = response.content if hasattr(response, 'content') else str(response)
            new_copy = self._parse_json_response(response_text)
            new_copy["platform"] = primary_platform
            # Ensure fields not in new_copy are preserved from old_content
            for k, v in (old_content or {}).items():
                if k not in new_copy:
                    new_copy[k] = v
            # validate
            return self._validate_copy(new_copy, primary_platform)
        except Exception as e:
            print(f"⚠️ Error regenerating copy, returning previous content: {e}")
            return old_content
    
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