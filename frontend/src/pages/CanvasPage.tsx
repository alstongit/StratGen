import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { CanvasData } from '@/types';
import { PostCard } from '@/components/Canvas/PostCard';
import { InfluencerCard } from '@/components/Canvas/InfluencerCard';
import { ExecutionPlanCard } from '@/components/Canvas/ExecutionPlanCard';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import CanvasChatBar from '@/components/Canvas/CanvasChatBar';
import { useRealtimeCanvas } from '@/hooks/useRealtimeCanvas';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { supabase } from '@/lib/supabase';  // Import supabase client

export default function CanvasPage() {
  const { campaignId } = useParams<{ campaignId: string }>();
  const navigate = useNavigate();

  const { data, loading, error, refetch } = useRealtimeCanvas(campaignId);

  const [automationStatus, setAutomationStatus] = useState<"idle" | "running" | "completed" | "failed">("idle");

  const handleInstagramAutomation = async () => {
    try {
      setAutomationStatus("running");
      
      // Get current session token from Supabase
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      console.log("🔍 Session check:", { session: !!session, error: sessionError });
      
      if (sessionError || !session) {
        console.error("❌ No valid session:", sessionError);
        throw new Error("Not authenticated. Please log in again.");
      }
      
      console.log("🔑 Using access token:", session.access_token.substring(0, 20) + "...");
      
      const response = await fetch(
        `http://localhost:8000/canvas/${campaignId}/automate-instagram`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${session.access_token}`  // Use session token
          }
        }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("❌ Automation request failed:", errorData);
        throw new Error(errorData.detail || "Failed to start automation");
      }
      
      const result = await response.json();
      console.log("✅ Automation started:", result);
      
      // Poll for completion (check scheduled_posts table)
      const pollInterval = setInterval(async () => {
        // Get fresh session for polling
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        
        if (!currentSession) {
          console.error("❌ Lost session during polling");
          clearInterval(pollInterval);
          setAutomationStatus("failed");
          return;
        }
        
        const statusRes = await fetch(
          `http://localhost:8000/canvas/${campaignId}/scheduled-posts`,
          {
            headers: {
              "Authorization": `Bearer ${currentSession.access_token}`
            }
          }
        );
        
        if (!statusRes.ok) {
          console.error("❌ Failed to fetch scheduled posts status");
          clearInterval(pollInterval);
          setAutomationStatus("failed");
          return;
        }
        
        const statusData = await statusRes.json();
        console.log("📊 Polling status:", statusData);
        
        const allPosted = statusData.posts.every((p: any) => 
          p.status === "posted" || p.status === "failed"
        );
        
        if (allPosted && statusData.posts.length > 0) {
          const anyFailed = statusData.posts.some((p: any) => p.status === "failed");
          setAutomationStatus(anyFailed ? "failed" : "completed");
          clearInterval(pollInterval);
          console.log("✅ Automation completed:", { failed: anyFailed });
        }
      }, 5000);
      
    } catch (error) {
      console.error("❌ Automation failed:", error);
      setAutomationStatus("failed");
      alert(`Automation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
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

  const { campaign, posts, influencers, plan, stats } = data as CanvasData;

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

            <div className="flex items-center gap-4">
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

              {/* Automate Instagram Button in Header */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <span>📸 Automate Instagram</span>
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Automate Instagram Posting</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      This will automatically post all {posts.length} campaign posts to Instagram using Selenium automation.
                    </p>
                    
                    {automationStatus === "idle" && (
                      <Button onClick={handleInstagramAutomation} className="w-full">
                        Start Automation
                      </Button>
                    )}
                    
                    {automationStatus === "running" && (
                      <div className="text-center py-4">
                        <div className="animate-pulse h-8 w-8 bg-primary rounded-full mx-auto mb-2" />
                        <p className="text-sm font-medium">Posting to Instagram...</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          This may take several minutes (5 min delay between posts)
                        </p>
                      </div>
                    )}
                    
                    {automationStatus === "completed" && (
                      <div className="text-center py-4 text-green-600">
                        <div className="text-4xl mb-2">✅</div>
                        <p className="font-medium">All posts published successfully!</p>
                        <Button 
                          onClick={() => setAutomationStatus("idle")} 
                          variant="outline" 
                          className="mt-2"
                        >
                          Close
                        </Button>
                      </div>
                    )}
                    
                    {automationStatus === "failed" && (
                      <div className="text-center py-4 text-red-600">
                        <div className="text-4xl mb-2">❌</div>
                        <p className="font-medium">Automation failed</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Check console for details
                        </p>
                        <Button onClick={() => setAutomationStatus("idle")} variant="outline" className="mt-2">
                          Try Again
                        </Button>
                      </div>
                    )}
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>

      {/* Main - posts grid + influencer column */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:flex lg:items-start lg:gap-8">
          {/* Posts column */}
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

          {/* Influencers column */}
          <aside className="mt-8 lg:mt-0 lg:w-[420px] flex-shrink-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Influencers ({influencers.length})</h3>
            <div className="bg-white rounded-lg border overflow-hidden">
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
        <div className="mt-10 mb-20">
          <ExecutionPlanCard asset={plan} />
        </div>
      </div>

      {campaignId && (
        <CanvasChatBar
          campaignId={campaignId}
          onUpdated={() => {
            refetch();
          }}
        />
      )}
    </div>
  );
}