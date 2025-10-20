import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRealtimeCampaign } from '../hooks/useRealtimeCampaign'
import { ChatInterface } from '../components/Strategy/ChatInterface'
import { DraftPreview } from '../components/Strategy/DraftPreview'
import { ConfirmExecuteModal } from '../components/Strategy/ConfirmExecuteModal'
import { Button } from '../components/ui/button'
import { ArrowLeft, Rocket, Loader2, X, MessageSquare, FileText } from 'lucide-react'
import api from '../lib/api'

export const StrategyPage = () => {
  const { campaignId } = useParams<{ campaignId: string }>()
  const navigate = useNavigate()
  const { campaign, messages, loading, error, refetch } = useRealtimeCampaign(campaignId!)
  
  const [isLoadingMessage, setIsLoadingMessage] = useState(false)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'chat' | 'draft'>('chat')

  const handleSendMessage = async (content: string) => {
    if (!campaignId) return

    setIsLoadingMessage(true)
    setApiError(null)

    try {
      console.log('📤 Sending message:', content)
      
      const response = await api.post('/chat/message', {
        campaign_id: campaignId,
        content,
      })
      
      console.log('✅ Message sent successfully:', response.data)
      
      // Manually refetch to get the latest data
      await refetch()
      
      // Switch to draft tab to show updates
      if (response.data.draft_updated) {
        setTimeout(() => setActiveTab('draft'), 500)
      }
      
    } catch (error: any) {
      console.error('❌ Error sending message:', error)
      console.error('Error details:', error.response?.data)
      setApiError(error.response?.data?.detail || 'Failed to send message')
    } finally {
      setIsLoadingMessage(false)
    }
  }

  const handleConfirmExecute = async () => {
    if (!campaignId) return

    try {
      setApiError(null)
      await api.post('/chat/confirm-execute', {
        campaign_id: campaignId,
      })
      
      setShowConfirmModal(false)
      
      // Navigate to canvas page after short delay
      setTimeout(() => {
        navigate(`/canvas/${campaignId}`)
      }, 1500)
    } catch (error: any) {
      console.error('Error executing campaign:', error)
      setApiError(error.response?.data?.detail || 'Failed to execute campaign')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading campaign...</p>
        </div>
      </div>
    )
  }

  if (error || !campaign) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Campaign Not Found
          </h3>
          <p className="text-gray-600 mb-4">{error || 'Could not load campaign'}</p>
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  const isDraftReady = campaign.status === 'draft_ready'
  const isExecuting = campaign.status === 'executing'

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Bar */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{campaign.title}</h1>
              <p className="text-sm text-gray-500">Strategy Development</p>
            </div>
          </div>

          {isDraftReady && !isExecuting && (
            <Button
              onClick={() => setShowConfirmModal(true)}
              className="gap-2"
            >
              <Rocket className="w-4 h-4" />
              Confirm & Execute
            </Button>
          )}

          {isExecuting && (
            <div className="flex items-center gap-2 text-blue-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm font-medium">Executing campaign...</span>
            </div>
          )}
        </div>

        {apiError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{apiError}</p>
          </div>
        )}

        {/* Mobile Tab Switcher */}
        <div className="mt-4 flex gap-2 md:hidden">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'chat'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('draft')}
            className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'draft'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Draft
          </button>
        </div>
      </div>

      {/* Main Content - Responsive Split Screen */}
      <div className="flex-1 flex overflow-hidden">
        {/* Desktop: Both visible, Mobile: Tabs */}
        <div className={`w-full md:w-1/2 border-r ${activeTab === 'chat' ? 'block' : 'hidden md:block'}`}>
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoadingMessage}
          />
        </div>

        <div className={`w-full md:w-1/2 ${activeTab === 'draft' ? 'block' : 'hidden md:block'}`}>
          <DraftPreview campaign={campaign} />
        </div>
      </div>

      {/* Confirm Execute Modal */}
      <ConfirmExecuteModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleConfirmExecute}
        campaignTitle={campaign.title}
      />
    </div>
  )
}