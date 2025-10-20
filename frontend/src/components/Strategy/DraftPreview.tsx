import type { Campaign } from '../../types'
import { 
  Users, 
  Palette, 
  Share2, 
  Calendar, 
  Lightbulb,
  Target,
  CheckCircle2,
  Clock
} from 'lucide-react'

interface DraftPreviewProps {
  campaign: Campaign
}

export const DraftPreview = ({ campaign }: DraftPreviewProps) => {
  const draft = campaign.draft_json

  if (!draft) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center max-w-md px-6">
          <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Target className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Draft Yet
          </h3>
          <p className="text-gray-600 text-sm">
            Start chatting to create your campaign strategy. I'll generate a comprehensive 
            draft based on your requirements.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{draft.title}</h2>
              <p className="text-sm text-gray-500 mt-1">Campaign Strategy Draft</p>
            </div>
            {campaign.status === 'draft_ready' && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Ready to Execute
              </span>
            )}
          </div>
        </div>

        {/* Target Audience */}
        {draft.target_audience && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Target Audience</h3>
            </div>
            <p className="text-gray-700">{draft.target_audience}</p>
          </div>
        )}

        {/* Color Scheme */}
        {draft.color_scheme && draft.color_scheme.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Palette className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Color Scheme</h3>
            </div>
            <div className="flex gap-3">
              {draft.color_scheme.map((color: string, index: number) => (
                <div key={index} className="flex flex-col items-center gap-2">
                  <div
                    className="w-16 h-16 rounded-lg shadow-md border-2 border-white"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs font-mono text-gray-600">{color}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Platforms */}
        {draft.platforms && draft.platforms.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Share2 className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Platforms</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {draft.platforms.map((platform: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium capitalize"
                >
                  {platform}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Posting Schedule */}
        {draft.posting_schedule && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Posting Schedule</h3>
            </div>
            <div className="space-y-3">
              {Object.entries(draft.posting_schedule).map(([day, details]: [string, any]) => (
                <div
                  key={day}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {day.replace('day_', '')}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">
                        {details.time}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 capitalize">
                      {details.content_type}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Themes */}
        {draft.content_themes && draft.content_themes.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Content Themes</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {draft.content_themes.map((theme: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium capitalize"
                >
                  {theme}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Additional Details */}
        {draft.additional_details && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Additional Details</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{draft.additional_details}</p>
          </div>
        )}
      </div>
    </div>
  )
}