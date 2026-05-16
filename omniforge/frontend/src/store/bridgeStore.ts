/**
 * OmniForge — Bridge Store (Zustand)
 * Communicates with the Godot Bridge via backend REST/broadcast.
 */

import { create } from 'zustand';

interface BridgeState {
  isConnected: boolean;
  
  sendPreviewCommand: (cmd: string, path: string, extra?: Record<string, any>) => Promise<void>;
  closePreview: () => Promise<void>;
}

export const useBridgeStore = create<BridgeState>((set) => ({
  isConnected: false, // In a real app, we'd poll this from /api/health

  sendPreviewCommand: async (cmd, path, extra = {}) => {
    try {
      // We'll add an endpoint to the backend to broadcast commands
      await fetch('/api/bridge/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd, path, ...extra }),
      });
    } catch (e) {
      console.error('Failed to send bridge command:', e);
    }
  },

  closePreview: async () => {
    try {
      await fetch('/api/bridge/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd: 'close_preview' }),
      });
    } catch (e) {
      console.error('Failed to close preview:', e);
    }
  },
}));
