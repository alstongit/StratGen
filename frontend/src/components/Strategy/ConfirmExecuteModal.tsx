import { useState } from 'react'
import { X, Rocket, AlertCircle } from 'lucide-react'
import { Button } from '../ui/button'

interface ConfirmExecuteModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  campaignTitle: string
}

export const ConfirmExecuteModal = ({
  isOpen,
  onClose,
  onConfirm,
  campaignTitle,
}: ConfirmExecuteModalProps) => {
  const [isExecuting, setIsExecuting] = useState(false)

  if (!isOpen) return null

  const handleConfirm = async () => {
    setIsExecuting(true)
    try {
      await onConfirm()
    } catch (error) {
      console.error('Error executing campaign:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
              <Rocket className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Execute Campaign</h3>
              <p className="text-sm text-gray-600">{campaignTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isExecuting}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="mb-6">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-900 mb-1">
                  This will start generating your campaign assets
                </p>
                <p className="text-xs text-amber-700">
                  The AI will create images, copy, influencer recommendations, and execution plans 
                  based on your strategy. This process may take a few minutes.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-2 text-sm text-gray-700">
            <p className="flex items-start gap-2">
              <span className="text-indigo-600 font-semibold">✓</span>
              <span>Generate images for each day</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-indigo-600 font-semibold">✓</span>
              <span>Create captions and headlines</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-indigo-600 font-semibold">✓</span>
              <span>Find relevant influencers</span>
            </p>
            <p className="flex items-start gap-2">
              <span className="text-indigo-600 font-semibold">✓</span>
              <span>Build execution plan</span>
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isExecuting}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={isExecuting}
            className="flex-1"
          >
            {isExecuting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Executing...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4 mr-2" />
                Confirm & Execute
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}