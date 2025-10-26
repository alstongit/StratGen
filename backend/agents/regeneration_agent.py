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
    except Exception:
        pass

REGENERATION_SYSTEM_PROMPT = """You are a campaign modification planner. You analyze user requests and produce structured action plans.

You receive:
- user_prompt: natural language request (may be vague, e.g., "change day 1", "find influencers in mumbai", "shorten prelaunch")
- final_draft: campaign strategy JSON
- canvas_data: current posts (with copy/image content), influencers, execution plan

Your task:
1. Parse user intent - identify which assets to modify and what changes to make
2. Resolve vague references using canvas_data:
   - "day with long caption" → search canvas posts for longest caption, return day_number
   - "prelaunch phase" → match to plan.phases[0] or plan.pre_launch
   - "the fitness post" → search posts for fitness keywords
3. For each modification, generate a CLEAR standalone instruction for the target agent:
   - Content agent: "Make caption more casual, under 100 chars, keep emojis"
   - Image agent: "Change to cityscape theme, vibrant colors, modern style"
   - Influencer agent: "Find fitness influencers in Mumbai with 10K-100K followers"
   - Plan agent: "Reduce pre-launch phase to 3 days, remove low-priority checklist items"
-4. Include previous_content when modifying existing assets so agents can compare/diff
+4. Include previous_content when modifying existing assets so agents can compare/diff. If creating new assets, set context.previous_content to null.

Return ONLY valid JSON with this exact structure:
{
  "needs_clarification": false,
  "clarify_message": null,
  "actions": [
    {
      "agent": "content_agent" | "image_agent" | "influencer_agent" | "plan_agent",
      "operation": "regenerate" | "modify_fields",
      "target": {
        "asset_id": "uuid-or-null",
        "day_number": 1,
        "plan_section": "pre_launch" | "checklist" | null
      },
      "instruction": "Clear standalone instruction for the agent",
+     "context": {
+       "previous_content": {...} | null,
+       "fields_to_modify": ["caption", "hashtags"] | null
+     }
    }
  ]
}

Rules:
- **ALWAYS include "context" field in every action, even if null.**
- If user request is ambiguous and you cannot resolve it using canvas_data, set needs_clarification: true
- Keep instructions clear, specific, actionable - the agent won't see the original user prompt
- For multi-change requests, create multiple actions with distinct instructions
- Always include previous_content when modifying existing assets (copy/image/plan)
- For new influencer searches or new plan creation, set context.previous_content to null
"""

class RegenerationAgent:
    """Agent responsible for analyzing modification requests and creating execution plans."""
    
    def __init__(self):
        """Initialize Agno AI regeneration agent."""
        try:
            self.agent = Agent(
                model=Gemini(id="gemini-2.0-flash-lite"),
                instructions=REGENERATION_SYSTEM_PROMPT,
                markdown=False,
                structured_outputs=True
            )
            print("✅ RegenerationAgent initialized")
        except Exception as e:
            print(f"❌ Failed to initialize RegenerationAgent: {e}")
            raise
    
    async def analyze_modification(
        self,
        user_prompt: str,
        final_draft: Dict[str, Any],
        canvas_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user modification request and create structured action plan.
        
        Args:
            user_prompt: Raw user message (e.g., "change image of day 1 and find influencers in mumbai")
            final_draft: Campaign strategy JSON
            canvas_data: Complete canvas state (posts, influencers, plan with full content)
            
        Returns:
            Dict with needs_clarification or actions[] array
        """
        try:
            print(f"🔍 Analyzing modification request...")
            print(f"   User prompt: {user_prompt[:100]}...")
            
            # Build context summary for the LLM
            context_summary = self._build_context_summary(canvas_data)
            
            # Build prompt
            prompt = f"""Analyze this modification request and create an action plan.

USER REQUEST:
"{user_prompt}"

CAMPAIGN STRATEGY:
{json.dumps(final_draft, indent=2)[:2000]}...

CURRENT CANVAS STATE:
{context_summary}

Return ONLY the JSON action plan."""

            # Generate response
            response = self.agent.run(prompt, stream=False)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📥 Raw response: {response_text[:200]}...")
            
            # Parse JSON
            plan = self._parse_json_response(response_text)
            
            # Validate structure
            if not self._validate_plan(plan):
                print("⚠️ Invalid plan structure, requesting clarification")
                return {
                    "needs_clarification": True,
                    "clarify_message": "I couldn't understand your request. Please be more specific about what you'd like to change.",
                    "actions": []
                }
            
            action_count = len(plan.get("actions", []))
            print(f"✅ Modification plan created: {action_count} action(s)")
            
            # Log actions for debugging
            for i, action in enumerate(plan.get("actions", []), 1):
                agent = action.get("agent", "unknown")
                target = action.get("target", {})
                day = target.get("day_number")
                instruction = action.get("instruction", "")[:60]
                print(f"   {i}. {agent} (day {day}): {instruction}...")
            
            return plan
        
        except Exception as e:
            print(f"❌ Error analyzing modification: {e}")
            import traceback
            traceback.print_exc()
            # Return fallback - request clarification
            return {
                "needs_clarification": True,
                "clarify_message": f"I encountered an error processing your request. Please try rephrasing it.",
                "actions": []
            }
    
    def _build_context_summary(self, canvas_data: Dict[str, Any]) -> str:
        """Build a concise summary of canvas state for LLM context."""
        try:
            posts = canvas_data.get("posts", [])
            influencers = canvas_data.get("influencers", [])
            plan = canvas_data.get("plan", {})
            
            summary_parts = []
            
            # Posts summary
            summary_parts.append(f"POSTS ({len(posts)} days):")
            for post in posts[:10]:  # Limit to first 10 for token efficiency
                day = post.get("day_number", "?")
                copy_data = post.get("copy", {}).get("content", {})
                image_data = post.get("image", {}).get("content", {})
                
                caption = copy_data.get("caption", "")[:80]
                image_prompt = image_data.get("prompt", "N/A")[:60]
                
                summary_parts.append(f"  Day {day}:")
                summary_parts.append(f"    Caption: {caption}...")
                summary_parts.append(f"    Image: {image_prompt}...")
            
            # Influencers summary
            summary_parts.append(f"\nINFLUENCERS ({len(influencers)} total):")
            for inf in influencers[:5]:
                content = inf.get("content", {})
                name = content.get("name", "Unknown")
                platform = content.get("platform", "?")
                summary_parts.append(f"  - {name} ({platform})")
            
            # Plan summary
            if plan:
                plan_content = plan.get("content", {})
                phases = plan_content.get("phases", [])
                checklist = plan_content.get("checklist", [])
                
                summary_parts.append(f"\nEXECUTION PLAN:")
                summary_parts.append(f"  Phases: {len(phases)}")
                for phase in phases:
                    name = phase.get("name", "?")
                    duration = phase.get("duration", "?")
                    summary_parts.append(f"    - {name} ({duration})")
                
                summary_parts.append(f"  Checklist: {len(checklist)} items")
            
            return "\n".join(summary_parts)
        
        except Exception as e:
            print(f"⚠️ Error building context summary: {e}")
            return "Canvas data available but error summarizing"
    
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
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate plan structure."""
        if not isinstance(plan, dict):
            return False
        
        # Must have needs_clarification
        if "needs_clarification" not in plan:
            return False
        
        # If clarification needed, must have message
        if plan["needs_clarification"] and not plan.get("clarify_message"):
            return False
        
        # If no clarification, must have actions
        if not plan["needs_clarification"]:
            actions = plan.get("actions", [])
            if not isinstance(actions, list) or len(actions) == 0:
                return False
            
            # Validate each action
            for action in actions:
                required_fields = ["agent", "operation", "target", "instruction"]
                if not all(field in action for field in required_fields):
                    return False
        
        return True

# Global instance
_regeneration_agent = None

def get_regeneration_agent() -> RegenerationAgent:
    """Get or create RegenerationAgent instance."""
    global _regeneration_agent
    if _regeneration_agent is None:
        _regeneration_agent = RegenerationAgent()
    return _regeneration_agent