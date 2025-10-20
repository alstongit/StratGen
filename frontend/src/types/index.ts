export interface User {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface Campaign {
  id: string
  user_id: string
  title: string
  initial_prompt: string
  status: 'drafting' | 'draft_ready' | 'executing' | 'completed' | 'failed'
  draft_json?: Record<string, any>
  final_draft_json?: Record<string, any>
  execution_started_at?: string
  execution_completed_at?: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  campaign_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: Record<string, any>
  created_at: string
}

export interface CampaignAsset {
  id: string
  campaign_id: string
  asset_type: 'image' | 'copy' | 'influencer' | 'plan'
  day_number?: number
  content: Record<string, any>
  status: 'pending' | 'generating' | 'completed' | 'failed'
  error_message?: string
  generation_metadata?: Record<string, any>
  created_at: string
  updated_at: string
}