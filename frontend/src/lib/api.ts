import axios from 'axios';
import { supabase } from './supabase';
import type { Campaign, Message, CanvasData } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(async (config) => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  } catch (error) {
    console.error('Error getting session:', error);
  }
  
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const data = error?.response?.data;
    console.error('API Error:', status ?? 'no-response', data ?? error.message);
    return Promise.reject(error);
  }
);

export const campaignsAPI = {
  createCampaign: async (title: string, initialPrompt: string): Promise<Campaign> => {
    const response = await api.post('/campaigns', { title, initial_prompt: initialPrompt });
    return response.data;
  },

  getCampaigns: async (): Promise<Campaign[]> => {
    const response = await api.get('/campaigns');
    return response.data;
  },

  getCampaign: async (id: string): Promise<Campaign> => {
    const response = await api.get(`/campaigns/${id}`);
    return response.data;
  },

  getCampaignMessages: async (id: string): Promise<Message[]> => {
    const response = await api.get(`/campaigns/${id}/messages`);
    return response.data;
  },

  deleteCampaign: async (id: string): Promise<void> => {
    await api.delete(`/campaigns/${id}`);
  },
};

export const chatAPI = {
  sendMessage: async (campaignId: string, message: string): Promise<any> => {
    const response = await api.post('/chat/message', {
      campaign_id: campaignId,
      message,
    });
    return response.data;
  },

  confirmExecute: async (campaignId: string): Promise<any> => {
    const response = await api.post('/chat/confirm-execute', {
      campaign_id: campaignId,
    });
    return response.data;
  },
};

export const canvasAPI = {
  getCanvasData: async (campaignId: string): Promise<CanvasData> => {
    const response = await api.get(`/canvas/${campaignId}`);
    return response.data;
  },
};

export async function modifyCanvas(campaignId: string, message: string) {
  // Use axios instance so request goes to API_URL (backend), not Vite dev server
  const response = await api.post(`/canvas/${campaignId}/modify`, { message });
  return response.data;
}

export async function getCanvasModification(campaignId: string, modificationId: string) {
  // Use axios for consistent baseURL handling
  const response = await api.get(`/canvas/${campaignId}/modifications/${modificationId}`);
  return response.data;
}

export default api;