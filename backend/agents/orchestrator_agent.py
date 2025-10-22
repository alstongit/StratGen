from typing import Dict, Any, List
from datetime import datetime
import asyncio

from services.supabase_service import get_supabase_service
from agents.content_agent import get_content_agent
from agents.image_agent import get_image_agent
from agents.influencer_agent import get_influencer_agent
from agents.plan_agent import get_plan_agent

class OrchestratorAgent:
    """
    Orchestrates the entire asset generation process.
    Coordinates Content, Image, Influencer, and Plan agents.
    Handles partial failures gracefully.
    """
    
    def __init__(self):
        self.supabase_service = get_supabase_service()
        
        # Initialize all sub-agents
        self.content_agent = get_content_agent()
        self.image_agent = get_image_agent()
        self.influencer_agent = get_influencer_agent()
        self.plan_agent = get_plan_agent()
        
        print("✅ OrchestratorAgent initialized with all sub-agents")
    
    async def execute_campaign(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any]
    ) -> bool:
        """
        Execute the full asset generation pipeline.
        Continues even if some agents fail.
        
        Args:
            campaign_id: UUID of the campaign
            final_draft: The confirmed draft JSON from /strategy
            
        Returns:
            True if at least copy generation succeeded, False otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            print(f"\n{'='*60}")
            print(f"🚀 STARTING ASSET GENERATION FOR CAMPAIGN: {campaign_id}")
            print(f"{'='*60}\n")
            
            # Update campaign status to 'executing'
            await self._update_campaign_status(
                campaign_id,
                status="executing",
                execution_started_at=datetime.utcnow()
            )
            
            await self._send_progress_message(
                campaign_id,
                "🎬 Starting asset generation pipeline..."
            )
            
            # Parse posting schedule
            posting_schedule = final_draft.get("posting_schedule", {})
            num_days = len(posting_schedule)
            
            print(f"📅 Campaign duration: {num_days} days")
            
            # PHASE 1: Generate copy content (CRITICAL - must succeed)
            print(f"\n{'='*60}")
            print(f"PHASE 1: COPY GENERATION")
            print(f"{'='*60}")
            
            copy_assets = await self._generate_all_copy(
                campaign_id,
                final_draft,
                num_days
            )
            
            if not copy_assets:
                raise Exception("Failed to generate any copy content")
            
            print(f"✅ Copy generation completed: {len(copy_assets)} posts")
            
            # PHASE 2: Generate images, influencers, and plan in parallel
            # These can fail individually without failing entire campaign
            print(f"\n{'='*60}")
            print(f"PHASE 2: PARALLEL ASSET GENERATION (Non-Critical)")
            print(f"{'='*60}")
            
            await self._send_progress_message(
                campaign_id,
                "🎨 Generating images, finding influencers, and creating plan..."
            )
            
            # Run in parallel with exception handling
            results = await asyncio.gather(
                self._generate_all_images(campaign_id, final_draft, copy_assets),
                self._generate_influencers(campaign_id, final_draft),
                self._generate_plan(campaign_id, final_draft, copy_assets),
                return_exceptions=True
            )
            
            # Process results
            image_assets = results[0] if not isinstance(results[0], Exception) else []
            influencer_assets = results[1] if not isinstance(results[1], Exception) else []
            plan_asset = results[2] if not isinstance(results[2], Exception) else None
            
            # Log any failures
            task_names = ["Images", "Influencers", "Plan"]
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"⚠️ {task_names[i]} generation failed (non-critical): {result}")
                    await self._send_progress_message(
                        campaign_id,
                        f"⚠️ {task_names[i]} generation failed, but continuing..."
                    )
                else:
                    count = len(result) if isinstance(result, list) else (1 if result else 0)
                    print(f"✅ {task_names[i]} completed: {count} items")
            
            # Mark as completed (even with partial success)
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            await self._update_campaign_status(
                campaign_id,
                status="completed",
                execution_completed_at=end_time
            )
            
            # Send completion message
            success_count = sum([
                1,  # Copy always succeeds (we checked earlier)
                1 if image_assets else 0,
                1 if influencer_assets else 0,
                1 if plan_asset else 0
            ])
            
            await self._send_progress_message(
                campaign_id,
                f"✅ Campaign generation complete! ({success_count}/4 components succeeded in {execution_time:.1f}s)"
            )
            
            print(f"\n{'='*60}")
            print(f"✅ ASSET GENERATION COMPLETED FOR CAMPAIGN: {campaign_id}")
            print(f"   Copy: {len(copy_assets)} posts")
            print(f"   Images: {len(image_assets) if isinstance(image_assets, list) else 0}")
            print(f"   Influencers: {len(influencer_assets) if isinstance(influencer_assets, list) else 0}")
            print(f"   Plan: {'Yes' if plan_asset else 'No'}")
            print(f"   Execution Time: {execution_time:.1f}s")
            print(f"{'='*60}\n")
            
            return True
        
        except Exception as e:
            print(f"❌ CRITICAL ERROR in orchestrator: {e}")
            import traceback
            traceback.print_exc()
            
            await self._update_campaign_status(
                campaign_id,
                status="failed"
            )
            
            await self._send_progress_message(
                campaign_id,
                f"❌ Campaign generation failed: {str(e)}"
            )
            
            return False
    
    async def _generate_all_copy(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        num_days: int
    ) -> List[Dict[str, Any]]:
        """Generate copy content for all days"""
        print(f"\n📝 Generating copy for {num_days} days...")
        
        posting_schedule = final_draft.get("posting_schedule", {})
        copy_assets = []
        
        for day_key, day_info in posting_schedule.items():
            try:
                day_number = int(day_key.split("_")[1])
                
                print(f"📝 Generating copy for Day {day_number}...")
                
                copy_content = await self.content_agent.generate_post_copy(
                    campaign_draft=final_draft,
                    day_number=day_number,
                    day_info=day_info
                )
                
                asset_id = await self._save_asset(
                    campaign_id=campaign_id,
                    asset_type="copy",
                    day_number=day_number,
                    content=copy_content,
                    status="completed"
                )
                
                copy_assets.append({
                    "id": asset_id,
                    "day_number": day_number,
                    "content": copy_content
                })
                
                print(f"✅ Day {day_number} copy saved (ID: {asset_id})")
                
            except Exception as e:
                print(f"❌ Error generating copy for {day_key}: {e}")
        
        print(f"✅ All copy generated: {len(copy_assets)} posts")
        return copy_assets
    
    async def _generate_all_images(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        copy_assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate images for all days"""
        print(f"\n🎨 Generating images for {len(copy_assets)} posts...")
        
        image_assets = []
        
        for i, copy_asset in enumerate(copy_assets, 1):
            try:
                day_number = copy_asset["day_number"]
                copy_content = copy_asset["content"]
                
                print(f"\n🎨 Generating image for Day {day_number}...")
                
                image_data = await self.image_agent.generate_image(
                    campaign_id=campaign_id,
                    campaign_draft=final_draft,
                    copy_content=copy_content,
                    day_number=day_number
                )
                
                asset_id = await self._save_asset(
                    campaign_id=campaign_id,
                    asset_type="image",
                    day_number=day_number,
                    content=image_data,
                    status="completed"
                )
                
                image_assets.append({
                    "id": asset_id,
                    "day_number": day_number,
                    "content": image_data
                })
                
                print(f"✅ Day {day_number} image saved (ID: {asset_id})")
                
            except Exception as e:
                print(f"⚠️ Error generating image for day {copy_asset.get('day_number')}: {e}")
                # Continue with other images
        
        print(f"✅ All images generated: {len(image_assets)} images")
        return image_assets
    
    async def _generate_influencers(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find and save influencers"""
        print(f"\n👥 Finding influencers...")
        
        try:
            influencers = await self.influencer_agent.find_influencers(
                campaign_draft=final_draft,
                count=10
            )
            
            if not influencers:
                print(f"⚠️ No influencers found")
                return []
            
            influencer_assets = []
            
            for i, influencer in enumerate(influencers, 1):
                asset_id = await self._save_asset(
                    campaign_id=campaign_id,
                    asset_type="influencer",
                    day_number=None,
                    content=influencer,
                    status="completed"
                )
                
                influencer_assets.append({
                    "id": asset_id,
                    "content": influencer
                })
            
            print(f"✅ All influencers saved: {len(influencer_assets)} influencers")
            return influencer_assets
        
        except Exception as e:
            print(f"⚠️ Error finding influencers: {e}")
            return []
    
    async def _generate_plan(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        copy_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate execution plan"""
        print(f"\n📋 Creating execution plan...")
        
        try:
            plan_data = await self.plan_agent.create_execution_plan(
                campaign_draft=final_draft,
                generated_assets=copy_assets
            )
            
            asset_id = await self._save_asset(
                campaign_id=campaign_id,
                asset_type="plan",
                day_number=None,
                content=plan_data,
                status="completed"
            )
            
            print(f"✅ Execution plan saved (ID: {asset_id})")
            
            return {
                "id": asset_id,
                "content": plan_data
            }
        
        except Exception as e:
            print(f"⚠️ Error creating execution plan: {e}")
            return None
    
    async def _save_asset(
        self,
        campaign_id: str,
        asset_type: str,
        day_number: int,
        content: Dict[str, Any],
        status: str = "completed"
    ) -> str:
        """Save asset to campaign_assets table"""
        result = self.supabase_service.supabase.table("campaign_assets").insert({
            "campaign_id": campaign_id,
            "asset_type": asset_type,
            "day_number": day_number,
            "content": content,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        
        return result.data[0]["id"]
    
    async def _update_campaign_status(
        self,
        campaign_id: str,
        status: str,
        execution_started_at: datetime = None,
        execution_completed_at: datetime = None
    ):
        """Update campaign status in database"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
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

# Global instance
_orchestrator_agent = None

def get_orchestrator_agent() -> OrchestratorAgent:
    """Get or create OrchestratorAgent instance"""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        _orchestrator_agent = OrchestratorAgent()
    return _orchestrator_agent