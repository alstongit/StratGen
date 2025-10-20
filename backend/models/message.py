from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class MessageCreate(BaseModel):
    campaign_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: str
    campaign_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class ChatRequest(BaseModel):
    campaign_id: str
    content: str

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    draft_updated: bool
    campaign_status: str

class ConfirmExecuteRequest(BaseModel):
    campaign_id: str

class ConfirmExecuteResponse(BaseModel):
    campaign_id: str
    status: str
    message: str
    execution_started_at: datetime