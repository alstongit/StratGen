import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { Campaign, ChatMessage, CampaignAsset } from '../types'

interface UseRealtimeCampaignReturn {
  campaign: Campaign | null
  messages: ChatMessage[]
  assets: CampaignAsset[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export const useRealtimeCampaign = (campaignId: string): UseRealtimeCampaignReturn => {
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [assets, setAssets] = useState<CampaignAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch campaign
      const { data: campaignData, error: campaignError } = await supabase
        .from('campaigns')
        .select('*')
        .eq('id', campaignId)
        .single()

      if (campaignError) throw campaignError
      setCampaign(campaignData)

      // Fetch messages
      const { data: messagesData, error: messagesError } = await supabase
        .from('chat_messages')
        .select('*')
        .eq('campaign_id', campaignId)
        .order('created_at', { ascending: true })

      if (messagesError) throw messagesError
      setMessages(messagesData || [])

      // Fetch assets
      const { data: assetsData, error: assetsError } = await supabase
        .from('campaign_assets')
        .select('*')
        .eq('campaign_id', campaignId)
        .order('created_at', { ascending: true })

      if (assetsError) throw assetsError
      setAssets(assetsData || [])

    } catch (err: any) {
      setError(err.message)
      console.error('Error fetching campaign data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()

    // Subscribe to campaign updates
    const campaignChannel = supabase
      .channel(`campaign_${campaignId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'campaigns',
          filter: `id=eq.${campaignId}`,
        },
        (payload) => {
          console.log('Campaign updated:', payload)
          setCampaign(payload.new as Campaign)
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages',
          filter: `campaign_id=eq.${campaignId}`,
        },
        (payload) => {
          console.log('New message:', payload)
          setMessages((prev) => [...prev, payload.new as ChatMessage])
        }
      )
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'campaign_assets',
          filter: `campaign_id=eq.${campaignId}`,
        },
        (payload) => {
          console.log('Asset updated:', payload)
          if (payload.eventType === 'INSERT') {
            setAssets((prev) => [...prev, payload.new as CampaignAsset])
          } else if (payload.eventType === 'UPDATE') {
            setAssets((prev) =>
              prev.map((asset) =>
                asset.id === payload.new.id ? (payload.new as CampaignAsset) : asset
              )
            )
          } else if (payload.eventType === 'DELETE') {
            setAssets((prev) => prev.filter((asset) => asset.id !== payload.old.id))
          }
        }
      )
      .subscribe()

    // Cleanup subscription
    return () => {
      supabase.removeChannel(campaignChannel)
    }
  }, [campaignId])

  return {
    campaign,
    messages,
    assets,
    loading,
    error,
    refetch: fetchData,
  }
}