import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import type { ChatMessage } from '../../types'
import { MessageBubble } from './MessageBubble'
import { Button } from '../ui/button'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onSendMessage: (content: string) => Promise<void>
  isLoading: boolean
}

export const ChatInterface = ({ messages, onSendMessage, isLoading }: ChatInterfaceProps) => {
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSend = async () => {
    if (!input.trim() || isSending) return

    const messageContent = input.trim()
    setInput('')
    setIsSending(true)

    try {
      await onSendMessage(messageContent)
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-900">Campaign Strategy</h2>
        <p className="text-sm text-gray-600 mt-1">
          Describe your campaign and I'll help you create a comprehensive strategy
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Send className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Start Your Campaign
              </h3>
              <p className="text-gray-600 text-sm">
                Tell me about your campaign - the event, product, or service you want to promote.
                I'll help you create a complete marketing strategy.
              </p>
              <div className="mt-6 text-left bg-white border rounded-lg p-4">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Example:</p>
                <p className="text-sm text-gray-700">
                  "I'm organizing a Counter Strike LAN event in Mumbai for 4 days. 
                  Need a social media campaign targeting gamers aged 18-30."
                </p>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
            </div>
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t px-6 py-4">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your campaign..."
            disabled={isSending || isLoading}
            className="flex-1 resize-none border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500 max-h-32"
            rows={1}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isSending || isLoading}
            className="flex-shrink-0"
          >
            {isSending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}