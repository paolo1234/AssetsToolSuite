import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface GenerationTask {
  id: string;
  project_id: string;
  prompt: string;
  adapter_id: string;
  workflow_id?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result_url?: string;
  result_asset_id?: string;
  error?: string;
  seed?: number;
  created_at?: number;
}

interface ImageState {
  activeTasks: Record<string, GenerationTask>;
  isGenerating: boolean;

  generateImage: (projectId: string, prompt: string, adapterId: string, workflowId?: string, params?: Record<string, unknown>) => Promise<string | null>;
  upscaleImage: (assetId: string, projectId: string) => Promise<void>;
  refineImage: (assetId: string, projectId: string) => Promise<void>;
  deleteTask: (taskId: string) => void;
  pollTaskStatus: (taskId: string) => Promise<void>;
  processImage: (projectId: string, assetId: string, pipeline: any[]) => Promise<void>;
}

export const useImageStore = create<ImageState>()(
  persist(
    (set, get) => ({
      activeTasks: {},
      isGenerating: false,

      generateImage: async (projectId, prompt, adapterId, workflowId = 'sprite_single', params = {}) => {
        set({ isGenerating: true });
        try {
          const res = await fetch('/api/generate/image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId, prompt, adapter_id: adapterId, workflow_id: workflowId, params }),
          });
          if (!res.ok) throw new Error('Failed to start generation');
          const data = await res.json();

          const newTask: GenerationTask = {
            id: data.task_id,
            project_id: projectId,
            prompt,
            adapter_id: adapterId,
            workflow_id: workflowId,
            status: 'pending',
            progress: 0,
            seed: params.seed as number || Math.floor(Math.random() * 1000000000),
            created_at: Date.now(),
          };

          set((state) => ({
            activeTasks: { ...state.activeTasks, [data.task_id]: newTask },
            isGenerating: false,
          }));

          get().pollTaskStatus(data.task_id);
          return data.task_id;
        } catch (e) {
          set({ isGenerating: false });
          console.error(e);
          return null;
        }
      },

      upscaleImage: async (assetId, projectId) => {
        try {
          const res = await fetch('/api/generate/upscale', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ asset_id: assetId, project_id: projectId, scale: 4 }),
          });
          if (!res.ok) throw new Error('Upscale failed');
          const data = await res.json();
          alert(`Upscale completato! Nuovo asset: ${data.asset_id}`);
        } catch (e) {
          console.error(e);
          alert('Upscale fallito. Verifica che il backend sia in esecuzione.');
        }
      },

      refineImage: async (assetId, projectId) => {
        try {
          const res = await fetch('/api/generate/refine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ asset_id: assetId, project_id: projectId }),
          });
          if (!res.ok) throw new Error('Refine failed');
          const data = await res.json();
          alert(`Refine completato! Nuovo asset: ${data.asset_id}`);
        } catch (e) {
          console.error(e);
          alert('Refine fallito. Verifica che il backend e ComfyUI siano in esecuzione.');
        }
      },

      deleteTask: (taskId) => {
        set((state) => {
          const { [taskId]: _, ...rest } = state.activeTasks;
          return { activeTasks: rest };
        });
      },

      pollTaskStatus: async (taskId) => {
        const interval = setInterval(async () => {
          try {
            const res = await fetch(`/api/generate/status/${taskId}`);
            if (!res.ok) throw new Error('Failed to poll status');
            const task = await res.json();

            set((state) => ({
              activeTasks: {
                ...state.activeTasks,
                [taskId]: {
                  ...state.activeTasks[taskId],
                  status: task.status,
                  progress: task.progress,
                  result_url: task.result_url,
                  result_asset_id: task.result_asset_id,
                  error: task.error,
                },
              },
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
    }),
    {
      name: 'omniforge-image',
      partialize: (state) => ({
        activeTasks: Object.fromEntries(
          Object.entries(state.activeTasks).filter(
            ([_, t]) => t.status === 'completed' || t.status === 'processing'
          )
        ),
      }),
    }
  )
);