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

// Add Message type (alias for ChatMessage for compatibility)
export interface Message {
  id: string
  campaign_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: Record<string, any>
  created_at: string
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
  asset_type: 'copy' | 'image' | 'influencer' | 'plan'
  day_number: number | null
  content: any
  status: 'pending' | 'generating' | 'completed' | 'failed'
  error_message?: string
  generation_metadata?: any
  created_at: string
  updated_at: string
}

export interface DayPost {
  day_number: number
  copy: CampaignAsset | null
  image: CampaignAsset | null
}

export interface Influencer {
  name: string
  handle: string
  platform: string
  followers: string
  engagement_rate?: string
  relevance_score: number
  profile_url: string
  bio: string
  why: string
  contact?: string
}

export interface ExecutionPlan {
  phases: Array<{
    name: string
    duration: string
    steps: string[]
  }>;
  timeline: string
  checklist: Array<{
    task: string
    completed: boolean
    priority: 'high' | 'medium' | 'low'
  }>;
  key_milestones: string[]
  success_metrics: string[]
  recommendations: string
}

export interface CanvasData {
  campaign: Campaign
  posts: DayPost[]
  influencers: CampaignAsset[]
  plan: CampaignAsset | null
  stats: {
    total_posts: number
    total_influencers: number
    status: string
    execution_time: number
  }
}