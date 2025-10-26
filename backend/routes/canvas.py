from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
import uuid

from middleware.auth_middleware import get_current_user
from agents.modification_classifier import classify_modification
from agents.orchestrator_agent import get_orchestrator_agent
from agents.regeneration_agent import get_regeneration_agent
from config.supabase_client import get_admin_supabase_client

router = APIRouter(prefix="/canvas", tags=["canvas"])

@router.get("/{campaign_id}")
async def get_canvas_data(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all canvas data for a campaign."""
    try:
        print(f"\n📊 === FETCHING CANVAS DATA ===")
        print(f"Campaign ID: {campaign_id}")
        print(f"User ID: {current_user['sub']}")
        
        supabase = get_admin_supabase_client()
        
        # Get campaign
        print(f"🔍 Fetching campaign...")
        campaign_result = supabase.table("campaigns").select("*").eq(
            "id", campaign_id
        ).eq("user_id", current_user["sub"]).execute()
        
        if not campaign_result.data:
            print(f"❌ Campaign not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign = campaign_result.data[0]
        print(f"✅ Campaign: {campaign['title']} (status: {campaign['status']})")
        
        # Get all assets
        print(f"🔍 Fetching assets...")
        assets_result = supabase.table("campaign_assets").select("*").eq(
            "campaign_id", campaign_id
        ).order("day_number", desc=False).execute()
        
        assets = assets_result.data
        print(f"📦 Found {len(assets)} total assets")
        
        # Organize assets
        posts = []
        influencers = []
        plan = None
        days_map = {}
        
        for asset in assets:
            asset_type = asset.get("asset_type")
            asset_id = asset.get("id", "unknown")[:8]
            day_num = asset.get("day_number")
            
            print(f"  📄 {asset_type} (day: {day_num}, id: {asset_id})")
            
            if asset_type == "copy":
                if day_num not in days_map:
                    days_map[day_num] = {
                        "day_number": day_num,
                        "copy": None,
                        "image": None
                    }
                days_map[day_num]["copy"] = asset
                print(f"    ✓ Copy added to day {day_num}")
            
            elif asset_type == "image":
                if day_num not in days_map:
                    days_map[day_num] = {
                        "day_number": day_num,
                        "copy": None,
                        "image": None
                    }
                days_map[day_num]["image"] = asset
                
                # Log image URL
                image_url = asset.get("content", {}).get("image_url", "N/A")
                print(f"    ✓ Image added to day {day_num}: {image_url[:60]}...")
            
            elif asset_type == "influencer":
                influencers.append(asset)
                influencer_name = asset.get("content", {}).get("name", "Unknown")
                print(f"    ✓ Influencer: {influencer_name}")
            
            elif asset_type == "plan":
                plan = asset
                phases_count = len(asset.get("content", {}).get("phases", []))
                print(f"    ✓ Plan with {phases_count} phases")
        
        # Convert days_map to sorted list
        posts = [days_map[day] for day in sorted(days_map.keys())]
        
        print(f"\n📊 === CANVAS DATA SUMMARY ===")
        print(f"Posts: {len(posts)}")
        print(f"Influencers: {len(influencers)}")
        print(f"Plan: {'Yes' if plan else 'No'}")
        
        # Log each post's structure
        for i, post in enumerate(posts, 1):
            has_copy = bool(post.get("copy"))
            has_image = bool(post.get("image"))
            print(f"  Post {i}: copy={has_copy}, image={has_image}")
        
        response_data = {
            "campaign": campaign,
            "posts": posts,
            "influencers": influencers,
            "plan": plan,
            "stats": {
                "total_posts": len(posts),
                "total_influencers": len(influencers),
                "status": campaign.get("status"),
                "execution_time": _calculate_execution_time(campaign)
            }
        }
        
        print(f"✅ Canvas data prepared successfully\n")
        
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching canvas data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch canvas data: {str(e)}"
        )

def _calculate_execution_time(campaign: Dict[str, Any]) -> float:
    """Calculate execution time in seconds"""
    started = campaign.get("execution_started_at")
    completed = campaign.get("execution_completed_at")
    
    if not started or not completed:
        return 0.0
    
    try:
        from dateutil import parser
        start_dt = parser.parse(started)
        end_dt = parser.parse(completed)
        return (end_dt - start_dt).total_seconds()
    except:
        return 0.0

@router.post("/{campaign_id}/modify")
async def modify_canvas(
    campaign_id: str,
    body: Dict[str, Any],
    background: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Entry point for prompt-based canvas modifications using RegenerationAgent.
    """
    message = (body or {}).get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    supabase = get_admin_supabase_client()

    # Auth: ensure campaign belongs to user
    campaign_q = supabase.table("campaigns").select("*").eq("id", campaign_id).eq("user_id", current_user["sub"]).execute()
    if not campaign_q.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign = campaign_q.data[0]
    final_draft = campaign.get("final_draft_json") or campaign.get("draft_json")
    if not final_draft:
        raise HTTPException(status_code=400, detail="No campaign draft available")

    # Fetch full canvas data (posts, influencers, plan with content)
    print(f"🔍 Fetching full canvas data for modification analysis...")
    canvas_data = await _get_full_canvas_data(campaign_id, current_user["sub"])
    
    # Analyze modification with RegenerationAgent
    regen_agent = get_regeneration_agent()
    plan = await regen_agent.analyze_modification(
        user_prompt=message,
        final_draft=final_draft,
        canvas_data=canvas_data
    )
    
    # Check if clarification needed
    if plan.get("needs_clarification"):
        raise HTTPException(
            status_code=400,
            detail=plan.get("clarify_message") or "Please provide more details about what you'd like to change."
        )
    
    # Create canvas_modifications record
    import uuid
    from datetime import datetime
    mod_id = str(uuid.uuid4())
    
    # Map action operation to valid modification_type for DB constraint
    # Get operation from first action (even if multiple actions)
    operation = plan.get("actions", [{}])[0].get("operation", "modify_content")
    # Map operation to valid modification_type
    operation_map = {
        "modify_fields": "modify_content",
        "regenerate": "regenerate",
        "change_style": "change_style",
        "add_element": "add_element",
        "remove_element": "remove_element"
    }
    mod_type = operation_map.get(operation, "modify_content")
    
    supabase.table("canvas_modifications").insert({
        "id": mod_id,
        "campaign_id": campaign_id,
        "user_message": message,
        "modification_type": mod_type,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    # Execute plan via orchestrator
    orchestrator = get_orchestrator_agent()
    
    # Determine if sync or async (sync if all content/small changes, async if images/influencers)
    has_async = any(
        action.get("agent") in ["image_agent", "influencer_agent", "plan_agent"]
        for action in plan.get("actions", [])
    )
    
    if not has_async:
        # Execute synchronously
        try:
            result = await orchestrator.execute_modification_plan(
                campaign_id=campaign_id,
                final_draft=final_draft,
                actions=plan.get("actions", []),
                modification_id=mod_id
            )
            return {"modification_id": mod_id, "status": "completed", "result": result}
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Execute in background
        background.add_task(
            orchestrator.execute_modification_plan,
            campaign_id,
            final_draft,
            plan.get("actions", []),
            mod_id
        )
        return {"modification_id": mod_id, "status": "accepted"}

async def _get_full_canvas_data(campaign_id: str, user_id: str) -> Dict[str, Any]:
    """Helper to fetch complete canvas data for modification analysis."""
    supabase = get_admin_supabase_client()
    
    # Get assets with full content
    assets_result = supabase.table("campaign_assets").select("*").eq(
        "campaign_id", campaign_id
    ).order("day_number", desc=False).execute()
    
    assets = assets_result.data
    
    # Organize assets
    posts = []
    influencers = []
    plan = None
    days_map = {}
    
    for asset in assets:
        asset_type = asset.get("asset_type")
        day_num = asset.get("day_number")
        
        if asset_type == "copy":
            if day_num not in days_map:
                days_map[day_num] = {"day_number": day_num, "copy": None, "image": None}
            days_map[day_num]["copy"] = asset
        
        elif asset_type == "image":
            if day_num not in days_map:
                days_map[day_num] = {"day_number": day_num, "copy": None, "image": None}
            days_map[day_num]["image"] = asset
        
        elif asset_type == "influencer":
            influencers.append(asset)
        
        elif asset_type == "plan":
            plan = asset
    
    # Convert days_map to sorted list
    posts = [days_map[day] for day in sorted(days_map.keys())]
    
    return {
        "posts": posts,
        "influencers": influencers,
        "plan": plan
    }

@router.get("/{campaign_id}/modifications/{modification_id}")
async def get_modification_status(
    campaign_id: str,
    modification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Poll modification status. Uses canvas_modifications snapshot to determine completion.
    """
    supabase = get_admin_supabase_client()

    # Safe fetch of modification record (avoid rpc dependency)
    mod_res = supabase.table("canvas_modifications").select("*").eq("id", modification_id).execute()
    mod = (mod_res.data or [None])[0]
    if not mod:
        raise HTTPException(status_code=404, detail="Modification not found")

    # ownership check
    camp_res = supabase.table("campaigns").select("id,user_id").eq("id", mod["campaign_id"]).execute()
    camp = (camp_res.data or [None])[0]
    if not camp or camp["user_id"] != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    is_done = mod.get("new_content") is not None
    status_label = "completed" if is_done else "processing"
    return {
        "status": status_label,
        "affected_asset_id": mod.get("affected_asset_id"),
        "previous_content": mod.get("previous_content") if is_done else None,
        "new_content": mod.get("new_content") if is_done else None
    }