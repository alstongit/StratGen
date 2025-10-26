import { useCallback, useEffect, useRef, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { canvasAPI } from '@/lib/api';
import type { CanvasData } from '@/types';

interface UseRealtimeCanvasReturn {
  data: CanvasData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useRealtimeCanvas(campaignId?: string): UseRealtimeCanvasReturn {
  const [data, setData] = useState<CanvasData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // simple debounce so multiple row updates don't spam refetches
  const debounceTimer = useRef<number | null>(null);
  const isFetching = useRef(false);

  const refetch = useCallback(async () => {
    if (!campaignId) {
      setError('No campaign ID provided');
      setLoading(false);
      return;
    }
    try {
      isFetching.current = true;
      setError(null);
      const result = await canvasAPI.getCanvasData(campaignId);
      setData(result);
    } catch (e: any) {
      setError(e?.message || 'Failed to load canvas');
    } finally {
      setLoading(false);
      isFetching.current = false;
    }
  }, [campaignId]);

  useEffect(() => {
    if (!campaignId) {
      setError('No campaign ID provided');
      setLoading(false);
      return;
    }

    // initial fetch
    refetch();

    // subscribe to changes in campaign_assets for this campaign
    const channel = supabase
      .channel(`campaign_assets_${campaignId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'campaign_assets',
          filter: `campaign_id=eq.${campaignId}`,
        },
        () => {
          // debounce refetch
          if (debounceTimer.current) window.clearTimeout(debounceTimer.current);
          debounceTimer.current = window.setTimeout(() => {
            if (!isFetching.current) refetch();
          }, 300);
        }
      )
      .subscribe();

    return () => {
      if (debounceTimer.current) window.clearTimeout(debounceTimer.current);
      supabase.removeChannel(channel);
    };
  }, [campaignId, refetch]);

  return { data, loading, error, refetch };
}