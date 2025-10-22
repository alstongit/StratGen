import type { CampaignAsset } from '@/types';
import { Card } from '@/components/ui/card';
import { ExternalLink, Instagram, Twitter, Youtube, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface InfluencerCardProps {
  asset: CampaignAsset;
}

export function InfluencerCard({ asset }: InfluencerCardProps) {
  const influencer = asset.content || {};

  const getPlatformIcon = (platform: string | undefined) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('instagram')) return <Instagram className="w-4 h-4" />;
    if (p.includes('twitter') || p.includes('x')) return <Twitter className="w-4 h-4" />;
    if (p.includes('youtube')) return <Youtube className="w-4 h-4" />;
    return <Globe className="w-4 h-4" />;
  };

  const getPlatformColor = (platform: string | undefined) => {
    const p = (platform || '').toLowerCase();
    if (p.includes('instagram')) return 'bg-pink-50 text-pink-700';
    if (p.includes('twitter') || p.includes('x')) return 'bg-blue-50 text-blue-700';
    if (p.includes('youtube')) return 'bg-red-50 text-red-700';
    return 'bg-gray-50 text-gray-700';
  };

  return (
    <Card className="p-3 hover:shadow-sm transition-shadow" style={{ height: 120 }}>
      <div className="flex items-start gap-3 h-full">
        <div className={`p-2 rounded-lg flex items-center justify-center ${getPlatformColor(influencer.platform)}`} style={{ minWidth: 44 }}>
          {getPlatformIcon(influencer.platform)}
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm text-gray-900 truncate">{influencer.name || 'Unknown'}</h4>
          {influencer.handle && <p className="text-xs text-gray-500 mb-1">@{influencer.handle}</p>}
          {influencer.description && <p className="text-xs text-gray-700 line-clamp-2 mb-2">{influencer.description}</p>}

          <div className="flex items-center gap-2">
            <Button variant="outline" className="text-xs" onClick={() => influencer.profile_url && window.open(influencer.profile_url, '_blank')}>
              Visit
            </Button>
            {typeof influencer.relevance_score === 'number' && (
              <div className="ml-auto text-xs text-gray-600">Score: {Math.round(influencer.relevance_score)}</div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}