from typing import Dict, Any, List, Optional
from utils.gemini_client import generate_json, generate_text
import json

DRAFT_SYSTEM_PROMPT = """You are an expert marketing strategist and campaign planner. Your role is to create comprehensive, actionable marketing campaign strategies.

When a user describes their campaign, you should:
1. Analyze their goals, target audience, and context
2. Generate a complete strategy with specific, actionable details
3. Be creative but realistic
4. Focus on social media marketing best practices
5. Provide concrete recommendations

Always respond with a JSON object following this exact structure:
{
    "title": "Campaign Title",
    "target_audience": "Detailed description of target audience (demographics, psychographics, behaviors)",
    "color_scheme": ["#HEX1", "#HEX2", "#HEX3"],
    "platforms": ["instagram", "twitter", "facebook", "linkedin"],
    "posting_schedule": {
        "day_1": {
            "time": "10:00 AM",
            "content_type": "teaser"
        },
        "day_2": {
            "time": "3:00 PM",
            "content_type": "announcement"
        }
    },
    "content_themes": ["theme1", "theme2", "theme3"],
    "additional_details": "Any other important strategic considerations"
}

Be specific and detailed in your recommendations."""

class DraftAgent:
    """Agent responsible for generating and refining campaign strategy drafts."""
    
    def __init__(self):
        self.system_prompt = DRAFT_SYSTEM_PROMPT
    
    async def generate_initial_draft(
        self,
        initial_prompt: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate initial campaign strategy draft from user's brief.
        
        Args:
            initial_prompt: User's campaign description
            user_id: ID of the user creating the campaign
        
        Returns:
            Draft JSON object
        """
        try:
            prompt = f"""Create a comprehensive marketing campaign strategy based on this brief:

USER BRIEF:
{initial_prompt}

Generate a complete strategy including:
- Clear campaign title
- Detailed target audience analysis
- Appropriate color scheme (3-5 colors that match the campaign theme)
- Relevant social media platforms
- Multi-day posting schedule with specific times and content types
- Key content themes to focus on
- Additional strategic recommendations

Remember: Be specific, actionable, and creative. The strategy should be ready to execute."""

            draft_json = await generate_json(
                prompt=prompt,
                system_instruction=self.system_prompt,
                temperature=0.8,
                max_tokens=2048
            )
            
            # Validate required fields
            required_fields = ["title", "target_audience", "color_scheme", "platforms"]
            for field in required_fields:
                if field not in draft_json:
                    draft_json[field] = self._get_default_value(field)
            
            return draft_json
        
        except Exception as e:
            print(f"Error generating initial draft: {e}")
            raise
    
    async def refine_draft(
        self,
        current_draft: Dict[str, Any],
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Refine existing draft based on user feedback.
        
        Args:
            current_draft: Current draft JSON
            user_message: User's refinement request
            conversation_history: Previous messages for context
        
        Returns:
            Updated draft JSON object
        """
        try:
            # Build context from conversation history
            context = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages for context
            ])
            
            prompt = f"""You are refining a marketing campaign strategy based on user feedback.

CONVERSATION CONTEXT:
{context}

CURRENT DRAFT:
{json.dumps(current_draft, indent=2)}

USER'S FEEDBACK:
{user_message}

Generate an updated strategy that incorporates the user's feedback while maintaining consistency with the overall campaign goals. Keep all the same fields but update the relevant parts based on the feedback.

Return the complete updated draft as JSON."""

            refined_draft = await generate_json(
                prompt=prompt,
                system_instruction=self.system_prompt,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Merge with current draft to ensure no fields are lost
            updated_draft = {**current_draft, **refined_draft}
            
            return updated_draft
        
        except Exception as e:
            print(f"Error refining draft: {e}")
            raise
    
    async def generate_conversational_response(
        self,
        draft: Optional[Dict[str, Any]],
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a natural conversational response explaining the draft or changes.
        
        Args:
            draft: The current/updated draft
            user_message: User's latest message
            conversation_history: Previous messages for context
        
        Returns:
            Natural language response
        """
        try:
            context = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history[-5:]
            ])
            
            prompt = f"""You are a friendly marketing strategist having a conversation with a client about their campaign.

CONVERSATION SO FAR:
{context}

LATEST USER MESSAGE:
{user_message}

CURRENT DRAFT:
{json.dumps(draft, indent=2) if draft else "No draft yet"}

Generate a natural, conversational response that:
1. Acknowledges what the user said
2. Explains the strategy you've created or updated
3. Highlights key decisions and why you made them
4. Asks if they'd like any changes or if they're ready to proceed

Keep it friendly, professional, and concise (2-3 paragraphs max)."""

            # Use generate_text instead of generate_json for conversational responses
            response = await generate_text(
                prompt=prompt,
                system_instruction="You are a helpful marketing strategist. Respond in natural, conversational language. Do not use JSON formatting.",
                temperature=0.8,
                max_tokens=500
            )
            
            return response.strip()
        
        except Exception as e:
            print(f"Error generating conversational response: {e}")
            # Fallback response
            return "I've updated your campaign strategy based on your feedback. Let me know if you'd like any changes, or if you're ready to execute the campaign!"
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing required fields."""
        defaults = {
            "title": "Untitled Campaign",
            "target_audience": "General audience",
            "color_scheme": ["#4F46E5", "#7C3AED", "#EC4899"],
            "platforms": ["instagram"],
            "posting_schedule": {},
            "content_themes": [],
            "additional_details": ""
        }
        return defaults.get(field, "")

# Global instance
draft_agent = DraftAgent()