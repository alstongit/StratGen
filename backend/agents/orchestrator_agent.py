from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import traceback
import re

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
            
            # Mark as completed
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            await self._update_campaign_status(
                campaign_id,
                status="completed",
                execution_completed_at=end_time
            )
            
            # Send completion message
            success_count = sum([
                1,
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
        
        print(f"✅ All images generated: {len(image_assets)} images")
        return image_assets
    
    async def _generate_influencers(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        user_instruction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find and save influencers"""
        print(f"\n👥 Finding influencers...")
        
        try:
            influencers = await self.influencer_agent.find_influencers(
                campaign_draft=final_draft,
                count=10,
                user_instruction=user_instruction
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
        day_number: Optional[int],
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
        execution_started_at: Optional[datetime] = None,
        execution_completed_at: Optional[datetime] = None
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
    
    async def execute_modification_plan(
        self,
        campaign_id: str,
        final_draft: Dict[str, Any],
        actions: List[Dict[str, Any]],
        modification_id: str
    ) -> Dict[str, Any]:
        """Execute modification plan from RegenerationAgent."""
        start = datetime.utcnow()
        results = []
        
        print(f"\n🎯 Executing modification plan: {len(actions)} action(s)")
        
        for i, action in enumerate(actions, 1):
            try:
                agent_name = action.get("agent")
                operation = action.get("operation")
                target = action.get("target", {})
                instruction = action.get("instruction", "")
                context = action.get("context", {})
                
                print(f"\n--- Action {i}/{len(actions)} ---")
                print(f"Agent: {agent_name}")
                print(f"Operation: {operation}")
                print(f"Instruction: {instruction[:80]}...")
                
                # Route to appropriate agent
                if agent_name == "content_agent":
                    result = await self._execute_content_modification(
                        campaign_id, final_draft, target, instruction, context, modification_id
                    )
                elif agent_name == "image_agent":
                    result = await self._execute_image_modification(
                        campaign_id, final_draft, target, instruction, context, modification_id
                    )
                elif agent_name == "influencer_agent":
                    result = await self._execute_influencer_modification(
                        campaign_id, final_draft, target, instruction, context, modification_id
                    )
                elif agent_name == "plan_agent":
                    result = await self._execute_plan_modification(
                        campaign_id, final_draft, target, instruction, context, modification_id
                    )
                else:
                    result = {"error": f"Unknown agent: {agent_name}"}
                
                results.append({"action": i, "success": "error" not in result, "result": result})
                print(f"✅ Action {i} completed")
            
            except Exception as e:
                print(f"❌ Action {i} failed: {e}")
                traceback.print_exc()
                results.append({"action": i, "success": False, "error": str(e)})
        
        # Update modification record
        success_count = sum(1 for r in results if r.get("success"))
        try:
            self.supabase_service.supabase.table("canvas_modifications").update({
                "new_content": {"results": results, "success_count": success_count, "total": len(actions)}
            }).eq("id", modification_id).execute()
        except Exception:
            pass
        
        end = datetime.utcnow()
        execution_time = (end - start).total_seconds()
        
        print(f"\n✅ Modification plan executed: {success_count}/{len(actions)} successful ({execution_time:.1f}s)")
        
        return {
            "total_actions": len(actions),
            "successful": success_count,
            "results": results,
            "execution_time": execution_time
        }
    
    async def _execute_content_modification(
        self, campaign_id: str, final_draft: Dict[str, Any],
        target: Dict[str, Any], instruction: str, context: Dict[str, Any],
        modification_id: str
    ) -> Dict[str, Any]:
        """Execute content modification."""
        if context is None:
            context = {}
        
        day_number = target.get("day_number")
        asset_id = target.get("asset_id")
        previous_content = context.get("previous_content", {})
        fields_to_modify = context.get("fields_to_modify")
        
        # Always fetch current asset to get asset_id
        if day_number:
            current = await self._get_asset(campaign_id, "copy", day_number)
            if current:
                asset_id = current["id"]
                if not previous_content:
                    previous_content = current.get("content", {})
            else:
                raise ValueError(f"No copy asset found for day {day_number}")
        else:
            asset_id = target.get("asset_id")
        
        if not previous_content:
            raise ValueError(f"No copy asset found for day {day_number}")
        
        await self._version_asset(asset_id, previous_content, {"operation": "modify", "modification_id": modification_id})
        
        new_content = await self.content_agent.regenerate_post_copy(
            campaign_draft=final_draft,
            day_number=day_number,
            old_content=previous_content,
            user_instruction=instruction,
            fields_to_modify=fields_to_modify
        )
        
        await self._update_asset_content(asset_id, new_content, "completed", {"modification_id": modification_id})
        
        return {"asset_id": asset_id, "day_number": day_number, "asset_type": "copy"}
    
    async def _execute_image_modification(
        self, campaign_id: str, final_draft: Dict[str, Any],
        target: Dict[str, Any], instruction: str, context: Dict[str, Any],
        modification_id: str
    ) -> Dict[str, Any]:
        """Execute image modification."""
        if context is None:
            context = {}
        
        day_number = target.get("day_number")
        asset_id = target.get("asset_id")
        previous_content = context.get("previous_content", {})
        
        # Always fetch current asset to get asset_id
        if day_number:
            current = await self._get_asset(campaign_id, "image", day_number)
            if current:
                asset_id = current["id"]
                if not previous_content:
                    previous_content = current.get("content", {})
            else:
                raise ValueError(f"No image asset found for day {day_number}")
        else:
            asset_id = target.get("asset_id")
        
        if not previous_content:
            raise ValueError(f"No image asset found for day {day_number}")
        
        await self._version_asset(asset_id, previous_content, {"operation": "modify", "modification_id": modification_id})
        await self._set_asset_status(asset_id, "generating", {"modification_id": modification_id})
        
        new_image = await self.image_agent.regenerate_image(
            campaign_id=campaign_id,
            campaign_draft=final_draft,
            day_number=day_number,
            old_image=previous_content,
            user_instruction=instruction
        )
        
        await self._update_asset_content(asset_id, new_image, "completed", {"modification_id": modification_id})
        
        return {"asset_id": asset_id, "day_number": day_number, "asset_type": "image"}
    
    async def _execute_influencer_modification(
        self, campaign_id: str, final_draft: Dict[str, Any],
        target: Dict[str, Any], instruction: str, context: Dict[str, Any],
        modification_id: str
    ) -> Dict[str, Any]:
        """Execute influencer search."""
        if context is None:
            context = {}
        
        prev_assets = self.supabase_service.supabase.table("campaign_assets").select("*").eq("campaign_id", campaign_id).eq("asset_type", "influencer").execute().data or []
        prev_snapshot = [a.get("content") for a in prev_assets]
        
        print(f"👥 Finding influencers with instruction: {instruction}")
        
        new_list = await self.influencer_agent.find_influencers(
            campaign_draft=final_draft,
            count=10,
            user_instruction=instruction
        )
        
        new_ids = []
        for item in new_list:
            asset_id = await self._save_asset(
                campaign_id=campaign_id,
                asset_type="influencer",
                day_number=None,
                content=item,
                status="completed"
            )
            new_ids.append(asset_id)
        
        await self._update_modification(modification_id, None, {"list": prev_snapshot}, {"list": new_list})
        
        print(f"✅ Found {len(new_ids)} new influencers")
        return {"asset_ids": new_ids, "count": len(new_ids), "asset_type": "influencer"}
    
    async def _execute_plan_modification(
        self, campaign_id: str, final_draft: Dict[str, Any],
        target: Dict[str, Any], instruction: str, context: Dict[str, Any],
        modification_id: str
    ) -> Dict[str, Any]:
        """Execute plan modification."""
        # Safely handle missing/null context
        if context is None:
            context = {}
        
        plan_section = target.get("plan_section")
        previous_content = context.get("previous_content", {})
        
        if not previous_content:
            plan_asset = self.supabase_service.supabase.table("campaign_assets").select("*").eq("campaign_id", campaign_id).eq("asset_type", "plan").limit(1).execute()
            plan_row = (plan_asset.data or [None])[0]
            if plan_row:
                previous_content = plan_row.get("content", {})
                asset_id = plan_row["id"]
            else:
                # No existing plan — create new one
                print("📋 No existing plan found, creating new plan...")
                new_plan = await self.plan_agent.create_execution_plan(
                    campaign_draft=final_draft,
                    generated_assets=[]  # empty for now
                )
                asset_id = await self._save_asset(
                    campaign_id=campaign_id,
                    asset_type="plan",
                    day_number=None,
                    content=new_plan,
                    status="completed"
                )
                await self._update_modification(modification_id, asset_id, {}, new_plan)
                return {"asset_id": asset_id, "asset_type": "plan", "section": plan_section}
        else:
            asset_id = target.get("asset_id")
        
        await self._version_asset(asset_id, previous_content, {"operation": "modify", "modification_id": modification_id})
        
        new_plan = await self.plan_agent.regenerate_plan(
            campaign_draft=final_draft,
            old_plan=previous_content,
            user_instruction=instruction,
            section=plan_section
        )
        
        await self._update_asset_content(asset_id, new_plan, "completed", {"modification_id": modification_id})
        await self._update_modification(modification_id, asset_id, previous_content, new_plan)
        
        return {"asset_id": asset_id, "asset_type": "plan", "section": plan_section}
    
    async def _get_asset(self, campaign_id: str, asset_type: str, day_number: int) -> Optional[Dict[str, Any]]:
        res = self.supabase_service.supabase.table("campaign_assets").select("*").eq("campaign_id", campaign_id).eq("asset_type", asset_type).eq("day_number", day_number).limit(1).execute()
        return (res.data or [None])[0]
    
    async def _version_asset(self, asset_id: str, prev_content: Dict[str, Any], generation_metadata: Dict[str, Any]):
        res = self.supabase_service.supabase.table("asset_versions").select("version_number").eq("asset_id", asset_id).order("version_number", desc=True).limit(1).execute()
        last = (res.data or [{"version_number": 0}])[0]["version_number"]
        self.supabase_service.supabase.table("asset_versions").insert({
            "asset_id": asset_id,
            "version_number": int(last) + 1,
            "content": prev_content,
            "generation_metadata": generation_metadata,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    
    async def _set_asset_status(self, asset_id: str, status: str, gen_meta: Dict[str, Any]):
        self.supabase_service.supabase.table("campaign_assets").update({
            "status": status,
            "generation_metadata": gen_meta,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", asset_id).execute()
    
    async def _update_asset_content(self, asset_id: str, new_content: Dict[str, Any], status: str, gen_meta: Dict[str, Any]):
        self.supabase_service.supabase.table("campaign_assets").update({
            "content": new_content,
            "status": status,
            "generation_metadata": gen_meta,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", asset_id).execute()
    
    async def _update_modification(self, modification_id: str, affected_asset_id: Optional[str], prev: Any, new: Any):
        self.supabase_service.supabase.table("canvas_modifications").update({
            "affected_asset_id": affected_asset_id,
            "previous_content": prev,
            "new_content": new
        }).eq("id", modification_id).execute()

# Global instance
_orchestrator_agent = None

def get_orchestrator_agent() -> OrchestratorAgent:
    """Get or create OrchestratorAgent instance"""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        _orchestrator_agent = OrchestratorAgent()
    return _orchestrator_agent