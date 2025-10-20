import type { Campaign } from '../../types'
import { 
  Users, 
  Palette, 
  Share2, 
  Calendar, 
  Lightbulb,
  Target,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react'
import { useEffect, useState } from 'react'

interface DraftPreviewProps {
  campaign: Campaign
}

export const DraftPreview = ({ campaign }: DraftPreviewProps) => {
  const [showUpdateAnimation, setShowUpdateAnimation] = useState(false)
  const draft = campaign.draft_json

  // Trigger animation when draft changes
  useEffect(() => {
    if (draft) {
      setShowUpdateAnimation(true)
      const timer = setTimeout(() => setShowUpdateAnimation(false), 2000)
      return () => clearTimeout(timer)
    }
  }, [draft])

  if (!draft) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-gray-50 to-gray-100">
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
      {/* Update Indicator */}
      {showUpdateAnimation && (
        <div className="sticky top-0 z-10 bg-indigo-600 text-white px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 animate-pulse">
          <Sparkles className="w-4 h-4" />
          Draft updated!
        </div>
      )}

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
            <p className="text-gray-700 leading-relaxed">{draft.target_audience}</p>
          </div>
        )}

        {/* Color Scheme */}
        {draft.color_scheme && draft.color_scheme.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Palette className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Color Scheme</h3>
            </div>
            <div className="flex flex-wrap gap-3">
              {draft.color_scheme.map((color: string, index: number) => (
                <div key={index} className="flex flex-col items-center gap-2">
                  <div
                    className="w-20 h-20 rounded-lg shadow-md border-2 border-white ring-1 ring-gray-200"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs font-mono text-gray-600 font-semibold">{color}</span>
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
                  className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium capitalize border border-indigo-100"
                >
                  {platform}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Posting Schedule */}
        {draft.posting_schedule && Object.keys(draft.posting_schedule).length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Posting Schedule</h3>
            </div>
            <div className="space-y-3">
              {Object.entries(draft.posting_schedule).map(([day, details]: [string, any]) => (
                <div
                  key={day}
                  className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-indigo-600" />
                    <h4 className="text-base font-bold text-gray-900 capitalize">
                      {day.replace(/_/g, ' ')}
                    </h4>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Clock className="w-4 h-4 text-indigo-600" />
                    <span className="font-semibold">{details.time}</span>
                    <span className="text-gray-500">•</span>
                    <span className="capitalize">{details.content_type}</span>
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
                  className="px-4 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium border border-purple-100"
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
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{draft.additional_details}</p>
          </div>
        )}
      </div>
    </div>
  )
}