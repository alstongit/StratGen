from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime

from middleware.auth_middleware import get_current_user
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