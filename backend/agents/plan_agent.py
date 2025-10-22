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

PLAN_SYSTEM_PROMPT = """You are an expert campaign manager and execution strategist.

Your role is to create detailed, actionable execution plans for marketing campaigns.

When given a campaign strategy and generated assets, you will:
1. Break down the campaign into clear phases (Pre-Launch, Launch, Post-Launch)
2. Create specific action items for each phase
3. Build a realistic timeline
4. Generate a comprehensive checklist
5. Provide strategic recommendations

CRITICAL: Respond with ONLY a valid JSON object. No explanations, no markdown.

Required JSON structure:
{
    "phases": [
        {
            "name": "Phase Name",
            "duration": "Timeline",
            "steps": ["Step 1", "Step 2", "Step 3"]
        }
    ],
    "timeline": "Overall campaign timeline description",
    "checklist": [
        {"task": "Task description", "completed": false, "priority": "high/medium/low"}
    ],
    "key_milestones": ["Milestone 1", "Milestone 2"],
    "success_metrics": ["Metric 1", "Metric 2"],
    "recommendations": "Strategic recommendations and tips"
}

Be specific, actionable, and realistic."""

class PlanAgent:
    """Agent responsible for creating campaign execution plans."""
    
    def __init__(self):
        """Initialize Agno AI plan agent."""
        try:
            self.agent = Agent(
                model=Gemini(id="gemini-2.0-flash-lite"),
                instructions=PLAN_SYSTEM_PROMPT,
                markdown=False,
                structured_outputs=True
            )
            print("✅ PlanAgent initialized")
        except Exception as e:
            print(f"❌ Failed to initialize PlanAgent: {e}")
            raise
    
    async def create_execution_plan(
        self,
        campaign_draft: Dict[str, Any],
        generated_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create comprehensive execution plan.
        
        Args:
            campaign_draft: Full campaign strategy
            generated_assets: List of all generated assets (copy, images)
            
        Returns:
            Execution plan with phases, checklist, timeline
        """
        try:
            print(f"📋 Creating execution plan...")
            
            # Extract campaign details
            title = campaign_draft.get("title", "Campaign")
            target_audience = campaign_draft.get("target_audience", "")
            platforms = campaign_draft.get("platforms", [])
            posting_schedule = campaign_draft.get("posting_schedule", {})
            content_themes = campaign_draft.get("content_themes", [])
            additional_details = campaign_draft.get("additional_details", "")
            
            # Count assets
            num_days = len(posting_schedule)
            num_posts = len([a for a in generated_assets if a.get("asset_type") == "copy"])
            num_images = len([a for a in generated_assets if a.get("asset_type") == "image"])
            
            # Build prompt
            prompt = f"""Create a detailed execution plan for this campaign:

CAMPAIGN: {title}

TARGET AUDIENCE: {target_audience}

PLATFORMS: {', '.join(platforms)}

CAMPAIGN DURATION: {num_days} days

CONTENT SCHEDULE:
{json.dumps(posting_schedule, indent=2)}

CONTENT THEMES: {', '.join(content_themes)}

GENERATED ASSETS:
- {num_posts} social media posts
- {num_images} images
- Influencer list ready

STRATEGY NOTES:
{additional_details}

Create a comprehensive execution plan that includes:
1. Pre-Launch phase (preparation tasks)
2. Launch phase (campaign execution)
3. Post-Launch phase (follow-up and analysis)
4. Detailed checklist with priorities
5. Key milestones to track
6. Success metrics to measure
7. Strategic recommendations

Return ONLY the JSON object."""

            # Generate response
            response = self.agent.run(prompt, stream=False)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📥 Raw response: {response_text[:150]}...")
            
            # Parse JSON
            plan_data = self._parse_json_response(response_text)
            
            # Validate and enhance
            plan_data = self._validate_plan(plan_data)
            
            print(f"✅ Execution plan created")
            print(f"   Phases: {len(plan_data.get('phases', []))}")
            print(f"   Checklist items: {len(plan_data.get('checklist', []))}")
            
            return plan_data
        
        except Exception as e:
            print(f"❌ Error creating execution plan: {e}")
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
    
    def _validate_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix plan structure."""
        # Ensure required fields
        if "phases" not in plan_data or not plan_data["phases"]:
            plan_data["phases"] = [
                {
                    "name": "Pre-Launch",
                    "duration": "1 week before",
                    "steps": ["Prepare assets", "Contact influencers", "Schedule posts"]
                },
                {
                    "name": "Launch",
                    "duration": "Campaign duration",
                    "steps": ["Publish content", "Monitor engagement", "Respond to comments"]
                },
                {
                    "name": "Post-Launch",
                    "duration": "1 week after",
                    "steps": ["Analyze results", "Thank participants", "Document learnings"]
                }
            ]
        
        if "checklist" not in plan_data or not plan_data["checklist"]:
            plan_data["checklist"] = [
                {"task": "Finalize all content", "completed": False, "priority": "high"},
                {"task": "Schedule posts", "completed": False, "priority": "high"},
                {"task": "Contact influencers", "completed": False, "priority": "medium"}
            ]
        
        if "timeline" not in plan_data:
            plan_data["timeline"] = "Multi-phase campaign execution"
        
        if "key_milestones" not in plan_data:
            plan_data["key_milestones"] = ["Campaign launch", "Mid-campaign review", "Campaign completion"]
        
        if "success_metrics" not in plan_data:
            plan_data["success_metrics"] = ["Engagement rate", "Reach", "Conversions"]
        
        if "recommendations" not in plan_data:
            plan_data["recommendations"] = "Monitor performance daily and adjust strategy as needed."
        
        return plan_data

# Global instance
_plan_agent = None

def get_plan_agent() -> PlanAgent:
    """Get or create PlanAgent instance."""
    global _plan_agent
    if _plan_agent is None:
        _plan_agent = PlanAgent()
    return _plan_agent