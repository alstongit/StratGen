from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime

from middleware.auth_middleware import get_current_user
from config.supabase_client import get_admin_supabase_client
from services.supabase_service import SupabaseService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.get("")
async def get_campaigns(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all campaigns for the authenticated user."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        
        response = supabase.table("campaigns").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        return response.data or []
    
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )

@router.post("")
async def create_campaign(
    campaign_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new campaign."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        
        new_campaign = {
            "user_id": user_id,
            "title": campaign_data.get("title", "Untitled Campaign"),
            "initial_prompt": campaign_data.get("initial_prompt", ""),
            "status": "drafting",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("campaigns").insert(new_campaign).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create campaign"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific campaign by ID."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        campaign = service.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this campaign"
            )
        
        return campaign
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign: {str(e)}"
        )

@router.get("/{campaign_id}/messages")
async def get_campaign_messages(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all messages for a campaign."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        # Verify campaign ownership
        campaign = service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this campaign"
            )
        
        # Get messages
        messages = service.get_campaign_messages(campaign_id)
        return messages
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )

@router.patch("/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    updates: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a campaign."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        campaign = service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this campaign"
            )
        
        updated_campaign = service.update_campaign(campaign_id, updates)
        
        return updated_campaign
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a campaign."""
    try:
        user_id = current_user["user_id"]
        supabase = get_admin_supabase_client()
        
        campaign_response = supabase.table("campaigns").select("*").eq("id", campaign_id).single().execute()
        
        if not campaign_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this campaign"
            )
        
        supabase.table("campaigns").delete().eq("id", campaign_id).execute()
        
        return {"message": "Campaign deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )