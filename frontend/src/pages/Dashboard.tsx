import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { campaignsAPI } from '@/lib/api';
import type { Campaign } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Loader2, Trash2, Calendar, CheckCircle, Clock } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const data = await campaignsAPI.getCampaigns();
      setCampaigns(data);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = async () => {
    setCreating(true);
    try {
      // Create campaign with placeholder title
      const campaign = await campaignsAPI.createCampaign(
        `Campaign ${new Date().toLocaleDateString()}`,
        '' // Empty initial prompt
      );
      
      // Navigate immediately to strategy page
      navigate(`/strategy/${campaign.id}`);
    } catch (error) {
      console.error('Failed to create campaign:', error);
      alert('Failed to create campaign');
      setCreating(false);
    }
  };

  const handleCampaignClick = (campaign: Campaign) => {
    if (campaign.status === 'completed' || campaign.status === 'executing') {
      navigate(`/canvas/${campaign.id}`);
    } else {
      navigate(`/strategy/${campaign.id}`);
    }
  };

  const handleDeleteCampaign = async (e: React.MouseEvent, campaignId: string) => {
    e.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this campaign?')) {
      try {
        await campaignsAPI.deleteCampaign(campaignId);
        setCampaigns(campaigns.filter(c => c.id !== campaignId));
      } catch (error) {
        console.error('Failed to delete campaign:', error);
        alert('Failed to delete campaign');
      }
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      drafting: { color: 'bg-gray-100 text-gray-800', icon: Clock, label: 'Drafting' },
      draft_ready: { color: 'bg-yellow-100 text-yellow-800', icon: CheckCircle, label: 'Draft Ready' },
      executing: { color: 'bg-blue-100 text-blue-800', icon: Loader2, label: 'Generating...' },
      completed: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Completed' },
      failed: { color: 'bg-red-100 text-red-800', icon: Clock, label: 'Failed' }
    };
    
    const badge = badges[status as keyof typeof badges] || badges.drafting;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className={`w-3 h-3 ${status === 'executing' ? 'animate-spin' : ''}`} />
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Campaigns</h1>
            <p className="text-gray-600 mt-1">Create and manage your marketing campaigns</p>
          </div>
          <Button 
            onClick={handleCreateCampaign} 
            className="gap-2"
            disabled={creating}
          >
            {creating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" />
                New Campaign
              </>
            )}
          </Button>
        </div>

        {/* Campaigns Grid */}
        {campaigns.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <div className="text-gray-400 mb-4">
                <Calendar className="w-16 h-16 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No campaigns yet</h3>
              <p className="text-gray-600 mb-6">Get started by creating your first campaign</p>
              <Button onClick={handleCreateCampaign} className="gap-2" disabled={creating}>
                {creating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Create Campaign
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign) => (
              <Card
                key={campaign.id}
                className="hover:shadow-lg transition-shadow cursor-pointer group"
                onClick={() => handleCampaignClick(campaign)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{campaign.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2">
                        {getStatusBadge(campaign.status)}
                      </CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => handleDeleteCampaign(e, campaign.id)}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>Created {new Date(campaign.created_at).toLocaleDateString()}</span>
                    </div>
                    {campaign.status === 'completed' && (
                      <div className="mt-2 pt-2 border-t">
                        <span className="text-xs text-green-600 font-medium">
                          ✓ View assets on canvas
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}