import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { CanvasData } from '@/types';

export function useRealtimeCanvas(campaignId: string) {
  const [data, setData] = useState<CanvasData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!campaignId) return;

    // Subscribe to campaign_assets changes
    const channel = supabase
      .channel(`campaign_assets_${campaignId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'campaign_assets',
          filter: `campaign_id=eq.${campaignId}`
        },
        (payload) => {
          console.log('🔔 Asset updated:', payload);
          // Refetch canvas data when asset changes
          fetchCanvasData();
        }
      )
      .subscribe();

    async function fetchCanvasData() {
      // Call your existing canvas API
      // Update setData() with new data
    }

    fetchCanvasData();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [campaignId]);

  return { data, loading };
}