import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRealtimeCampaign } from '../hooks/useRealtimeCampaign'
import { ChatInterface } from '../components/Strategy/ChatInterface'
import { DraftPreview } from '../components/Strategy/DraftPreview'
import { ConfirmExecuteModal } from '../components/Strategy/ConfirmExecuteModal'
import { Button } from '../components/ui/button'
import { ArrowLeft, Rocket, Loader2, X } from 'lucide-react'
import api from '../lib/api'

export const StrategyPage = () => {
  const { campaignId } = useParams<{ campaignId: string }>()
  const navigate = useNavigate()
  const { campaign, messages, loading, error } = useRealtimeCampaign(campaignId!)
  
  const [isLoadingMessage, setIsLoadingMessage] = useState(false)
  const [showConfirmModal, setShowConfirmModal] = useState(false)

  const handleSendMessage = async (content: string) => {
    if (!campaignId) return

    setIsLoadingMessage(true)
    try {
      await api.post('/chat/message', {
        campaign_id: campaignId,
        content,
      })
    } catch (error) {
      console.error('Error sending message:', error)
      throw error
    } finally {
      setIsLoadingMessage(false)
    }
  }

  const handleConfirmExecute = async () => {
    if (!campaignId) return

    try {
      await api.post('/chat/confirm-execute', {
        campaign_id: campaignId,
      })
      
      setShowConfirmModal(false)
      
      // Navigate to canvas page after short delay
      setTimeout(() => {
        navigate(`/canvas/${campaignId}`)
      }, 1500)
    } catch (error) {
      console.error('Error executing campaign:', error)
      throw error
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
      </div>

      {/* Main Content - Split Screen */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side - Chat */}
        <div className="w-1/2 border-r">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoadingMessage}
          />
        </div>

        {/* Right Side - Draft Preview */}
        <div className="w-1/2">
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