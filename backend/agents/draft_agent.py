from agno.agent import Agent
from agno.models.google import Gemini
from typing import Dict, Any, List, Optional
import json
import os

# Ensure GOOGLE_API_KEY is available
if not os.getenv("GOOGLE_API_KEY"):
    try:
        from config.settings import settings
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        print("✅ Loaded GOOGLE_API_KEY from settings")
    except Exception as e:
        print(f"❌ Could not load API key: {e}")

# System prompts
DRAFT_SYSTEM_PROMPT = """You are an expert marketing strategist and campaign planner.

Your role is to create comprehensive, actionable marketing campaign strategies.

When a user describes their campaign, you should:
1. Analyze their goals, target audience, and context
2. Generate a complete strategy with specific, actionable details
3. Be creative but realistic
4. Focus on social media marketing best practices
5. Provide concrete recommendations

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no markdown, just pure JSON.

Required JSON structure:
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
    "additional_details": "Strategic considerations and recommendations"
}

Be specific, detailed, and actionable in your recommendations."""

CONVERSATIONAL_PROMPT = """You are a friendly, expert marketing strategist having a conversation with a client.

Your communication style:
- Warm and professional
- Clear and concise (2-3 paragraphs max)
- Acknowledge user feedback
- Explain your strategic decisions
- Ask clarifying questions when needed
- Show enthusiasm for the campaign

DO NOT use JSON in your responses. Speak naturally like a consultant would."""

class DraftAgent:
    """Agent responsible for generating and refining campaign strategy drafts using Agno AI."""
    
    def __init__(self):
        """Initialize Agno AI agents."""
        try:
            # Create Gemini model instances
            strategy_model = Gemini(
                id="gemini-2.0-flash-lite",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            
            conversation_model = Gemini(
                id="gemini-2.0-flash-lite",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            
            # Strategy agent - generates JSON drafts
            self.strategy_agent = Agent(
                name="Strategy Draft Agent",
                model=strategy_model,
                instructions=DRAFT_SYSTEM_PROMPT,
                markdown=False,
                structured_outputs=True
            )
            
            # Conversation agent - natural language responses
            self.conversation_agent = Agent(
                name="Marketing Advisor",
                model=conversation_model,
                instructions=CONVERSATIONAL_PROMPT,
                markdown=True
            )
            
            print("✅ DraftAgent initialized with Agno AI")
        except Exception as e:
            print(f"❌ Failed to initialize Agno agents: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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
            print(f"🤖 Generating initial draft with Agno AI...")
            
            prompt = f"""Create a comprehensive marketing campaign strategy based on this brief:

USER BRIEF:
{initial_prompt}

Generate a complete strategy including:
- Clear, compelling campaign title
- Detailed target audience analysis
- Appropriate color scheme (3-5 colors that match the campaign theme and psychology)
- Relevant social media platforms for the target audience
- Multi-day posting schedule with specific times and content types
- Key content themes aligned with campaign goals
- Additional strategic recommendations

IMPORTANT: Return ONLY the JSON object. No explanations or markdown."""

            # Use Agno's run method
            response = self.strategy_agent.run(prompt, stream=False)
            
            # Get the response content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📥 Raw response: {response_text[:200]}...")
            
            # Parse the JSON response
            draft_json = self._parse_json_response(response_text)
            
            # Validate and fix required fields
            draft_json = self._validate_draft(draft_json)
            
            print(f"✅ Draft generated: {draft_json.get('title', 'N/A')}")
            
            return draft_json
        
        except Exception as e:
            print(f"❌ Error generating initial draft: {e}")
            import traceback
            traceback.print_exc()
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
            print(f"🔄 Refining draft based on feedback...")
            
            # Build context from recent conversation
            context = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history[-3:]  # Last 3 messages
            ])
            
            prompt = f"""Update this marketing campaign strategy based on user feedback.

CONVERSATION CONTEXT:
{context}

CURRENT DRAFT:
{json.dumps(current_draft, indent=2)}

USER'S FEEDBACK:
{user_message}

Instructions:
1. Carefully read the user's feedback
2. Update ONLY the parts they're asking to change
3. Keep everything else from the current draft
4. Ensure consistency across all fields
5. Maintain the same JSON structure

IMPORTANT: Return ONLY the complete updated JSON object. No explanations."""

            response = self.strategy_agent.run(prompt, stream=False)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📥 Refinement response: {response_text[:200]}...")
            
            # Parse the refined draft
            refined_draft = self._parse_json_response(response_text)
            
            # Merge with current draft (refined takes precedence)
            updated_draft = {**current_draft, **refined_draft}
            
            # Validate
            updated_draft = self._validate_draft(updated_draft)
            
            print(f"✅ Draft refined successfully")
            
            return updated_draft
        
        except Exception as e:
            print(f"❌ Error refining draft: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_conversational_response(
        self,
        draft: Optional[Dict[str, Any]],
        user_message: str,
        conversation_history: List[Dict[str, str]],
        campaign_id: str
    ) -> str:
        """
        Generate natural conversational response.
        
        Args:
            draft: The current/updated draft
            user_message: User's latest message
            conversation_history: Previous messages (for context)
            campaign_id: Campaign ID (used as session ID for Agno's memory)
        
        Returns:
            Natural language response
        """
        try:
            print(f"💬 Generating conversational response...")
            
            # Build context about the draft
            draft_summary = "No draft created yet"
            if draft:
                draft_summary = f"""
Draft Title: {draft.get('title', 'N/A')}
Platforms: {', '.join(draft.get('platforms', []))}
Target Audience: {draft.get('target_audience', 'N/A')[:150]}...
Posting Days: {len(draft.get('posting_schedule', {}))}
"""
            
            prompt = f"""The user just said: "{user_message}"

Current Campaign Status:
{draft_summary}

Your task:
1. Acknowledge what the user said
2. Explain the strategy you've created or updated
3. Highlight 2-3 key strategic decisions and why you made them
4. End with a question or call-to-action (e.g., "Would you like me to adjust anything?" or "Ready to proceed?")

Keep it conversational, friendly, and concise (2-3 short paragraphs)."""

            response = self.conversation_agent.run(prompt, stream=False, session_id=campaign_id)
            response_text = response.content if hasattr(response, 'content') else str(response)
            conversational_response = response_text.strip()
            
            print(f"✅ Response generated: {conversational_response[:100]}...")
            
            return conversational_response
        
        except Exception as e:
            print(f"❌ Error generating conversational response: {e}")
            # Fallback response
            return "Great! I've updated your campaign strategy based on your feedback. The strategy is looking solid. Would you like me to make any other changes, or are you ready to execute the campaign?"
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        try:
            # Clean up response
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            return json.loads(cleaned)
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from AI: {e}")
    
    def _validate_draft(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix draft structure."""
        required_fields = {
            "title": "Untitled Campaign",
            "target_audience": "General audience",
            "color_scheme": ["#4F46E5", "#7C3AED", "#EC4899"],
            "platforms": ["instagram"],
            "posting_schedule": {},
            "content_themes": [],
            "additional_details": ""
        }
        
        # Ensure all required fields exist
        for field, default in required_fields.items():
            if field not in draft or not draft[field]:
                draft[field] = default
        
        # Ensure color_scheme has at least 3 colors
        if len(draft.get("color_scheme", [])) < 3:
            draft["color_scheme"] = ["#4F46E5", "#7C3AED", "#EC4899"]
        
        # Ensure platforms is a list
        if not isinstance(draft.get("platforms"), list):
            draft["platforms"] = ["instagram"]
        
        return draft

# Global instance - Safe initialization
try:
    print("🔄 Creating DraftAgent instance...")
    draft_agent = DraftAgent()
except Exception as e:
    print(f"❌ Failed to create DraftAgent: {e}")
    import traceback
    traceback.print_exc()
    draft_agent = None
    raise