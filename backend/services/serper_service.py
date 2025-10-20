import httpx
from typing import List, Dict, Any, Optional
import asyncio

class SerperService:
    """Service for interacting with Serper.dev Google Search API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        
    async def search_influencers(
        self,
        niche: str,
        platform: str = "instagram",
        location: Optional[str] = None,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for influencers using Serper.dev
        
        Args:
            niche: Campaign niche (e.g., "gaming", "counter strike")
            platform: Social media platform (default: instagram)
            location: Geographic location (e.g., "Mumbai, Maharashtra, India")
            count: Number of influencers to find (default: 10)
            
        Returns:
            List of influencer data dictionaries
        """
        try:
            # Build search query
            query = f"{niche} {platform} influencers accounts"
            if location:
                query += f" {location}"
            
            # Prepare request
            payload = {
                "q": query,
                "gl": "in",  # India
                "num": min(count, 10)  # Serper returns max 10 organic results
            }
            
            if location:
                payload["location"] = location
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            print(f"🔍 Searching Serper.dev for: {query}")
            
            # Make async request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse results
            influencers = self._parse_search_results(data, platform)
            
            print(f"✅ Found {len(influencers)} influencers")
            
            return influencers[:count]
        
        except Exception as e:
            print(f"❌ Error searching influencers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_search_results(
        self,
        data: Dict[str, Any],
        platform: str
    ) -> List[Dict[str, Any]]:
        """Parse Serper.dev search results into influencer objects"""
        influencers = []
        organic_results = data.get("organic", [])
        
        for result in organic_results:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            # Extract handle from title or link
            handle = self._extract_handle(title, link, platform)
            if not handle:
                continue
            
            # Extract follower count from snippet
            followers = self._extract_follower_count(snippet)
            
            # Extract name
            name = self._extract_name(title)
            
            # Skip if it's not a profile page
            if not self._is_profile_page(link, platform):
                continue
            
            influencer = {
                "name": name,
                "handle": handle,
                "platform": platform,
                "followers": followers,
                "engagement_rate": None,  # Not available from search
                "relevance_score": self._calculate_relevance(
                    result.get("position", 10)
                ),
                "profile_url": link,
                "bio": snippet[:200] if snippet else "",
                "why": self._generate_why_text(name, snippet)
            }
            
            influencers.append(influencer)
        
        return influencers
    
    def _extract_handle(self, title: str, link: str, platform: str) -> Optional[str]:
        """Extract social media handle from title or URL"""
        # Try to extract from title (e.g., "dona (@donacsgo)")
        if "(@" in title and ")" in title:
            start = title.index("(@") + 2
            end = title.index(")", start)
            return "@" + title[start:end]
        
        # Try to extract from URL
        if platform == "instagram" and "instagram.com/" in link:
            # Extract from URL like https://www.instagram.com/donacsgo/
            parts = link.split("instagram.com/")
            if len(parts) > 1:
                handle = parts[1].split("/")[0].split("?")[0]
                return "@" + handle
        
        return None
    
    def _extract_follower_count(self, snippet: str) -> Optional[str]:
        """Extract follower count from snippet text"""
        # Look for patterns like "56K followers" or "2M followers"
        import re
        
        # Pattern: number + K/M + "followers"
        pattern = r'(\d+(?:\.\d+)?[KMkm])\s*followers'
        match = re.search(pattern, snippet)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_name(self, title: str) -> str:
        """Extract influencer name from title"""
        # Remove platform indicators and handle
        name = title.split("•")[0].split("-")[0].split("(")[0]
        name = name.strip()
        return name if name else "Unknown"
    
    def _is_profile_page(self, link: str, platform: str) -> bool:
        """Check if the link is a profile page"""
        if platform == "instagram":
            return "instagram.com/" in link and "/p/" not in link and "/reel/" not in link
        elif platform == "twitter":
            return "twitter.com/" in link or "x.com/" in link
        elif platform == "youtube":
            return "youtube.com/" in link
        
        return True  # Default to true for other platforms
    
    def _calculate_relevance(self, position: int) -> float:
        """Calculate relevance score based on search position"""
        # Top 3 results get 9-10 score, decreasing for lower positions
        if position <= 3:
            return 10.0 - (position - 1) * 0.5
        elif position <= 5:
            return 8.5 - (position - 4) * 0.5
        else:
            return max(6.0, 8.0 - (position - 5) * 0.3)
    
    def _generate_why_text(self, name: str, snippet: str) -> str:
        """Generate explanation for why this influencer is recommended"""
        # Extract key phrases from snippet
        if "professional" in snippet.lower():
            return f"{name} is a professional in the field with strong community presence"
        elif "content creator" in snippet.lower():
            return f"{name} is an active content creator with engaged audience"
        elif "streamer" in snippet.lower():
            return f"{name} is a popular streamer with live audience engagement"
        else:
            return f"{name} has relevant audience and strong social media presence"

# Create global instance (will be initialized with API key from settings)
_serper_service = None

def get_serper_service() -> SerperService:
    """Get or create SerperService instance"""
    global _serper_service
    if _serper_service is None:
        from config.settings import settings
        _serper_service = SerperService(api_key=settings.SERPER_API_KEY)
    return _serper_service