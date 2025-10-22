import httpx
from typing import List, Dict, Any, Optional
import json
import asyncio

class SerperService:
    """Service for interacting with Serper.dev Google Search API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        print("✅ SerperService initialized")
    
    async def search(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform a general search using Serper.dev
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
        
        Returns:
            List of search result dictionaries
        """
        try:
            print(f"🔍 Serper search query: {query}")
            
            payload = {
                "q": query
            }
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract organic results
            organic_results = data.get("organic", [])
            
            print(f"✅ Serper returned {len(organic_results)} organic results")
            
            # Log first few results for debugging
            for i, result in enumerate(organic_results[:3], 1):
                print(f"  {i}. {result.get('title', 'N/A')[:60]}...")
                print(f"     Link: {result.get('link', 'N/A')}")
            
            return organic_results[:num_results]
        
        except Exception as e:
            print(f"❌ Serper API error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def search_influencers(
        self,
        niche: str,
        platform: str = "instagram",
        location: Optional[str] = None,
        count: int = 10,
        prompts: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for influencers/orgs/companies using multiple Serper prompts.

        If `prompts` is provided, it will run each prompt. Otherwise uses 3
        smart templates to cover influencers, orgs/NGOs, and companies/partners.
        Results from all prompts are aggregated, deduplicated (by profile link),
        parsed, and top `count` returned.
        """
        try:
            # Build default prompts if none provided
            if prompts is None:
                base = niche or ""
                loc_part = f" in {location}" if location else ""
                prompts = [
                    f"Top {platform} influencers for {base}{loc_part} — influencers, creators, accounts",
                    f"Organizations, NGOs, companies that partner with brands in {base}{loc_part}",
                    f"Brands and agencies in {base}{loc_part} that work with influencers for promotions"
                ]

            print(f"🔍 Running {len(prompts)} search prompts for influencers")
            # Run searches concurrently (more results per prompt so we can filter)
            tasks = [self.search(query=p, num_results= min(10, count*2)) for p in prompts]
            all_results_lists = await asyncio.gather(*tasks, return_exceptions=True)

            # Flatten and filter exceptions
            raw_results = []
            for res in all_results_lists:
                if isinstance(res, Exception):
                    print(f"⚠️ One prompt search failed: {res}")
                    continue
                raw_results.extend(res or [])

            print(f"📊 Aggregated {len(raw_results)} raw results from prompts")

            # Deduplicate by link (profile URL)
            seen = set()
            unique_results = []
            for r in raw_results:
                link = (r.get("link") or "").split("?")[0].rstrip("/")
                if not link:
                    continue
                if link in seen:
                    continue
                seen.add(link)
                unique_results.append(r)

            print(f"✅ Deduped to {len(unique_results)} unique profile links")

            # Parse into influencer objects
            influencers = self._parse_search_results(unique_results, platform)

            # Sort by relevance_score (already provided by _parse_search_results) and return top count
            influencers_sorted = sorted(influencers, key=lambda x: x.get("relevance_score", 0), reverse=True)

            print(f"✅ Returning top {min(count, len(influencers_sorted))} influencers")
            return influencers_sorted[:count]

        except Exception as e:
            print(f"❌ Error searching influencers (multi-prompt): {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_search_results(
        self,
        results: List[Dict[str, Any]],
        platform: str
    ) -> List[Dict[str, Any]]:
        """Parse Serper.dev search results into influencer objects"""
        influencers = []
        
        for result in results:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            position = result.get("position", 10)
            
            # Skip if not a profile page
            if not self._is_profile_page(link, platform):
                continue
            
            # Extract handle from link
            handle = self._extract_handle(title, link, platform)
            
            # Extract name
            name = self._extract_name(title)
            
            # Extract follower count from snippet
            followers = self._extract_follower_count(snippet)
            
            influencer = {
                "name": name,
                "handle": handle or f"@{name.lower().replace(' ', '')}",
                "platform": platform.capitalize(),
                "followers": followers or "Unknown",
                "engagement_rate": None,
                "relevance_score": self._calculate_relevance(position),
                "profile_url": link,
                "bio": snippet[:200] if snippet else "",
                "why": self._generate_why_text(name, snippet)
            }
            
            influencers.append(influencer)
            print(f"  ✓ Parsed: {name} ({handle or 'no handle'}) - {followers or 'no follower count'}")
        
        return influencers
    
    def _extract_handle(self, title: str, link: str, platform: str) -> Optional[str]:
        """Extract social media handle from title or URL"""
        # Try to extract from title (e.g., "BYD Global (@byd_global)")
        if "(@" in title and ")" in title:
            start = title.index("(@") + 2
            end = title.index(")", start)
            return "@" + title[start:end]
        
        # Try to extract from URL
        if platform.lower() == "instagram" and "instagram.com/" in link:
            parts = link.split("instagram.com/")
            if len(parts) > 1:
                handle = parts[1].split("/")[0].split("?")[0]
                if handle and handle not in ["reel", "p", "tv", "stories"]:
                    return "@" + handle
        
        return None
    
    def _extract_follower_count(self, snippet: str) -> Optional[str]:
        """Extract follower count from snippet text"""
        import re
        
        # Pattern: "17K followers" or "2M followers"
        pattern = r'(\d+(?:\.\d+)?[KMBkmb]?)\s*followers'
        match = re.search(pattern, snippet, re.IGNORECASE)
        
        if match:
            count = match.group(1)
            # Normalize to uppercase
            return count.upper()
        
        return None
    
    def _extract_name(self, title: str) -> str:
        """Extract influencer name from title"""
        # Remove platform indicators and handle
        name = title.split("•")[0].split("-")[0].split("(")[0].split("|")[0]
        name = name.strip()
        return name if name else "Influencer"
    
    def _is_profile_page(self, link: str, platform: str) -> bool:
        """Check if the link is a profile page (not a post)"""
        if platform.lower() == "instagram":
            # Profile pages: instagram.com/username or instagram.com/username/?hl=en
            # NOT posts: instagram.com/p/, instagram.com/reel/, instagram.com/tv/
            if "instagram.com/" not in link:
                return False
            
            # Exclude posts/reels/tv
            excluded = ["/p/", "/reel/", "/tv/", "/stories/"]
            return not any(exc in link for exc in excluded)
        
        return True
    
    def _calculate_relevance(self, position: int) -> float:
        """Calculate relevance score based on search position"""
        if position <= 3:
            return 10.0 - (position - 1) * 0.5
        elif position <= 5:
            return 8.5 - (position - 4) * 0.5
        else:
            return max(6.0, 8.0 - (position - 5) * 0.3)
    
    def _generate_why_text(self, name: str, snippet: str) -> str:
        """Generate explanation for why this influencer is recommended"""
        snippet_lower = snippet.lower()
        
        if "followers" in snippet_lower:
            return f"{name} has a strong follower base and active engagement"
        elif "official" in snippet_lower or "verified" in snippet_lower:
            return f"{name} is an official/verified account with credibility"
        elif "innovation" in snippet_lower or "technology" in snippet_lower:
            return f"{name} focuses on innovation and tech, matching campaign themes"
        else:
            return f"{name} has relevant content and audience for this campaign"

# Global instance
_serper_service = None

def get_serper_service() -> SerperService:
    """Get or create SerperService instance"""
    global _serper_service
    if _serper_service is None:
        from config.settings import settings
        _serper_service = SerperService(api_key=settings.SERPER_API_KEY)
    return _serper_service