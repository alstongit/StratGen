import { useEffect, useState, useCallback, useRef } from 'react'
import { supabase } from '../lib/supabase'
import api from '../lib/api'
import type { Campaign, ChatMessage, CampaignAsset } from '../types'
import type { RealtimeChannel } from '@supabase/supabase-js'

interface UseRealtimeCampaignReturn {
  campaign: Campaign | null
  messages: ChatMessage[]
  assets: CampaignAsset[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  isRealtimeConnected: boolean
}

export const useRealtimeCampaign = (campaignId: string): UseRealtimeCampaignReturn => {
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [assets, setAssets] = useState<CampaignAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRealtimeConnected, setIsRealtimeConnected] = useState(false)
  const channelRef = useRef<RealtimeChannel | null>(null)

  const fetchData = useCallback(async () => {
    if (!campaignId) return

    try {
      console.log('🔄 Fetching campaign data for:', campaignId)
      setLoading(true)
      setError(null)

      // Fetch campaign via API (backend handles auth)
      const campaignResponse = await api.get(`/campaigns/${campaignId}`)
      console.log('✅ Campaign loaded:', campaignResponse.data.title)
      setCampaign(campaignResponse.data)

      // Fetch messages via API (more reliable than Supabase direct with RLS disabled)
      console.log('📬 Fetching messages...')
      const messagesResponse = await api.get(`/campaigns/${campaignId}/messages`)
      console.log(`✅ Loaded ${messagesResponse.data?.length || 0} messages`)
      setMessages(messagesResponse.data || [])

      // Fetch assets directly from Supabase (fewer assets, less critical)
      console.log('📦 Fetching assets...')
      const { data: assetsData, error: assetsError } = await supabase
        .from('campaign_assets')
        .select('*')
        .eq('campaign_id', campaignId)
        .order('created_at', { ascending: true })

      if (assetsError) {
        console.error('❌ Error fetching assets:', assetsError)
        setAssets([])
      } else {
        console.log(`✅ Loaded ${assetsData?.length || 0} assets`)
        setAssets(assetsData || [])
      }

    } catch (err: any) {
      console.error('❌ Error fetching campaign data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load campaign')
    } finally {
      setLoading(false)
    }
  }, [campaignId])

  useEffect(() => {
    if (!campaignId) return
    
    console.log('🚀 Initializing campaign:', campaignId)
    fetchData()

    // Try to set up realtime, but don't fail if it doesn't work
    try {
      console.log('📡 Attempting to connect to realtime...')
      
      const channel = supabase
        .channel(`campaign_${campaignId}`, {
          config: {
            broadcast: { self: false },
            presence: { key: campaignId }
          }
        })
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'campaigns',
            filter: `id=eq.${campaignId}`,
          },
          (payload) => {
            console.log('📢 Campaign UPDATE received')
            if (payload.new) {
              setCampaign(payload.new as Campaign)
            }
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
            console.log('📢 Message INSERT received')
            if (payload.new) {
              const newMessage = payload.new as ChatMessage
              setMessages((prev) => {
                if (prev.some(m => m.id === newMessage.id)) {
                  console.log('⚠️ Duplicate message, skipping')
                  return prev
                }
                console.log('✅ Adding message to state')
                return [...prev, newMessage]
              })
            }
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
            console.log('📢 Asset event received:', payload.eventType)
            if (payload.eventType === 'INSERT' && payload.new) {
              setAssets((prev) => {
                if (prev.some(a => a.id === payload.new.id)) return prev
                return [...prev, payload.new as CampaignAsset]
              })
            } else if (payload.eventType === 'UPDATE' && payload.new) {
              setAssets((prev) =>
                prev.map((asset) =>
                  asset.id === payload.new.id ? (payload.new as CampaignAsset) : asset
                )
              )
            } else if (payload.eventType === 'DELETE' && payload.old) {
              setAssets((prev) => prev.filter((asset) => asset.id !== payload.old.id))
            }
          }
        )
        .subscribe((status, err) => {
          console.log('📡 Realtime status:', status)
          if (err) {
            console.error('❌ Realtime error:', err)
            setIsRealtimeConnected(false)
            // Don't throw error, just log it
          } else if (status === 'SUBSCRIBED') {
            console.log('✅ Realtime connected')
            setIsRealtimeConnected(true)
          } else if (status === 'CLOSED') {
            console.log('🔌 Realtime connection closed')
            setIsRealtimeConnected(false)
          }
        })

      channelRef.current = channel
    } catch (realtimeError) {
      console.error('❌ Failed to set up realtime (will use polling):', realtimeError)
      setIsRealtimeConnected(false)
    }

    // Cleanup
    return () => {
      if (channelRef.current) {
        console.log('🔌 Unsubscribing from realtime')
        supabase.removeChannel(channelRef.current)
        channelRef.current = null
      }
    }
  }, [campaignId, fetchData])

  // Polling fallback if realtime fails (every 3 seconds)
  useEffect(() => {
    if (!campaignId || isRealtimeConnected) return

    console.log('🔄 Realtime not connected, using polling fallback')
    const interval = setInterval(() => {
      console.log('⏰ Polling for updates...')
      fetchData()
    }, 3000)

    return () => clearInterval(interval)
  }, [campaignId, isRealtimeConnected, fetchData])

  return {
    campaign,
    messages,
    assets,
    loading,
    error,
    refetch: fetchData,
    isRealtimeConnected,
  }
}