from typing import Dict, Any, List, Optional
from services.serper_service import get_serper_service
from utils.gemini_client import gemini_client
import json
import asyncio

class InfluencerAgent:
    """
    Agent responsible for finding relevant influencers.
    Uses Gemini (Agno) to generate search prompts based on the campaign draft,
    then runs those prompts through Serper to collect and score results.
    """
    
    def __init__(self):
        self.serper = get_serper_service()
        print("✅ InfluencerAgent initialized")
    
    async def find_influencers(
        self,
        campaign_draft: Dict[str, Any],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find relevant influencers/organizations/partners for the campaign.
        Workflow:
         - Ask Gemini to generate 2-3 targeted search prompts based on campaign_draft
         - Run those prompts against Serper concurrently
         - Aggregate, dedupe and return top `count` influencer objects
        """
        try:
            print(f"\n🔍 Finding {count} influencers using AI-generated prompts...")

            # Prepare concise context for Gemini
            title = campaign_draft.get("title", "")
            niche = campaign_draft.get("target_audience", "")
            platforms = campaign_draft.get("platforms", ["instagram"])
            content_themes = campaign_draft.get("content_themes", [])
            follower_pref = campaign_draft.get("influencer_preference", "")  # optional guidance

            primary_platform = platforms[0] if platforms else "instagram"

            gemini_prompt = f"""
You are a research assistant. Given the campaign draft context below, generate 2 to 3 concise search prompts (single-line each) that will surface:
- top influencers on {primary_platform} (and other relevant social platforms)
- relevant organizations, NGOs, companies, or partner brands
Prompts should be short search queries suitable to paste into a search API (Serper). They should implicitly respect follower/prestige preference if provided.

Campaign title: {title}
Niche / Target audience: {niche}
Content themes: {', '.join(content_themes) if content_themes else 'none'}
Influencer preference (followers / scale / type): {follower_pref}

Return the prompts only, as either a JSON array of strings or plain newline-separated lines. Do not add explanations.
""".strip()

            # Generate prompts via Gemini (may return JSON array or newline list)
            try:
                gen_response = gemini_client.generate_content(gemini_prompt)
                gen_text = getattr(gen_response, "text", None) or str(gen_response)
                gen_text = gen_text.strip()
                print(f"🧠 Gemini returned: {gen_text[:200]}...")
            except Exception as e:
                print(f"⚠️ Gemini prompt generation failed: {e}")
                gen_text = ""

            # Parse generated prompts (tolerant)
            prompts: List[str] = []
            if gen_text:
                # Try JSON first
                try:
                    parsed = json.loads(gen_text)
                    if isinstance(parsed, list):
                        prompts = [p.strip() for p in parsed if isinstance(p, str) and p.strip()]
                except Exception:
                    # Fallback: split lines, remove bullets/quotes
                    lines = [l.strip().lstrip("-•* ").strip('"').strip("'") for l in gen_text.splitlines()]
                    prompts = [l for l in lines if l]

            # If Gemini failed or returned nothing, fallback to sensible defaults
            if not prompts:
                print("ℹ️ Using fallback prompt templates")
                base = title or niche or "local audience"
                loc = campaign_draft.get("location", "")
                loc_part = f" in {loc}" if loc else ""
                prompts = [
                    f"Top {primary_platform} influencers for {base}{loc_part}",
                    f"Organizations and NGOs that partner with brands in {base}{loc_part}",
                    f"Companies and agencies that work with influencers in {base}{loc_part}"
                ]

            print(f"🔎 Running {len(prompts)} search prompts against Serper:")
            for i, p in enumerate(prompts, 1):
                print(f"  {i}. {p}")

            # Use serper_service.search_influencers which handles concurrent searches, parsing & dedupe
            influencers = await self.serper.search_influencers(
                niche=niche or title,
                platform=primary_platform,
                location=campaign_draft.get("location"),
                count=count,
                prompts=prompts
            )

            print(f"✅ Serper (via prompts) returned {len(influencers)} influencer objects")
            # Ensure sorted by relevance_score
            influencers_sorted = sorted(influencers, key=lambda x: x.get("relevance_score", 0), reverse=True)

            return influencers_sorted[:count]
        
        except Exception as e:
            print(f"❌ Error finding influencers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _detect_platform(self, url: str) -> str:
        """Detect social media platform from URL"""
        url_lower = url.lower()
        
        if "instagram.com" in url_lower:
            return "Instagram"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "Twitter/X"
        elif "youtube.com" in url_lower:
            return "YouTube"
        elif "tiktok.com" in url_lower:
            return "TikTok"
        elif "linkedin.com" in url_lower:
            return "LinkedIn"
        else:
            return "Website"
    
    def _calculate_relevance(
        self,
        result: Dict[str, Any],
        campaign_draft: Dict[str, Any]
    ) -> float:
        """(kept for backward compatibility) Calculate relevance score (0-100)"""
        score = 50.0  # Base score
        
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        combined_text = title + " " + snippet
        
        # Check for title keywords
        campaign_title = campaign_draft.get("title", "").lower()
        title_words = campaign_title.split()[:3]
        
        for word in title_words:
            if word in combined_text:
                score += 10
        
        # Check for content themes
        content_themes = campaign_draft.get("content_themes", [])
        for theme in content_themes[:3]:
            if theme.lower() in combined_text:
                score += 8
        
        # Prefer verified social profiles
        link = result.get("link", "")
        if "instagram.com" in link or "twitter.com" in link or "youtube.com" in link:
            score += 15
        
        return min(score, 100)

# Global instance
_influencer_agent = None

def get_influencer_agent() -> InfluencerAgent:
    """Get or create InfluencerAgent instance"""
    global _influencer_agent
    if _influencer_agent is None:
        _influencer_agent = InfluencerAgent()
    return _influencer_agent