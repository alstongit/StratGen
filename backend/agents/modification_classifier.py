from utils.gemini_client import generate_text, generate_json
import json
import re
from typing import Dict, Any, List

SYSTEM_INSTRUCTIONS = """
You classify a user's natural-language request into a strict JSON action list for modifying a campaign canvas.
Return ONLY JSON (no explanation). The top-level object MUST be:

{
  "needs_clarification": false,
  "clarify_message": null,
  "actions": [
    {
      "asset_type": "copy" | "image" | "influencer" | "plan",
      "action": "regenerate" | "modify_content" | "change_style" | "add_element" | "remove_element",
      "target": {
        "day_numbers": [number,...] | null,
        "apply_to": "specific" | "all" | "inferred" | null,
        "match_text": "optional short snippet used to match posts" | null
      },
      "fields": ["caption","hashtags","description","cta","headline","image"] | [],
      "user_instruction": "short imperative instruction (<=120 chars)",
      "evidence": "short explanation if you inferred day(s), else null",
      "mode_hint": "sync" | "async"
    }
  ]
}

Rules:
- If the user mentions specific day(s), set day_numbers to those integers.
- If the user omits day but describes content ("the long post about travel"), try to infer matching day(s) by matching content; set apply_to:"inferred" and provide evidence.
- If the user means "all days" or "every day", set apply_to:"all" and day_numbers:null.
- If ambiguous and you cannot reasonably infer days, set needs_clarification:true and provide a concise clarify_message.
- Keep user_instruction concise; prefer imperative phrasing.
"""

def _normalize_asset(token: str) -> str:
    t = (token or "").lower()
    if "image" in t or "photo" in t:
        return "image"
    if "caption" in t or "copy" in t or "post" in t or "headline" in t or "description" in t or "hashtags" in t or "cta" in t:
        return "copy"
    if "plan" in t or "pre-launch" in t or "milestone" in t or "checklist" in t or "metric" in t or "recommend" in t:
        return "plan"
    if "influencer" in t or "influencers" in t:
        return "influencer"
    return "unknown"

def _extract_day(text: str):
    m = re.search(r"(?:day\s*|d\s*|day_?)(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*(?:st|nd|rd|th)?\s*(?:day|day post|post)?", text, re.I)
    if m:
        return int(m.group(1))
    return None

def _classify_with_regex(message: str, final_draft: Dict[str, Any]) -> Dict[str, Any]:
    text = (message or "").strip()
    if not text:
        return {"needs_clarification": True, "clarify_message": "Empty message", "actions": []}

    parts = re.split(r'\s*(?:\band\b|;|\n)\s*', text, flags=re.I)
    actions: List[Dict[str, Any]] = []

    for part in parts:
        p = part.strip()
        if not p:
            continue

        m = re.search(r'(?P<verb>change|update|regenerate|replace|modify|rewrite)\s+(?P<target>[\w\- ]{2,60})(?:\s+(?:of|for|on))?(?:\s*(?:day\s*)?(?P<day>\d+))?(?:\s*(?:to|with|into|:)\s*(?P<instr>.*))?$', p, flags=re.I)
        if m:
            target = m.group("target") or ""
            day = _extract_day(p) if not m.group("day") else int(m.group("day"))
            instr = (m.group("instr") or "").strip()
            asset = _normalize_asset(target)

            fields = []
            t = p.lower()
            if "caption" in t: fields.append("caption")
            if "hashtag" in t or "hashtags" in t: fields.append("hashtags")
            if "cta" in t or "call to action" in t: fields.append("cta")
            if "headline" in t or "title" in t: fields.append("headline")
            if "description" in t or "details" in t: fields.append("description")
            if "image" in t or "photo" in t: fields.append("image")
            if "entire" in t or "whole" in t or "complete" in t or "all" in t:
                fields = []

            target_obj = {"day_numbers": [day] if day else None, "apply_to": "specific" if day else None, "match_text": None}

            actions.append({
                "asset_type": asset,
                "action": "modify_content",
                "target": target_obj,
                "fields": fields,
                "user_instruction": instr or p,
                "evidence": None,
                "mode_hint": "async" if asset in ("image","plan","influencer") else "sync",
                "raw_text": p
            })
            continue

        # fallback guess
        asset_guess = "plan" if re.search(r'plan|phase|pre-launch|milestone|checklist|metric', p, re.I) else ("image" if re.search(r'image|photo|visual', p, re.I) else "copy")
        day_guess = _extract_day(p)
        target_obj = {"day_numbers": [day_guess] if day_guess else None, "apply_to": "specific" if day_guess else None, "match_text": None}
        actions.append({
            "asset_type": asset_guess,
            "action": "modify_content",
            "target": target_obj,
            "fields": [],
            "user_instruction": p,
            "evidence": None,
            "raw_text": p
        })

    if not actions:
        return {"needs_clarification": True, "clarify_message": "I couldn't parse what to change. Please specify e.g. 'change caption of day 2 to X'.", "actions": []}

    return {"needs_clarification": False, "clarify_message": None, "actions": actions}

def _validate_actions(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    if "actions" not in payload or not isinstance(payload["actions"], list):
        return False
    for a in payload["actions"]:
        if "asset_type" not in a or "action" not in a or "user_instruction" not in a or "target" not in a:
            return False
    return True

def _summarize_final_draft(final_draft: Dict[str, Any]) -> str:
    try:
        schedule = final_draft.get("posting_schedule", {}) or {}
        lines = []
        for k, v in schedule.items():
            try:
                day_num = int(k.split("_")[1])
            except Exception:
                day_num = None
            caption = v.get("caption") if isinstance(v, dict) else (v or "")
            if caption and day_num:
                lines.append(f"Day {day_num}: {caption[:120]}")
        return "\n".join(lines[:12])
    except Exception:
        return ""

async def classify_modification(message: str, final_draft: Dict[str, Any]) -> Dict[str, Any]:
    text_lower = (message or "").lower()

    influencer_keywords = [
        "influencer", "influencers", "find influencers", "refetch influencers",
        "recommend influencers", "scout influencers", "search influencers",
        "fetch influencers", "get influencers"
    ]
    if any(k in text_lower for k in influencer_keywords):
        return {
            "needs_clarification": False,
            "clarify_message": None,
            "actions": [
                {
                    "asset_type": "influencer",
                    "action": "regenerate",
                    "target": {"day_numbers": None, "apply_to": "all", "match_text": None},
                    "fields": [],
                    "user_instruction": message,
                    "evidence": None,
                    "mode_hint": "async",
                    "raw_text": message
                }
            ]
        }

    # Build examples for few-shot
    examples = [
        {"user":"change image of day 1 to a globe", "assistant":{"actions":[{"asset_type":"image","action":"regenerate","target":{"day_numbers":[1],"apply_to":"specific","match_text":None},"fields":[],"user_instruction":"Make image a globe theme","evidence":None,"mode_hint":"async"}]}},
        {"user":"make day 2 description shorter","assistant":{"actions":[{"asset_type":"copy","action":"modify_content","target":{"day_numbers":[2],"apply_to":"specific","match_text":None},"fields":["description"],"user_instruction":"Shorten description for day 2","evidence":None,"mode_hint":"sync"}]}},
        {"user":"make all images colorful","assistant":{"actions":[{"asset_type":"image","action":"change_style","target":{"day_numbers":None,"apply_to":"all","match_text":None},"fields":["image"],"user_instruction":"Make images colorful","evidence":None,"mode_hint":"async"}]}}
    ]

    draft_summary = _summarize_final_draft(final_draft)
    prompt_parts = [SYSTEM_INSTRUCTIONS, "\n\nExamples:\n"]
    for ex in examples:
        prompt_parts.append(f"USER: {ex['user']}\nASSISTANT: {json.dumps(ex['assistant'], separators=(',',':'))}\n")
    if draft_summary:
        prompt_parts.append(f"\n\nFINAL_DRAFT_SUMMARY:\n{draft_summary}\n\n")
    prompt_parts.append(f"USER: {message}\nASSISTANT: ")

    prompt = "\n".join(prompt_parts)
    try:
        # ask Gemini for strict JSON output
        parsed = await generate_json(prompt, system_instruction=SYSTEM_INSTRUCTIONS, temperature=0.0, max_tokens=800)
        if _validate_actions(parsed):
            for a in parsed["actions"]:
                a.setdefault("mode_hint", "async" if a.get("asset_type") in ("image","plan","influencer") else "sync")
                a.setdefault("fields", a.get("fields", []))
                a.setdefault("evidence", a.get("evidence", None))
                if "target" not in a:
                    a["target"] = {"day_numbers": None, "apply_to": None, "match_text": None}
            parsed.setdefault("needs_clarification", False)
            parsed.setdefault("clarify_message", None)
            return parsed
        else:
            return _classify_with_regex(message, final_draft)
    except Exception as e:
        # LLM failed — fallback to regex
        print(f"⚠️ Classifier LLM failure, falling back to regex: {e}")
        return _classify_with_regex(message, final_draft)