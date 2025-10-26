from typing import Dict, Any, List, Optional
from services.serper_service import get_serper_service
from utils.gemini_client import generate_text
import json
import asyncio
import re
import html

try:
    # Agno agent for integrated search+scrape if agno available in env
    from agno.agent import Agent as AgnoAgent
    from agno.models.google import Gemini as AgnoGemini
    AGNO_AVAILABLE = True
except Exception:
    AGNO_AVAILABLE = False

class InfluencerAgent:
    """
    Agent responsible for finding relevant influencers.
    Uses Gemini to generate Serper-ready search prompts, then runs those prompts
    through Serper, parses and returns cleaned influencer objects.
    """

    # Prompt to generate search queries oriented to profile pages
    SYSTEM_PROMPT = """
You are a research assistant. Produce 2 or 3 concise search queries (single-line)
optimized for a Google-style search API (serper.dev). Each query must be short,
clear English, and specially crafted to surface influencer PROFILE PAGES
(not individual posts or listicles). Prefer using site: filters and short
phrases like "profile", "official", "(@handle)". Return ONLY a JSON array of
strings, no explanation.

Examples:
- ["site:instagram.com \"yoga\" \"influencer\" profile", "site:instagram.com \"yoga instructor\" profile", "site:instagram.com \"yoga\" \"wellness\" profile"]
- ["site:youtube.com \"fitness influencer\" channel", "site:instagram.com \"fitness\" \"influencer\" profile"]

Constraints:
- Keep queries <= 120 chars.
- Focus on profile pages (use 'profile', 'official', '(@handle)', or site:domain).
- If primary platform is provided, prefer its domain (instagram -> site:instagram.com, tiktok -> tiktok.com/@, youtube -> youtube.com/@)
"""

    # Prompt to convert raw search results into cleaned influencer objects
    PARSE_PROMPT = """
You are given a list of raw search results from a Google-style search API.
Each result has 'title', 'link', 'snippet'. Return a JSON array of influencer
objects with fields:
- name: string
- profile_url: string
- handle: string|null (if can be inferred)
- platform: string (instagram/tiktok/youtube/other)
- followers: string|null (if detectable)
- bio: short text (<=300 chars)
- reason: short explanation why relevant (1-2 sentences)
Return ONLY valid JSON. If you cannot extract a field, use null.
"""

    def __init__(self):
        self.serper = get_serper_service()
        # optionally create an Agno agent which has built-in search/url_context features
        self.search_agent = None
        if AGNO_AVAILABLE:
            try:
                self.search_agent = AgnoAgent(
                    # Use Gemini 2.0 Flash Lite + enable web search
                    model=AgnoGemini(id="gemini-2.0-flash-lite", search=True),
                    instructions="You are an assistant that searches the web for influencer profile pages and returns structured JSON."
                )
                print("✅ InfluencerAgent initialized with Agno search-agent")
            except Exception as e:
                print("⚠️ Agno agent init failed, falling back to Serper:", e)
        else:
            print("✅ InfluencerAgent initialized (Agno not available, using Serper fallback)")

    def _make_platform_domain(self, platform: str) -> str:
        p = (platform or "instagram").lower()
        if "instagram" in p:
            return "site:instagram.com"
        if "tiktok" in p:
            return "site:tiktok.com"
        if "youtube" in p:
            return "site:youtube.com"
        if "twitter" in p or "x " in p:
            return "site:twitter.com"
        return "site:instagram.com"

    # new: lightweight stopword-based keyword extractor
    _STOPWORDS = {
        "find","me","show","get","in","from","for","the","a","an","of","and","to","please","i","we","us","on","with",
        "search","searching","looking","list","top","nearest","near","nearby"
    }

    def _keywords_from_instruction(self, instr: Optional[str]) -> str:
        if not instr:
            return ""
        toks = re.findall(r"\w+", instr.lower())
        toks = [t for t in toks if t not in self._STOPWORDS and len(t) > 2]
        # prefer location tokens last if present (keeps queries short)
        return " ".join(toks[:6])

    def _to_plain_query(self, q: str, location: Optional[str] = None) -> str:
        """Normalize a LLM/Google-style query into plain English keywords.
        Examples:
         - 'site:instagram.com "fitness" "mumbai" "influencer" profile' -> 'fitness influencers mumbai'
         - 'site:tiktok.com/@john profile' -> 'john tiktok'
        """
        if not q:
            return ""
        s = q.lower()
        # remove site: tokens and common search-only tokens
        s = re.sub(r"site:\S+", " ", s)
        s = s.replace("profile", " ").replace("official", " ").replace("(@)", " ").replace("(@", " ").replace(")", " ").replace("(", " ")
        # remove extra quotes and punctuation used for search
        s = s.replace('"', " ").replace("'", " ").replace("—", " ").replace("-", " ")
        # collapse multiple spaces, keep words longer than 1 char
        toks = [t for t in re.findall(r"\w+", s) if len(t) > 1 and t not in self._STOPWORDS]
        if location and location.lower() not in toks:
            toks.append(location.lower())
        # prefer explicit 'influencer' or 'influencers' if present in original query or user intent
        if "influencer" not in toks and "influencers" not in toks:
            toks.append("influencers")
        return " ".join(toks).strip()

    # modify fallback builder to prefer cleaned instruction
    def _fallback_build_prompts(self, title: str, niche: str, primary_platform: str, location: Optional[str], user_instruction: Optional[str] = None) -> List[str]:
        # Build plain-English fallback prompts (natural language)
        raw = (user_instruction or title or niche or "local creators").strip()
        keywords = self._keywords_from_instruction(raw)
        if location and location.lower() not in (keywords or ""):
            keywords = (keywords + " " + location).strip() if keywords else location
        if not keywords:
            keywords = title or niche or "local creators"
        base = keywords.strip()
        # Return a few plain English queries the UI / agent can use
        return [
            f"{base} influencers",
            f"{base} creators {location or ''}".strip(),
            f"{base} fitness influencers" if "fitness" not in base else f"{base}"
        ]

    async def _run_search_prompts(self, prompts: List[str], count: int) -> List[Dict[str, Any]]:
        # Run Serper.search for each prompt concurrently and aggregate raw organic results
        tasks = [self.serper.search(query=p, num_results=min(10, count * 2)) for p in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        raw = []
        for r in results:
            if isinstance(r, Exception):
                print(f"⚠️ One Serper prompt failed: {r}")
                continue
            raw.extend(r or [])
        return raw

    async def _parse_with_gemini(self, raw_results: List[Dict[str, Any]], platform_hint: str, user_instruction: Optional[str] = None) -> List[Dict[str, Any]]:
        # Build concise JSON payload string of top N results for Gemini
        sample = []
        for r in raw_results[:25]:
            sample.append({
                "title": html.unescape(r.get("title", "")),
                "link": r.get("link", ""),
                "snippet": html.unescape(r.get("snippet", "") or "")
            })
        payload = json.dumps(sample, ensure_ascii=False)
        extra = f"\nUser request: {user_instruction}" if user_instruction else ""
        prompt = f"{self.PARSE_PROMPT}\n\nPlatform hint: {platform_hint}{extra}\n\nRawResults:\n{payload}\n\nReturn JSON array of influencer objects."
        try:
            gen_text = await generate_text(prompt, temperature=0.0, max_tokens=800)
            # log raw LLM output for debugging (helps diagnose parse errors)
            print("🔎 Gemini post-process raw output:", repr(gen_text)[:2000])
            # Strip markdown fences before parsing
            cleaned = gen_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            if isinstance(parsed, list):
                return parsed
        except Exception as e:
            print(f"⚠️ Gemini post-process failed: {e}")
            import traceback
            traceback.print_exc()
            # continue to fallback
        return []

    # Local, tolerant parser fallback (if Gemini fails)
    def _simple_parse_results(self, raw_results: List[Dict[str, Any]], primary_platform: str) -> List[Dict[str, Any]]:
        parsed = []
        seen = set()
        for r in raw_results:
            link = (r.get("link") or "").split("?")[0].rstrip("/")
            if not link or link in seen:
                continue
            seen.add(link)
            title = r.get("title") or ""
            snippet = r.get("snippet") or ""
            # simple handle extraction
            handle = None
            if "instagram.com/" in link:
                parts = link.split("instagram.com/")[1].split("/")
                if parts:
                    h = parts[0]
                    if h and h not in ["p", "reel", "tv", "stories"]:
                        handle = "@" + h
            name = title.split("•")[0].split("-")[0].split("(")[0].strip() or "Influencer"
            followers = None
            m = re.search(r'(\d+(?:\.\d+)?[KMBkmb]?)\s*followers', snippet, re.I)
            if m:
                followers = m.group(1).upper()
            parsed.append({
                "name": name,
                "profile_url": link,
                "handle": handle,
                "platform": primary_platform.capitalize(),
                "followers": followers or None,
                "bio": snippet[:300],
                "reason": f"Matched by search result: {title[:120]}"
            })
        return parsed

    async def find_influencers(
        self,
        campaign_draft: Dict[str, Any],
        count: int = 10,
        user_instruction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            # enforce a hard cap of 10 influencer accounts
            count = max(1, int(count or 10))
            if count > 10:
                count = 10

            title = campaign_draft.get("title", "")
            niche = campaign_draft.get("target_audience", "") or campaign_draft.get("niche", "")
            platforms = campaign_draft.get("platforms", ["instagram"])
            primary_platform = platforms[0] if platforms else "instagram"
            follower_pref = campaign_draft.get("influencer_preference", "")
            location = campaign_draft.get("location")

            # Build a short context we will give to the searcher LLM/agent
            user_ctx = {
                "campaign_title": title,
                "niche": niche,
                "platform": primary_platform,
                "location": location,
                "preference": follower_pref,
                "user_request": user_instruction
            }

            # If Agno's integrated search agent is available, ask it directly to find structured influencer profiles
            if self.search_agent:
                try:
                    agno_prompt = (
                        f"Find up to {count} influencer PROFILE pages relevant to this campaign. "
                        f"Return ONLY a JSON array of objects each with: {{name, profile_url, handle, platform, followers, bio, reason}}.\n\n"
                        f"Context: {json.dumps(user_ctx, ensure_ascii=False)}\n\nReturn JSON only."
                    )
                    # log prompt for debugging
                    print("🔎 Agno search-agent prompt:", agno_prompt)

                    # Use keyword argument for stream (Agno changed signature)
                    resp = await asyncio.to_thread(self.search_agent.run, agno_prompt, stream=False)
                    raw = getattr(resp, "content", None) or getattr(resp, "text", None) or str(resp)
                    print("🔎 Agno search-agent raw output:", repr(raw)[:2000])

                    # try parse JSON (tolerant)
                    parsed = None
                    try:
                        parsed = json.loads(raw.strip())
                    except Exception:
                        # strip common code fences and retry
                        txt = raw.strip()
                        if txt.startswith("```json"):
                            txt = txt[7:]
                        if txt.startswith("```"):
                            txt = txt[3:]
                        if txt.endswith("```"):
                            txt = txt[:-3]
                        try:
                            parsed = json.loads(txt.strip())
                        except Exception:
                            pass

                    if isinstance(parsed, list):
                        return parsed[:count]
                except Exception as e:
                    print("⚠️ Agno search-agent failed, falling back to Serper:", e)
                    import traceback
                    traceback.print_exc()

            # Otherwise proceed with prompt-generation + Serper flow (existing code)
            # Ask Gemini to propose 2-3 very targeted search queries (profile-oriented)
            user_ctx = f"Campaign title: {title}\nNiche: {niche}\nPrimary platform: {primary_platform}\nPreference: {follower_pref}\nLocation: {location or 'N/A'}"
            if user_instruction:
                user_ctx += f"\nUser request: {user_instruction}"
            prompt = f"{self.SYSTEM_PROMPT}\n\n{user_ctx}\n\nReturn the JSON array now:"

            prompts = []
            try:
                gen_text = await generate_text(prompt, temperature=0.0, max_tokens=300)
                print("🔎 Gemini generated prompts raw:", repr(gen_text)[:2000])
                if gen_text:
                    # Strip markdown fences from Gemini output before parsing
                    cleaned = gen_text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    parsed = json.loads(cleaned.strip())
                    if isinstance(parsed, list):
                        prompts = [p.strip() for p in parsed if isinstance(p, str) and p.strip()]
            except Exception as e:
                # Gemini generation may fail depending on client; fall back to deterministic templates
                print(f"⚠️ Gemini prompt failed: {e}")
                import traceback
                traceback.print_exc()

            # Normalize queries to plain English. Prefer user_instruction as first query.
            normalized = []
            if user_instruction:
                normalized.append(user_instruction.strip())

            if prompts:
                for p in prompts:
                    plain = self._to_plain_query(p, location=location)
                    if plain and plain not in normalized:
                        normalized.append(plain)

            if not normalized:
                normalized = self._fallback_build_prompts(title, niche, primary_platform, location, user_instruction)

            # make sure prompts are trimmed / safe
            clean_prompts = []
            for q in normalized[:3]:
                q = re.sub(r'[\r\n]+', ' ', q).strip()
                if len(q) > 180:
                    q = q[:180].rsplit(" ", 1)[0]
                clean_prompts.append(q)
            prompts = clean_prompts[:3]

            print(f"🔎 Running {len(prompts)} search prompts against Serper:")
            for i, p in enumerate(prompts, 1):
                print(f"  {i}. {p}")

            # Run Serper search() per prompt to get raw organic results
            raw_results = await self._run_search_prompts(prompts, count)
            print(f"📊 Aggregated {len(raw_results)} raw results from prompts")

            # Deduplicate by link
            unique = []
            seen = set()
            for r in raw_results:
                link = (r.get("link") or "").split("?")[0].rstrip("/")
                if not link or link in seen:
                    continue
                seen.add(link)
                unique.append(r)
            print(f"✅ Deduped to {len(unique)} unique links")

            # Let Gemini post-process raw results into clean influencer objects
            parsed_with_gemini = await self._parse_with_gemini(unique, primary_platform, user_instruction=user_instruction)
            if parsed_with_gemini:
                print(f"✅ Gemini parsed {len(parsed_with_gemini)} influencer objects (capped to {count})")
                return parsed_with_gemini[:count]
 
            # Fallback local parsing
            cleaned = self._simple_parse_results(unique, primary_platform)
            print(f"✅ Fallback parsed {len(cleaned)} influencer objects (capped to {count})")
            return cleaned[:count]
 
        except Exception as e:
            print(f"❌ Error finding influencers: {e}")
            import traceback; traceback.print_exc()
            return []

    async def regenerate_influencers(
        self,
        campaign_draft: Dict[str, Any],
        old_list: List[Dict[str, Any]],
        user_instruction: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Regenerate influencer/org list based on new constraints.
        This does NOT require a day_number.
        """
        try:
            constraints = []
            if filters.get("followers_lt"):
                constraints.append(f"followers under {int(filters['followers_lt'])}")
            if filters.get("followers_gt"):
                constraints.append(f"followers over {int(filters['followers_gt'])}")
            if filters.get("location"):
                constraints.append(f"location {filters['location']}")
            if filters.get("orgs_only"):
                constraints.append("organizations only")
            if filters.get("ngos_only"):
                constraints.append("NGOs only")
            if user_instruction:
                constraints.append(user_instruction)

            draft = dict(campaign_draft)
            draft["influencer_preference"] = ", ".join(constraints)
            new_list = await self.find_influencers(campaign_draft=draft, count=10, user_instruction=user_instruction)
            # ensure strict cap before returning
            return (new_list or [])[:10]
        except Exception as e:
            print(f"❌ regenerate_influencers failed: {e}")
            import traceback; traceback.print_exc()
            return []

# Global instance (unchanged)
_influencer_agent = None

def get_influencer_agent() -> InfluencerAgent:
    """Get or create InfluencerAgent instance"""
    global _influencer_agent
    if _influencer_agent is None:
        _influencer_agent = InfluencerAgent()
    return _influencer_agent