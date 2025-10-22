from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any
from datetime import datetime

from middleware.auth_middleware import get_current_user
from config.supabase_client import get_admin_supabase_client
from models.message import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    ConfirmExecuteRequest,
    ConfirmExecuteResponse
)
from agents.draft_agent import draft_agent
from agents.orchestrator_agent import get_orchestrator_agent
from services.supabase_service import SupabaseService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a chat message and receive AI response with updated draft.
    Uses Agno AI for intelligent strategy generation.
    """
    try:
        user_id = current_user["sub"]
        campaign_id = request.campaign_id
        
        print(f"\n🔵 === NEW MESSAGE REQUEST (Agno AI) ===")
        print(f"User ID: {user_id}")
        print(f"Campaign ID: {campaign_id}")
        print(f"Content: {request.message[:100]}...")
        
        # Initialize Supabase service with admin client
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        # 1. Verify campaign belongs to user
        print(f"🔍 Verifying campaign ownership...")
        campaign_result = supabase.table("campaigns").select("*").eq(
            "id", campaign_id
        ).eq("user_id", user_id).execute()
        
        if not campaign_result.data:
            print(f"❌ Campaign not found: {campaign_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign = campaign_result.data[0]
        print(f"✅ Campaign verified")
        
        # 2. Save user message
        print(f"💾 Saving user message...")
        user_message_data = {
            "campaign_id": campaign_id,
            "role": "user",
            "content": request.message,
            "created_at": datetime.utcnow().isoformat()
        }
        user_msg_result = supabase.table("chat_messages").insert(user_message_data).execute()
        user_message = user_msg_result.data[0]
        print(f"✅ User message saved: {user_message['id']}")
        
        # 3. Get conversation history
        print(f"📜 Fetching conversation history...")
        messages_result = supabase.table("chat_messages").select("*").eq(
            "campaign_id", campaign_id
        ).order("created_at", desc=False).execute()
        
        messages = messages_result.data
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages[:-1]  # Exclude the message we just added
        ]
        print(f"✅ Loaded {len(conversation_history)} previous messages")
        
        # 4. Generate or refine draft using Agno AI
        current_draft = campaign.get("draft_json")
        is_first_message = not current_draft or len(current_draft) == 0
        
        print(f"🤖 Using Agno AI (first_message: {is_first_message})...")
        
        if is_first_message:
            # Generate initial draft with Agno
            draft_json = await draft_agent.generate_initial_draft(
                initial_prompt=request.message,
                user_id=user_id
            )
            draft_updated = True
            print(f"✅ Initial draft generated with Agno: {draft_json.get('title', 'N/A')}")
        else:
            # Refine existing draft with Agno
            draft_json = await draft_agent.refine_draft(
                current_draft=current_draft,
                user_message=request.message,
                conversation_history=conversation_history
            )
            draft_updated = True
            print(f"✅ Draft refined with Agno")
        
        # 5. Generate conversational response using Agno's memory
        print(f"💬 Generating conversational response with Agno...")
        assistant_content = await draft_agent.generate_conversational_response(
            draft=draft_json,
            user_message=request.message,
            conversation_history=conversation_history,
            campaign_id=campaign_id  # Session ID for Agno's memory
        )
        print(f"✅ Response generated: {assistant_content[:100]}...")
        
        # 6. Update campaign with new draft
        new_status = "draft_ready" if draft_json else "drafting"
        
        print(f"💾 Updating campaign status to: {new_status}")
        supabase.table("campaigns").update({
            "draft_json": draft_json,
            "status": new_status,
            "title": draft_json.get("title", campaign["title"]),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", campaign_id).execute()
        print(f"✅ Campaign updated")
        
        # 7. Save assistant message
        print(f"💾 Saving assistant message...")
        assistant_message_data = {
            "campaign_id": campaign_id,
            "role": "assistant",
            "content": assistant_content,
            "metadata": {"draft_snapshot": draft_json},
            "created_at": datetime.utcnow().isoformat()
        }
        asst_msg_result = supabase.table("chat_messages").insert(assistant_message_data).execute()
        assistant_message = asst_msg_result.data[0]
        print(f"✅ Assistant message saved: {assistant_message['id']}")
        
        # 8. Return response
        print(f"✅ === MESSAGE PROCESSING COMPLETE (Agno AI) ===\n")
        
        return ChatResponse(
            message=MessageResponse(**assistant_message)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/confirm-execute", response_model=ConfirmExecuteResponse)
async def confirm_execute(
    request: ConfirmExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Confirm and execute campaign - triggers asset generation.
    This starts the orchestrator agent in the background.
    """
    try:
        supabase = get_admin_supabase_client()
        
        # Get campaign
        result = supabase.table("campaigns").select("*").eq(
            "id", request.campaign_id
        ).eq("user_id", current_user["sub"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign = result.data[0]
        
        # Verify campaign has a draft
        if not campaign.get("draft_json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign has no draft to execute"
            )
        
        # Save final_draft_json (snapshot of draft before execution)
        final_draft = campaign["draft_json"]
        
        supabase.table("campaigns").update({
            "final_draft_json": final_draft,
            "status": "executing",
            "execution_started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", request.campaign_id).execute()
        
        # Create confirmation message
        confirmation_msg = {
            "campaign_id": request.campaign_id,
            "role": "assistant",
            "content": "Perfect! I'm starting the asset generation now. This will take a few minutes...",
            "metadata": {"event": "execution_confirmed"},
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("chat_messages").insert(confirmation_msg).execute()
        
        # Start orchestrator agent in background
        orchestrator = get_orchestrator_agent()
        background_tasks.add_task(
            orchestrator.execute_campaign,
            request.campaign_id,
            final_draft
        )
        
        return ConfirmExecuteResponse(
            success=True,
            message="Asset generation started! You'll see progress updates in real-time.",
            campaign_id=request.campaign_id,
            status="executing"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in confirm-execute: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start execution: {str(e)}"
        )