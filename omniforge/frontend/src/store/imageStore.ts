/**
 * OmniForge — Image Store (Zustand)
 * Handles AI generation tasks, inpainting state, and post-processing.
 */

import { create } from 'zustand';

// ── Types ──────────────────────────────────────────────────────────

export interface GenerationTask {
  id: string;
  project_id: string;
  prompt: string;
  adapter_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result_url?: string;
  error?: string;
}

interface ImageState {
  // State
  activeTasks: Record<string, GenerationTask>;
  isGenerating: boolean;
  
  // Actions
  generateImage: (projectId: string, prompt: string, adapterId: string, params?: Record<string, unknown>) => Promise<string | null>;
  pollTaskStatus: (taskId: string) => Promise<void>;
  processImage: (projectId: string, assetId: string, pipeline: any[]) => Promise<void>;
}

// ── Store ──────────────────────────────────────────────────────────

export const useImageStore = create<ImageState>((set, get) => ({
  activeTasks: {},
  isGenerating: false,

  generateImage: async (projectId, prompt, adapterId, params = {}) => {
    set({ isGenerating: true });
    try {
      const res = await fetch('/api/generate/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, prompt, adapter_id: adapterId, params }),
      });
      if (!res.ok) throw new Error('Failed to start generation');
      const data = await res.json();
      
      const newTask: GenerationTask = {
        id: data.task_id,
        project_id: projectId,
        prompt,
        adapter_id: adapterId,
        status: 'pending',
        progress: 0,
      };

      set((state) => ({
        activeTasks: { ...state.activeTasks, [data.task_id]: newTask },
        isGenerating: false,
      }));

      // Start polling
      get().pollTaskStatus(data.task_id);
      
      return data.task_id;
    } catch (e) {
      set({ isGenerating: false });
      console.error(e);
      return null;
    }
  },

  pollTaskStatus: async (taskId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/generate/status/${taskId}`);
        if (!res.ok) throw new Error('Failed to poll status');
        const task = await res.json();

        set((state) => ({
          activeTasks: { ...state.activeTasks, [taskId]: task },
        }));

        if (task.status === 'completed' || task.status === 'failed') {
          clearInterval(interval);
        }
      } catch (e) {
        clearInterval(interval);
        console.error(e);
      }
    }, 2000);
  },

  processImage: async (projectId, assetId, pipeline) => {
    try {
      const res = await fetch('/api/generate/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, asset_id: assetId, pipeline }),
      });
      if (!res.ok) throw new Error('Processing failed');
    } catch (e) {
      console.error(e);
    }
  },
}));
