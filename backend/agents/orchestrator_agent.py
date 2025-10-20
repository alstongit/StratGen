from typing import Dict, Any, List
from datetime import datetime
import asyncio
import json

from services.supabase_service import SupabaseService
from services.serper_service import get_serper_service
from services.pollinations_service import get_pollinations_service
from utils.storage_utils import get_storage_utils

class OrchestratorAgent:
    """
    Orchestrates the entire asset generation process.
    Coordinates Content, Image, Influencer, and Plan agents.
    """
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.serper_service = get_serper_service()
        self.pollinations_service = get_pollinations_service()
        self.storage_utils = get_storage_utils()
        
        print("✅ OrchestratorAgent initialized")
    
    async def execute_campaign(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any]
    ) -> bool:
        """
        Execute the full asset generation pipeline.
        
        Args:
            campaign_id: UUID of the campaign
            final_draft: The confirmed draft JSON from /strategy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 STARTING ASSET GENERATION FOR CAMPAIGN: {campaign_id}")
            print(f"{'='*60}\n")
            
            # Log execution start
            await self._log_execution(campaign_id, "orchestrator", "started", {
                "draft": final_draft
            })
            
            # Update campaign status to 'executing'
            await self._update_campaign_status(
                campaign_id,
                status="executing",
                execution_started_at=datetime.utcnow()
            )
            
            # Send progress message
            await self._send_progress_message(
                campaign_id,
                "🎬 Starting asset generation pipeline..."
            )
            
            # Parse posting schedule to determine number of days
            posting_schedule = final_draft.get("posting_schedule", {})
            num_days = len(posting_schedule)
            
            print(f"📅 Campaign duration: {num_days} days")
            await self._send_progress_message(
                campaign_id,
                f"📅 Generating assets for {num_days}-day campaign..."
            )
            
            # PHASE 1: Generate copy content for all days
            print(f"\n--- PHASE 1: COPY GENERATION ---")
            copy_assets = await self._generate_all_copy(
                campaign_id,
                final_draft,
                num_days
            )
            
            # PHASE 2: Generate images, influencers, and plan in parallel
            print(f"\n--- PHASE 2: PARALLEL ASSET GENERATION ---")
            await self._send_progress_message(
                campaign_id,
                "🎨 Generating images, finding influencers, and creating plan..."
            )
            
            # Run these 3 tasks in parallel
            results = await asyncio.gather(
                self._generate_all_images(campaign_id, final_draft, copy_assets),
                self._generate_influencers(campaign_id, final_draft),
                self._generate_plan(campaign_id, final_draft, copy_assets),
                return_exceptions=True
            )
            
            # Check for errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_names = ["images", "influencers", "plan"]
                    print(f"❌ Error in {task_names[i]}: {result}")
            
            # Update campaign status to 'completed'
            await self._update_campaign_status(
                campaign_id,
                status="completed",
                execution_completed_at=datetime.utcnow()
            )
            
            # Send completion message
            await self._send_progress_message(
                campaign_id,
                "✅ All assets generated successfully! Redirecting to canvas..."
            )
            
            # Log execution completion
            await self._log_execution(campaign_id, "orchestrator", "completed", {
                "num_days": num_days,
                "copy_count": len(copy_assets),
                "status": "completed"
            })
            
            print(f"\n{'='*60}")
            print(f"✅ ASSET GENERATION COMPLETED FOR CAMPAIGN: {campaign_id}")
            print(f"{'='*60}\n")
            
            return True
        
        except Exception as e:
            print(f"❌ CRITICAL ERROR in orchestrator: {e}")
            import traceback
            traceback.print_exc()
            
            # Update campaign status to 'failed'
            await self._update_campaign_status(
                campaign_id,
                status="failed"
            )
            
            # Send error message
            await self._send_progress_message(
                campaign_id,
                f"❌ Asset generation failed: {str(e)}"
            )
            
            # Log execution failure
            await self._log_execution(campaign_id, "orchestrator", "failed", {
                "error": str(e)
            })
            
            return False
    
    async def _generate_all_copy(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        num_days: int
    ) -> List[Dict[str, Any]]:
        """Generate copy content for all days"""
        # Placeholder - will implement ContentAgent in next step
        print(f"📝 Generating copy for {num_days} days...")
        await self._send_progress_message(
            campaign_id,
            f"📝 Generating copy content... (0/{num_days})"
        )
        
        # TODO: Implement ContentAgent
        # For now, return empty list
        return []
    
    async def _generate_all_images(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        copy_assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate images for all days"""
        # Placeholder - will implement ImageAgent in next step
        print(f"🎨 Generating images for {len(copy_assets)} posts...")
        await self._send_progress_message(
            campaign_id,
            f"🎨 Generating images... (0/{len(copy_assets)})"
        )
        
        # TODO: Implement ImageAgent
        return []
    
    async def _generate_influencers(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find and save influencers"""
        print(f"👥 Finding influencers...")
        await self._send_progress_message(
            campaign_id,
            "👥 Searching for relevant influencers..."
        )
        
        # TODO: Implement InfluencerAgent
        return []
    
    async def _generate_plan(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        copy_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate execution plan"""
        print(f"📋 Creating execution plan...")
        await self._send_progress_message(
            campaign_id,
            "📋 Creating campaign execution plan..."
        )
        
        # TODO: Implement PlanAgent
        return {}
    
    async def _update_campaign_status(
        self,
        campaign_id: str,
        status: str,
        execution_started_at: datetime = None,
        execution_completed_at: datetime = None
    ):
        """Update campaign status in database"""
        update_data = {"status": status}
        
        if execution_started_at:
            update_data["execution_started_at"] = execution_started_at.isoformat()
        
        if execution_completed_at:
            update_data["execution_completed_at"] = execution_completed_at.isoformat()
        
        self.supabase_service.supabase.table("campaigns").update(
            update_data
        ).eq("id", campaign_id).execute()
    
    async def _send_progress_message(self, campaign_id: str, message: str):
        """Send progress update as system message"""
        await self.supabase_service.create_message(
            campaign_id=campaign_id,
            role="system",
            content=message,
            metadata={"event": "execution_progress"}
        )
    
    async def _log_execution(
        self,
        campaign_id: str,
        agent_name: str,
        status: str,
        data: Dict[str, Any]
    ):
        """Log agent execution to agent_execution_logs table"""
        self.supabase_service.supabase.table("agent_execution_logs").insert({
            "campaign_id": campaign_id,
            "agent_name": agent_name,
            "execution_type": "generate",
            "input_data": data if status == "started" else None,
            "output_data": data if status == "completed" else None,
            "status": status,
            "error_message": data.get("error") if status == "failed" else None,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

# Global instance
_orchestrator_agent = None

def get_orchestrator_agent() -> OrchestratorAgent:
    """Get or create OrchestratorAgent instance"""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        _orchestrator_agent = OrchestratorAgent()
    return _orchestrator_agent