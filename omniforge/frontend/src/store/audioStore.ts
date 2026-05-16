/**
 * OmniForge — Audio Store (Zustand)
 * Handles audio generation and processing state.
 */

import { create } from 'zustand';

interface AudioState {
  isProcessing: boolean;
  
  generateAudio: (projectId: string, prompt: string) => Promise<void>;
  processAudio: (projectId: string, assetId: string, pipeline: any[]) => Promise<void>;
}

export const useAudioStore = create<AudioState>((set) => ({
  isProcessing: false,

  generateAudio: async (projectId, prompt) => {
    set({ isProcessing: true });
    try {
      const res = await fetch('/api/audio/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, prompt }),
      });
      if (!res.ok) throw new Error('Audio generation failed');
    } catch (e) {
      console.error(e);
    } finally {
      set({ isProcessing: false });
    }
  },

  processAudio: async (projectId, assetId, pipeline) => {
    set({ isProcessing: true });
    try {
      const res = await fetch('/api/audio/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, asset_id: assetId, pipeline }),
      });
      if (!res.ok) throw new Error('Audio processing failed');
    } catch (e) {
      console.error(e);
    } finally {
      set({ isProcessing: false });
    }
  },
}));
