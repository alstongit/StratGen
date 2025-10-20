from fastapi import APIRouter, Depends, HTTPException, status
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
from services.supabase_service import SupabaseService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a chat message and receive AI response with updated draft.
    
    This endpoint:
    1. Saves user's message to database
    2. Loads conversation history
    3. Calls draft agent to generate/refine strategy
    4. Updates campaign draft_json
    5. Saves assistant's response
    6. Returns both messages
    """
    try:
        user_id = current_user["user_id"]
        campaign_id = request.campaign_id
        
        # Initialize Supabase service with admin client
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        # 1. Verify campaign belongs to user
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
        
        # 2. Save user message
        user_message = service.create_message(
            campaign_id=campaign_id,
            role="user",
            content=request.content
        )
        
        # 3. Get conversation history
        messages = service.get_campaign_messages(campaign_id)
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages[:-1]  # Exclude the message we just added
        ]
        
        # 4. Generate or refine draft
        current_draft = campaign.get("draft_json")
        is_first_message = current_draft is None
        
        if is_first_message:
            # Generate initial draft
            draft_json = await draft_agent.generate_initial_draft(
                initial_prompt=request.content,
                user_id=user_id
            )
            draft_updated = True
        else:
            # Refine existing draft
            draft_json = await draft_agent.refine_draft(
                current_draft=current_draft,
                user_message=request.content,
                conversation_history=conversation_history
            )
            draft_updated = True
        
        # 5. Generate conversational response
        assistant_content = await draft_agent.generate_conversational_response(
            draft=draft_json,
            user_message=request.content,
            conversation_history=conversation_history
        )
        
        # 6. Update campaign with new draft
        new_status = "draft_ready" if draft_json else "drafting"
        
        updated_campaign = service.update_campaign(
            campaign_id=campaign_id,
            updates={
                "draft_json": draft_json,
                "status": new_status,
                "title": draft_json.get("title", campaign["title"])
            }
        )
        
        # 7. Save assistant message
        assistant_message = service.create_message(
            campaign_id=campaign_id,
            role="assistant",
            content=assistant_content,
            metadata={"draft_snapshot": draft_json}
        )
        
        # 8. Return response
        return ChatResponse(
            user_message=MessageResponse(**user_message),
            assistant_message=MessageResponse(**assistant_message),
            draft_updated=draft_updated,
            campaign_status=new_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in send_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/confirm-execute", response_model=ConfirmExecuteResponse)
async def confirm_execute(
    request: ConfirmExecuteRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Confirm the draft and start campaign execution.
    
    This endpoint:
    1. Copies draft_json to final_draft_json
    2. Updates status to 'executing'
    3. Sets execution_started_at timestamp
    4. Triggers orchestrator (Phase 2)
    """
    try:
        user_id = current_user["user_id"]
        campaign_id = request.campaign_id
        
        # Initialize Supabase service
        supabase = get_admin_supabase_client()
        service = SupabaseService(supabase)
        
        # 1. Verify campaign
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
        
        if campaign["status"] != "draft_ready":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campaign is not ready to execute. Current status: {campaign['status']}"
            )
        
        if not campaign.get("draft_json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No draft found. Please create a strategy first."
            )
        
        # 2. Update campaign to executing status
        execution_started_at = datetime.utcnow()
        
        updated_campaign = service.update_campaign(
            campaign_id=campaign_id,
            updates={
                "final_draft_json": campaign["draft_json"],
                "status": "executing",
                "execution_started_at": execution_started_at.isoformat()
            }
        )
        
        # 3. TODO: Trigger orchestrator to generate assets (Phase 2)
        # from agents.orchestrator import orchestrator
        # await orchestrator.execute_campaign(campaign_id, campaign["draft_json"])
        
        # 4. Save system message
        service.create_message(
            campaign_id=campaign_id,
            role="system",
            content="Campaign execution started. Generating assets...",
            metadata={"event": "execution_started"}
        )
        
        return ConfirmExecuteResponse(
            campaign_id=campaign_id,
            status="executing",
            message="Campaign execution started successfully",
            execution_started_at=execution_started_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in confirm_execute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start campaign execution: {str(e)}"
        )