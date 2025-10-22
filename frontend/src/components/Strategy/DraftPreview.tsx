import type { Campaign } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Calendar, 
  Target, 
  Users, 
  TrendingUp, 
  Palette,
  MessageSquare,
  CheckCircle
} from 'lucide-react';

interface DraftPreviewProps {
  campaign: Campaign;
}

export function DraftPreview({ campaign }: DraftPreviewProps) {
  const draft = campaign.draft_json;

  if (!draft || Object.keys(draft).length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 p-8">
        <div className="text-center max-w-md">
          <div className="bg-gray-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Draft Yet
          </h3>
          <p className="text-gray-600">
            Start chatting to generate your campaign strategy. 
            Your draft will appear here in real-time.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 text-green-600 mb-2">
            <CheckCircle className="w-5 h-5" />
            <span className="text-sm font-medium">Draft Ready</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {draft.title || 'Campaign Draft'}
          </h2>
        </div>

        {/* Target Audience */}
        {draft.target_audience && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Target Audience
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{draft.target_audience}</p>
            </CardContent>
          </Card>
        )}

        {/* Platforms */}
        {draft.platforms && Array.isArray(draft.platforms) && draft.platforms.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Platforms
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {draft.platforms.map((platform: string, idx: number) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm capitalize"
                  >
                    {platform}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Posting Schedule */}
        {draft.posting_schedule && Object.keys(draft.posting_schedule).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Posting Schedule
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(draft.posting_schedule).map(([day, details]) => {
                  const schedule = details as any;
                  return (
                    <div key={day} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900 capitalize">
                          {day.replace('_', ' ')}
                        </h4>
                        {schedule.time && (
                          <span className="text-sm text-gray-600">{schedule.time}</span>
                        )}
                      </div>
                      {schedule.content_type && (
                        <p className="text-sm text-gray-700 capitalize">
                          Type: {schedule.content_type}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content Themes */}
        {draft.content_themes && Array.isArray(draft.content_themes) && draft.content_themes.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Content Themes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {draft.content_themes.map((theme: string, idx: number) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                  >
                    {theme}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Color Scheme */}
        {draft.color_scheme && Array.isArray(draft.color_scheme) && draft.color_scheme.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="w-5 h-5" />
                Color Scheme
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3">
                {draft.color_scheme.map((color: string, idx: number) => (
                  <div key={idx} className="flex flex-col items-center gap-2">
                    <div
                      className="w-16 h-16 rounded-lg border-2 border-gray-200 shadow-sm"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs text-gray-600 font-mono">{color}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Additional Details */}
        {draft.additional_details && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Additional Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 whitespace-pre-wrap">{draft.additional_details}</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}