from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime

from middleware.auth_middleware import get_current_user
from config.supabase_client import get_admin_supabase_client
from models.message import CreateCampaignRequest, Campaign, MessageResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("", response_model=Campaign)
async def create_campaign(
    request: CreateCampaignRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new campaign"""
    try:
        print(f"🔍 Creating campaign for user: {current_user}")
        
        supabase = get_admin_supabase_client()
        
        # Create campaign
        campaign_data = {
            "user_id": current_user["sub"],
            "title": request.title,
            "initial_prompt": request.initial_prompt or "",  # Allow empty
            "status": "drafting",
            "draft_json": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        print(f"📝 Inserting campaign data: {campaign_data}")
        
        result = supabase.table("campaigns").insert(campaign_data).execute()
        campaign = result.data[0]
        
        print(f"✅ Campaign created: {campaign['id']}")
        
        # Only create initial message if initial_prompt is not empty
        if request.initial_prompt and request.initial_prompt.strip():
            initial_message = {
                "campaign_id": campaign["id"],
                "role": "user",
                "content": request.initial_prompt,
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("chat_messages").insert(initial_message).execute()
            print(f"✅ Initial message created")
        
        return campaign
    
    except Exception as e:
        print(f"❌ Error creating campaign: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("", response_model=List[Campaign])
async def get_campaigns(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all campaigns for current user"""
    try:
        print(f"🔍 Fetching campaigns for user: {current_user}")
        
        supabase = get_admin_supabase_client()
        
        result = supabase.table("campaigns").select("*").eq(
            "user_id", current_user["sub"]
        ).order("created_at", desc=True).execute()
        
        print(f"📊 Found {len(result.data)} campaigns")
        
        return result.data
    
    except Exception as e:
        print(f"❌ Error fetching campaigns: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get single campaign by ID"""
    try:
        print(f"🔍 Getting campaign {campaign_id} for user: {current_user}")
        
        supabase = get_admin_supabase_client()
        
        # First, check if campaign exists at all
        all_campaigns = supabase.table("campaigns").select("id, user_id").eq(
            "id", campaign_id
        ).execute()
        
        print(f"📊 Campaign query result: {all_campaigns.data}")
        
        if not all_campaigns.data:
            print(f"❌ Campaign {campaign_id} does not exist in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign_data = all_campaigns.data[0]
        print(f"🔍 Campaign user_id: {campaign_data['user_id']}")
        print(f"🔍 Current user sub: {current_user['sub']}")
        
        if campaign_data['user_id'] != current_user['sub']:
            print(f"❌ User mismatch! Campaign belongs to {campaign_data['user_id']}, but request from {current_user['sub']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Now get full campaign data
        result = supabase.table("campaigns").select("*").eq(
            "id", campaign_id
        ).eq("user_id", current_user["sub"]).execute()
        
        print(f"✅ Campaign found: {result.data[0]['title']}")
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting campaign: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )

@router.get("/{campaign_id}/messages", response_model=List[MessageResponse])
async def get_campaign_messages(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all messages for a campaign"""
    try:
        print(f"🔍 Getting messages for campaign {campaign_id}")
        
        supabase = get_admin_supabase_client()
        
        # Verify campaign ownership
        campaign_result = supabase.table("campaigns").select("id").eq(
            "id", campaign_id
        ).eq("user_id", current_user["sub"]).execute()
        
        if not campaign_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get messages
        messages_result = supabase.table("chat_messages").select("*").eq(
            "campaign_id", campaign_id
        ).order("created_at", desc=False).execute()
        
        print(f"📊 Found {len(messages_result.data)} messages")
        
        return messages_result.data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting messages: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a campaign"""
    try:
        print(f"🔍 Deleting campaign {campaign_id} for user: {current_user}")
        
        supabase = get_admin_supabase_client()
        
        # Verify ownership
        result = supabase.table("campaigns").select("id").eq(
            "id", campaign_id
        ).eq("user_id", current_user["sub"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Delete campaign
        supabase.table("campaigns").delete().eq("id", campaign_id).execute()
        
        print(f"✅ Campaign deleted: {campaign_id}")
        
        return {"message": "Campaign deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting campaign: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )