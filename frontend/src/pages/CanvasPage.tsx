import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { canvasAPI } from '@/lib/api';
import type { CanvasData } from '@/types';
import { PostCard } from '@/components/Canvas/PostCard';
import { InfluencerCard } from '@/components/Canvas/InfluencerCard';
import { ExecutionPlanCard } from '@/components/Canvas/ExecutionPlanCard';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, AlertCircle, FileDown } from 'lucide-react';

export default function CanvasPage() {
  const { campaignId } = useParams<{ campaignId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<CanvasData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (campaignId) loadCanvasData(campaignId);
    else {
      setError('No campaign ID provided');
      setLoading(false);
    }
  }, [campaignId]);

  const loadCanvasData = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const canvasData = await canvasAPI.getCanvasData(id);
      setData(canvasData);
    } catch (err: any) {
      setError(err?.message || 'Failed to load canvas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading campaign assets...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Canvas</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">No canvas data available</p>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const { campaign, posts, influencers, plan, stats } = data;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{campaign.title}</h1>
                <p className="text-sm text-gray-600">
                  Status: <span className="font-medium capitalize">{stats.status}</span>
                  {stats.execution_time > 0 && <> • Generated in {stats.execution_time.toFixed(1)}s</>}
                </p>
              </div>
            </div>

            <div className="flex gap-6 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.total_posts}</div>
                <div className="text-gray-600">Posts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.total_influencers}</div>
                <div className="text-gray-600">Influencers</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main - posts grid + influencer column */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:flex lg:items-start lg:gap-8">
          {/* Posts column - center, grid 2 per row on md+; cards smaller so two can sit side-by-side */}
          <div className="lg:flex-1 lg:mx-auto w-full max-w-4xl">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Content Calendar ({posts.length})</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {posts.length > 0 ? (
                posts.map((post) => <PostCard key={post.day_number} post={post} />)
              ) : (
                <div className="bg-white rounded-lg border p-8 text-center col-span-full">
                  <p className="text-gray-500">No posts generated yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Influencers column - increased width so more cards fit; taller scroll area */}
          <aside className="mt-8 lg:mt-0 lg:w-[420px] flex-shrink-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Influencers ({influencers.length})</h3>
            <div className="bg-white rounded-lg border overflow-hidden">
              {/* taller so ~3+ compact influencer cards are visible at once */}
              <div className="h-[640px] overflow-y-auto p-3 space-y-3">
                {influencers.length > 0 ? (
                  influencers.map((asset) => <InfluencerCard key={asset.id} asset={asset} />)
                ) : (
                  <div className="p-4 text-sm text-gray-500">No influencers found yet</div>
                )}
              </div>
            </div>
          </aside>
        </div>

        {/* Execution plan below full width */}
        <div className="mt-10">
          <ExecutionPlanCard asset={plan} />
        </div>
      </div>
    </div>
  );
}