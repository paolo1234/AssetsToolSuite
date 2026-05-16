/**
 * OmniForge — Quality Store (Zustand)
 * Handles quality analysis and batch corrections.
 */

import { create } from 'zustand';

interface AnalysisResult {
  score: number;
  metrics: Record<string, any>;
  suggestions: string[];
}

interface QualityState {
  isAnalyzing: boolean;
  lastAnalysis: AnalysisResult | null;
  
  analyzeAsset: (projectId: string, assetId: string) => Promise<void>;
  applyBatchCorrection: (projectId: string, assetIds: string[], params: Record<string, any>) => Promise<void>;
}

export const useQualityStore = create<QualityState>((set) => ({
  isAnalyzing: false,
  lastAnalysis: null,

  analyzeAsset: async (projectId, assetId) => {
    set({ isAnalyzing: true });
    try {
      const res = await fetch(`/api/quality/${projectId}/${assetId}/analyze`);
      if (!res.ok) throw new Error('Analysis failed');
      const data = await res.json();
      set({ lastAnalysis: data, isAnalyzing: false });
    } catch (e) {
      console.error(e);
      set({ isAnalyzing: false });
    }
  },

  applyBatchCorrection: async (projectId, assetIds, params) => {
    try {
      const res = await fetch('/api/quality/batch-correct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, asset_ids: assetIds, params }),
      });
      if (!res.ok) throw new Error('Batch correction failed');
    } catch (e) {
      console.error(e);
    }
  },
}));
