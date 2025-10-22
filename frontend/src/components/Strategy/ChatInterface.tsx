import { useState, useEffect, useRef } from 'react';
import type { Campaign, Message } from '@/types';
import { chatAPI, campaignsAPI } from '@/lib/api';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { ConfirmExecuteModal } from './ConfirmExecuteModal';
import { useNavigate } from 'react-router-dom';

interface ChatInterfaceProps {
  campaign: Campaign;
}

export function ChatInterface({ campaign }: ChatInterfaceProps) {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(true);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages on mount
  useEffect(() => {
    loadMessages();
  }, [campaign.id]);

  // Subscribe to new messages
  useEffect(() => {
    console.log(`🔔 Subscribing to messages for campaign ${campaign.id}`);
    
    const channel = supabase
      .channel(`messages:${campaign.id}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'chat_messages',
          filter: `campaign_id=eq.${campaign.id}`,
        },
        (payload) => {
          console.log('🔔 New message received:', payload);
          const newMessage = payload.new as Message;
          
          setMessages((prev) => {
            // Avoid duplicates
            if (prev.find(m => m.id === newMessage.id)) {
              return prev;
            }
            return [...prev, newMessage];
          });
        }
      )
      .subscribe();

    return () => {
      console.log(`🔕 Unsubscribing from messages for campaign ${campaign.id}`);
      supabase.removeChannel(channel);
    };
  }, [campaign.id]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async () => {
    try {
      setLoadingMessages(true);
      const msgs = await campaignsAPI.getCampaignMessages(campaign.id);
      console.log(`📚 Loaded ${msgs.length} messages`);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    try {
      console.log('📤 Sending message:', userMessage);
      
      // The backend will save both user and AI messages to DB
      // Realtime will pick them up and add them to the UI
      await chatAPI.sendMessage(campaign.id, userMessage);
      
      console.log('✅ Message sent successfully');
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
      setInput(userMessage); // Restore message on error
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleConfirmExecute = async () => {
    try {
      setLoading(true);
      await chatAPI.confirmExecute(campaign.id);
      setShowConfirmModal(false);
      
      // Navigate to canvas after a brief delay
      setTimeout(() => {
        navigate(`/canvas/${campaign.id}`);
      }, 1000);
    } catch (error) {
      console.error('Failed to execute campaign:', error);
      alert('Failed to start execution. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canExecute = campaign.status === 'draft_ready' && campaign.draft_json && Object.keys(campaign.draft_json).length > 0;

  if (loadingMessages) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col h-full bg-white">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="bg-blue-50 rounded-full p-4 mb-4">
                <Sparkles className="w-12 h-12 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Let's Create Your Campaign Strategy
              </h3>
              <p className="text-gray-600 max-w-md mb-6">
                Tell me about your campaign! What are you trying to achieve? Who's your target audience? 
                I'll help you build a complete marketing strategy.
              </p>
              <div className="bg-gray-50 rounded-lg p-4 text-left max-w-md">
                <p className="text-sm text-gray-700 mb-2 font-medium">Example prompts:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "I want to launch a new fitness app for millennials"</li>
                  <li>• "Creating a campaign for our eco-friendly products"</li>
                  <li>• "Need to promote a tech conference in Mumbai"</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs opacity-70 mt-2">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
                  </div>
                </div>
              )}
            </>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Action Button - Show when draft is ready */}
        {canExecute && (
          <div className="border-t bg-green-50 px-6 py-3">
            <Button
              onClick={() => setShowConfirmModal(true)}
              className="w-full gap-2 bg-green-600 hover:bg-green-700"
              size="lg"
            >
              <Sparkles className="w-5 h-5" />
              Confirm & Execute Campaign
            </Button>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t p-4 bg-gray-50">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                messages.length === 0
                  ? "Describe your campaign goals, target audience, timeline..."
                  : "Continue the conversation or refine your strategy..."
              }
              className="flex-1 min-h-[80px] resize-none"
              disabled={loading}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              size="icon"
              className="h-[80px] w-[80px]"
            >
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <Send className="w-6 h-6" />
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>

      {/* Confirm Execute Modal */}
      <ConfirmExecuteModal
        open={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleConfirmExecute}
        campaign={campaign}
      />
    </>
  );
}