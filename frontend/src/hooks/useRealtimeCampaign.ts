import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { campaignsAPI } from '@/lib/api'
import type { Campaign, Message } from '@/types'

interface UseRealtimeCampaignReturn {
  campaign: Campaign | null
  messages: Message[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useRealtimeCampaign(campaignId: string): UseRealtimeCampaignReturn {
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCampaign = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [campaignData, messagesData] = await Promise.all([
        campaignsAPI.getCampaign(campaignId),
        campaignsAPI.getCampaignMessages(campaignId)
      ])
      
      setCampaign(campaignData)
      setMessages(messagesData)
    } catch (err) {
      console.error('Error fetching campaign:', err)
      setError(err instanceof Error ? err.message : 'Failed to load campaign')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!campaignId) return

    fetchCampaign()

    // Subscribe to campaign updates
    const campaignChannel = supabase
      .channel(`campaign:${campaignId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'campaigns',
          filter: `id=eq.${campaignId}`,
        },
        (payload) => {
          console.log('🔔 Campaign updated:', payload)
          if (payload.new) {
            setCampaign(payload.new as Campaign)
          }
        }
      )
      .subscribe()

    // Subscribe to new messages
    const messagesChannel = supabase
      .channel(`messages:${campaignId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages',
          filter: `campaign_id=eq.${campaignId}`,
        },
        (payload) => {
          console.log('🔔 New message:', payload)
          if (payload.new) {
            setMessages((prev) => [...prev, payload.new as Message])
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(campaignChannel)
      supabase.removeChannel(messagesChannel)
    }
  }, [campaignId])

  return {
    campaign,
    messages,
    loading,
    error,
    refetch: fetchCampaign,
  }
}