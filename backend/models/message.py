from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

# ==================== CAMPAIGN MODELS ====================

class CreateCampaignRequest(BaseModel):
    title: str
    initial_prompt: str

class Campaign(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    draft_json: Optional[Dict[str, Any]] = None
    final_draft_json: Optional[Dict[str, Any]] = None
    execution_started_at: Optional[str] = None
    execution_completed_at: Optional[str] = None
    created_at: str
    updated_at: str

# ==================== CHAT MODELS ====================

class ChatRequest(BaseModel):
    campaign_id: str
    message: str

class MessageResponse(BaseModel):
    id: str
    campaign_id: str
    role: str
    content: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: MessageResponse

# ==================== EXECUTION MODELS ====================

class ConfirmExecuteRequest(BaseModel):
    campaign_id: str

class ConfirmExecuteResponse(BaseModel):
    success: bool
    message: str
    campaign_id: str
    status: str