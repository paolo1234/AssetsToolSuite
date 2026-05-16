/**
 * OmniForge — Config Store (Zustand)
 * Manages global application settings.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface GlobalConfig {
  BACKEND_HOST: string;
  BACKEND_PORT: number;
  BRIDGE_PORT: number;
  PROJECTS_DIR: string;
  MAX_ASSET_VERSIONS: number;
  QUALITY_GATE_THRESHOLD: number;
  OPENAI_API_KEY: string;
  COMFYUI_URL: string;
  ELEVENLABS_API_KEY: string;
  REPLICATE_API_KEY: string;
  SUNO_API_KEY: string;
}

interface ConfigState {
  config: GlobalConfig | null;
  isLoading: boolean;
  error: string | null;
  
  fetchConfig: () => Promise<void>;
  updateConfig: (newSettings: Partial<GlobalConfig>) => Promise<void>;
}

export const useConfigStore = create<ConfigState>()(
  persist(
    (set) => ({
  config: null,
  isLoading: false,
  error: null,

  fetchConfig: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch('/api/config');
      if (!res.ok) throw new Error('Failed to fetch config');
      const data = await res.json();
      set({ config: data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },

  updateConfig: async (newSettings) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: newSettings }),
      });
      if (!res.ok) throw new Error('Failed to update config');
      
      // Refresh local state
      const updatedRes = await fetch('/api/config');
      const updatedData = await updatedRes.json();
      set({ config: updatedData, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },
}),
    {
      name: 'omniforge-config',
      partialize: (state) => ({ config: state.config }),
    }
  )
);
