from typing import Dict, Any, List, Optional
from supabase import Client
from datetime import datetime
from config.supabase_client import get_admin_supabase_client

class SupabaseService:
    """Helper service for common Supabase operations."""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        # If no client provided, use admin client
        self.supabase = supabase_client or get_admin_supabase_client()
    
    # ==================== CAMPAIGNS ====================
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by ID."""
        try:
            response = self.supabase.table("campaigns").select("*").eq("id", campaign_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error getting campaign: {e}")
            return None
    
    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a campaign."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            response = self.supabase.table("campaigns").update(updates).eq("id", campaign_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating campaign: {e}")
            raise
    
    # ==================== MESSAGES ====================
    
    def get_campaign_messages(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a campaign."""
        try:
            response = self.supabase.table("chat_messages").select("*").eq("campaign_id", campaign_id).order("created_at").execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    async def create_message(
        self,
        campaign_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new chat message."""
        try:
            message_data = {
                "campaign_id": campaign_id,
                "role": role,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat()
            }
            response = self.supabase.table("chat_messages").insert(message_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating message: {e}")
            raise
    
    # ==================== ASSETS ====================
    
    def get_campaign_assets(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all assets for a campaign."""
        try:
            response = self.supabase.table("campaign_assets").select("*").eq("campaign_id", campaign_id).order("created_at").execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting assets: {e}")
            return []
    
    def create_asset(
        self,
        campaign_id: str,
        asset_type: str,
        day_number: Optional[int] = None,
        content: Dict[str, Any] = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a new campaign asset."""
        try:
            asset_data = {
                "campaign_id": campaign_id,
                "asset_type": asset_type,
                "day_number": day_number,
                "content": content or {},
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.supabase.table("campaign_assets").insert(asset_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating asset: {e}")
            raise
    
    def update_asset(self, asset_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an asset."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            response = self.supabase.table("campaign_assets").update(updates).eq("id", asset_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating asset: {e}")
            raise

# Global singleton instance
_supabase_service = None

def get_supabase_service() -> SupabaseService:
    """Get or create SupabaseService singleton instance."""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service