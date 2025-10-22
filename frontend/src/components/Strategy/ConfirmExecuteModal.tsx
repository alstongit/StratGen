import type { Campaign } from '@/types'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Sparkles, CheckCircle, Clock, Target } from 'lucide-react'

interface ConfirmExecuteModalProps {
  open: boolean // Changed from isOpen to open
  onClose: () => void
  onConfirm: () => void
  campaign: Campaign
}

export function ConfirmExecuteModal({
  open,
  onClose,
  onConfirm,
  campaign,
}: ConfirmExecuteModalProps) {
  const draftJson = campaign.draft_json || {}

  // Extract key info from draft
  const brandName = draftJson.brand_name || 'Your brand'
  const duration = draftJson.duration || 'N/A'
  const postingSchedule = draftJson.posting_schedule || {}
  const numPosts = Object.keys(postingSchedule).length || 0

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Sparkles className="w-6 h-6 text-blue-600" />
            Ready to Generate Assets?
          </DialogTitle>
          <DialogDescription className="text-base pt-2">
            I'll now generate all campaign assets based on your approved strategy.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              What will be generated:
            </h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>
                  <strong>{numPosts || 'Multiple'} social media posts</strong> with
                  copy optimized for engagement
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>
                  <strong>{numPosts || 'Custom'} images</strong> matching your
                  brand's visual style
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>
                  <strong>10 relevant influencers</strong> for potential
                  partnerships
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>
                  <strong>Execution plan</strong> with timeline and checklist
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <Target className="w-5 h-5" />
              Campaign Summary:
            </h4>
            <div className="space-y-1 text-sm text-gray-700">
              <p>
                <strong>Brand:</strong> {brandName}
              </p>
              <p>
                <strong>Duration:</strong> {duration}
              </p>
              {numPosts > 0 && (
                <p>
                  <strong>Posts:</strong> {numPosts} posts scheduled
                </p>
              )}
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Clock className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <p className="font-semibold mb-1">Estimated time: 2-3 minutes</p>
                <p>
                  You'll see real-time progress updates. Once complete, you'll be
                  redirected to the canvas to view all assets.
                </p>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose}>
            Go Back
          </Button>
          <Button onClick={onConfirm} className="gap-2">
            <Sparkles className="w-4 h-4" />
            Start Generation
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}