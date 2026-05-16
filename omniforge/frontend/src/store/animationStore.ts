/**
 * OmniForge — Animation Store (Zustand)
 * Handles spritesheet slicing and preview playback state.
 */

import { create } from 'zustand';

interface AnimationState {
  isPlaying: boolean;
  currentFrame: number;
  fps: number;
  grid: { width: number; height: number };
  
  togglePlay: () => void;
  setFPS: (fps: number) => void;
  setFrame: (frame: number) => void;
  sliceAsset: (projectId: string, assetId: string, frameWidth?: number, frameHeight?: number) => Promise<void>;
}

export const useAnimationStore = create<AnimationState>((set) => ({
  isPlaying: false,
  currentFrame: 0,
  fps: 10,
  grid: { width: 32, height: 32 },

  togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
  setFPS: (fps) => set({ fps }),
  setFrame: (frame) => set({ currentFrame: frame }),

  sliceAsset: async (projectId, assetId, frameWidth, frameHeight) => {
    try {
      const res = await fetch('/api/animations/slice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          asset_id: assetId,
          frame_width: frameWidth,
          frame_height: frameHeight,
        }),
      });
      if (!res.ok) throw new Error('Slicing failed');
      const data = await res.json();
      set({ grid: data.grid });
    } catch (e) {
      console.error(e);
    }
  },
}));
