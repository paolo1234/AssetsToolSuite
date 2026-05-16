/**
 * OmniForge — Project Store (Zustand)
 * Global state for project & asset management.
 * All modules read/write through this store — no local state.
 */

import { create } from 'zustand';

// ── Types ──────────────────────────────────────────────────────────

export interface AssetMetadata {
  frames?: number;
  fps?: number;
  pivot?: { x: number; y: number };
  loop_mode?: 'loop' | 'ping-pong' | 'once';
  loop_in?: number;
  loop_out?: number;
  duration_ms?: number;
  extra?: Record<string, unknown>;
  resolution?: string;
}

export interface AssetEntry {
  id: string;
  name: string;
  type: string;
  category: string;
  tags: string[];
  file_path: string;
  hash_md5: string;
  created_at: string;
  updated_at: string;
  version: number;
  metadata: AssetMetadata;
  dna_id: string | null;
  quality_score: number | null;
}

export interface ProjectManifest {
  version: string;
  project_name: string;
  target_resolution: { width: number; height: number };
  tile_size: number;
  base_fps: number;
  godot_project_path: string;
  palette_reference: string;
  light_direction_degrees: number;
  naming_convention: string;
  style_bible_images: string[];
  assets: AssetEntry[];
  presets: Record<string, unknown>;
  export_history: unknown[];
}

export interface Project {
  id: string;
  project_name: string;
  name?: string; // For compatibility with older references
  path: string;
  manifest?: ProjectManifest;
}

export interface Conflict {
  asset_id: string;
  name: string;
  issue: string;
  detail: string;
}

// ── Store ──────────────────────────────────────────────────────────

const API_BASE = '/api';

interface ProjectState {
  // State
  projects: Project[];
  currentProject: Project | null;
  assets: AssetEntry[];
  selectedAsset: AssetEntry | null;
  conflicts: Conflict[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchProjects: () => Promise<void>;
  createProject: (name: string, options?: Record<string, unknown>) => Promise<Project | null>;
  loadProject: (id: string) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  addAsset: (asset: Partial<AssetEntry>) => Promise<AssetEntry | null>;
  updateAsset: (assetId: string, updates: Partial<AssetEntry>) => Promise<void>;
  deleteAsset: (assetId: string) => Promise<void>;
  rollbackAsset: (assetId: string, targetVersion: number) => Promise<void>;
  checkConflicts: () => Promise<void>;
  selectAsset: (asset: AssetEntry | null) => void;
  clearError: () => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  // Initial state
  projects: [],
  currentProject: null,
  assets: [],
  selectedAsset: null,
  conflicts: [],
  isLoading: false,
  error: null,

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/projects`);
      if (!res.ok) throw new Error('Failed to fetch projects');
      const projects = await res.json();
      set({ projects, isLoading: false });
    } catch (e) {
      set({ error: (e as Error).message, isLoading: false });
    }
  },

  createProject: async (name, options = {}) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_name: name, ...options }),
      });
      if (!res.ok) throw new Error('Failed to create project');
      const project = await res.json();
      await get().fetchProjects();
      set({ isLoading: false });
      return project;
    } catch (e) {
      set({ error: (e as Error).message, isLoading: false });
      return null;
    }
  },

  loadProject: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/projects/${id}`);
      if (!res.ok) throw new Error('Failed to load project');
      const data = await res.json();
      set({
        currentProject: { id: data.id, project_name: data.manifest.project_name, path: '', manifest: data.manifest },
        assets: data.manifest.assets || [],
        isLoading: false,
      });
    } catch (e) {
      set({ error: (e as Error).message, isLoading: false });
    }
  },

  deleteProject: async (id) => {
    try {
      await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
      const { currentProject } = get();
      if (currentProject?.id === id) {
        set({ currentProject: null, assets: [], selectedAsset: null });
      }
      await get().fetchProjects();
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  addAsset: async (asset) => {
    const { currentProject } = get();
    if (!currentProject) return null;
    try {
      const res = await fetch(`${API_BASE}/projects/${currentProject.id}/assets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(asset),
      });
      if (!res.ok) throw new Error('Failed to add asset');
      const data = await res.json();
      await get().loadProject(currentProject.id);
      return data.asset;
    } catch (e) {
      set({ error: (e as Error).message });
      return null;
    }
  },

  updateAsset: async (assetId, updates) => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      await fetch(`${API_BASE}/projects/${currentProject.id}/assets/${assetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      await get().loadProject(currentProject.id);
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  deleteAsset: async (assetId) => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      await fetch(`${API_BASE}/projects/${currentProject.id}/assets/${assetId}`, {
        method: 'DELETE',
      });
      set({ selectedAsset: null });
      await get().loadProject(currentProject.id);
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  rollbackAsset: async (assetId, targetVersion) => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      await fetch(`${API_BASE}/projects/${currentProject.id}/assets/${assetId}/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_version: targetVersion }),
      });
      await get().loadProject(currentProject.id);
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  checkConflicts: async () => {
    const { currentProject } = get();
    if (!currentProject) return;
    try {
      const res = await fetch(`${API_BASE}/projects/${currentProject.id}/conflicts`);
      const conflicts = await res.json();
      set({ conflicts });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  selectAsset: (asset) => set({ selectedAsset: asset }),
  clearError: () => set({ error: null }),
}));
