/**
 * OmniForge — Main Application
 * Entry point with workspace tabs and project management.
 */

import { useEffect, useState } from 'react';
import WorkspaceLayout from './layouts/WorkspaceLayout';
import ImageWorkspace from './workspaces/ImageWorkspace';
import AnimationWorkspace from './workspaces/AnimationWorkspace';
import AudioWorkspace from './workspaces/AudioWorkspace';
import CheckerWorkspace from './workspaces/CheckerWorkspace';
import MovesetWorkspace from './workspaces/MovesetWorkspace';
import StatesWorkspace from './workspaces/StatesWorkspace';
import LibraryWorkspace from './workspaces/LibraryWorkspace';
import CutsceneWorkspace from './workspaces/CutsceneWorkspace';
import { useProjectStore, type Project } from './store/projectStore';

// ── Workspace Definitions ────────────────────────────────────────

type WorkspaceId =
  | 'image'
  | 'animation'
  | 'audio'
  | 'ui'
  | 'checker'
  | 'moveset'
  | 'statemachine'
  | 'cutscene'
  | 'library';

interface WorkspaceTab {
  id: WorkspaceId;
  label: string;
  icon: string;
}

const WORKSPACES: WorkspaceTab[] = [
  { id: 'image', label: 'Image', icon: '🖼️' },
  { id: 'animation', label: 'Animation', icon: '🎬' },
  { id: 'audio', label: 'Audio', icon: '🔊' },
  { id: 'ui', label: 'UI/Level', icon: '🎨' },
  { id: 'checker', label: 'Checker', icon: '✅' },
  { id: 'moveset', label: 'Moveset', icon: '🏃' },
  { id: 'statemachine', label: 'States', icon: '🔀' },
  { id: 'cutscene', label: 'Cutscene', icon: '🎭' },
  { id: 'library', label: 'Library', icon: '📚' },
];

// ── TopBar Component ─────────────────────────────────────────────

function TopBar({
  activeWorkspace,
  onWorkspaceChange,
  projectName,
}: {
  activeWorkspace: WorkspaceId;
  onWorkspaceChange: (id: WorkspaceId) => void;
  projectName: string;
}) {
  return (
    <header className="h-12 bg-of-bg-800 border-b border-of-border flex items-center px-4 gap-2">
      {/* Logo & Project Name */}
      <div className="flex items-center gap-2 mr-4 min-w-[180px]">
        <span className="text-of-accent font-bold text-lg">⚒️</span>
        <span className="text-sm font-semibold text-of-text truncate">
          {projectName || 'OmniForge'}
        </span>
      </div>

      {/* Workspace Tabs */}
      <nav className="flex items-center gap-0.5 overflow-x-auto flex-1">
        {WORKSPACES.map((ws) => (
          <button
            key={ws.id}
            onClick={() => onWorkspaceChange(ws.id)}
            className={`workspace-tab whitespace-nowrap ${
              activeWorkspace === ws.id ? 'workspace-tab-active' : ''
            }`}
          >
            <span className="mr-1.5">{ws.icon}</span>
            {ws.label}
          </button>
        ))}
      </nav>

      {/* Connection Status */}
      <div className="flex items-center gap-2 text-xs text-of-text-dim ml-2">
        <span className="w-2 h-2 rounded-full bg-of-success animate-pulse" />
        Backend
      </div>
    </header>
  );
}

// ── StatusBar Component ──────────────────────────────────────────

function StatusBar({ assetCount, godotConnected }: { assetCount: number; godotConnected: boolean }) {
  return (
    <footer className="h-7 bg-of-bg-800 border-t border-of-border flex items-center px-4 text-xs text-of-text-dim gap-4">
      <span>Assets: {assetCount}</span>
      <span className="flex items-center gap-1">
        <span className={`w-1.5 h-1.5 rounded-full ${godotConnected ? 'bg-of-success' : 'bg-of-text-dim'}`} />
        Godot {godotConnected ? 'Connected' : 'Offline'}
      </span>
      <span className="ml-auto">OmniForge v0.1.0</span>
    </footer>
  );
}

// ── Welcome Screen ───────────────────────────────────────────────

function WelcomeScreen({ onCreateProject }: { onCreateProject: (name: string) => void }) {
  const [name, setName] = useState('');
  const { projects, fetchProjects, loadProject } = useProjectStore();

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <div className="flex items-center justify-center h-full">
      <div className="max-w-md w-full p-8 panel">
        <h1 className="text-2xl font-bold text-of-text mb-1">⚒️ OmniForge</h1>
        <p className="text-sm text-of-text-muted mb-6">Game Assets Tool Suite</p>

        {/* Create new project */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-of-text-muted mb-2">New Project</label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Project name..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input-field flex-1"
              onKeyDown={(e) => e.key === 'Enter' && name && onCreateProject(name)}
            />
            <button
              onClick={() => name && onCreateProject(name)}
              disabled={!name}
              className="btn-primary disabled:opacity-40"
            >
              Create
            </button>
          </div>
        </div>

        {/* Recent projects */}
        {projects.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-of-text-muted mb-2">Recent Projects</label>
            <div className="space-y-1.5">
              {projects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => loadProject(p.id)}
                  className="w-full text-left px-3 py-2.5 rounded-md 
                             bg-of-bg-800 hover:bg-of-surface-hover
                             border border-of-border hover:border-of-border-focus
                             transition-all duration-150 group"
                >
                  <span className="text-sm font-medium text-of-text group-hover:text-of-accent-light">
                    {p.project_name}
                  </span>
                  <span className="block text-xs text-of-text-dim mt-0.5 truncate">{p.path}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sidebar (Asset List) ─────────────────────────────────────────

function Sidebar() {
  const { assets, selectedAsset, selectAsset } = useProjectStore();

  const categories = [...new Set(assets.map((a) => a.category))];

  return (
    <div className="p-3">
      <div className="panel-header mb-3">
        <span>Assets ({assets.length})</span>
      </div>
      {categories.map((cat) => (
        <div key={cat} className="mb-3">
          <h3 className="text-xs font-semibold text-of-text-dim uppercase tracking-wider mb-1.5 px-1">
            {cat}
          </h3>
          {assets
            .filter((a) => a.category === cat)
            .map((asset) => (
              <button
                key={asset.id}
                onClick={() => selectAsset(asset)}
                className={`w-full text-left px-2 py-1.5 rounded text-sm mb-0.5
                  transition-colors duration-100
                  ${
                    selectedAsset?.id === asset.id
                      ? 'bg-of-accent/20 text-of-accent-light'
                      : 'text-of-text hover:bg-of-surface-hover'
                  }`}
              >
                {asset.name}
                <span className="block text-xs text-of-text-dim">{asset.type}</span>
              </button>
            ))}
        </div>
      ))}
      {assets.length === 0 && (
        <p className="text-xs text-of-text-dim text-center mt-8">No assets yet</p>
      )}
    </div>
  );
}

// ── Inspector (Asset Details) ────────────────────────────────────

function Inspector() {
  const { selectedAsset, deleteAsset } = useProjectStore();

  if (!selectedAsset) {
    return (
      <div className="p-3">
        <div className="panel-header mb-3">
          <span>Inspector</span>
        </div>
        <p className="text-xs text-of-text-dim text-center mt-8">Select an asset</p>
      </div>
    );
  }

  return (
    <div className="p-3">
      <div className="panel-header mb-3">
        <span>Inspector</span>
      </div>

      <div className="space-y-3 text-sm">
        <div>
          <label className="text-xs text-of-text-dim">Name</label>
          <p className="text-of-text font-medium">{selectedAsset.name}</p>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs text-of-text-dim">Type</label>
            <p className="text-of-text">{selectedAsset.type}</p>
          </div>
          <div>
            <label className="text-xs text-of-text-dim">Category</label>
            <p className="text-of-text">{selectedAsset.category}</p>
          </div>
        </div>
        <div>
          <label className="text-xs text-of-text-dim">Tags</label>
          <div className="flex flex-wrap gap-1 mt-1">
            {selectedAsset.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 rounded-full text-xs bg-of-accent/20 text-of-accent-light"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs text-of-text-dim">Version</label>
          <p className="text-of-text">{selectedAsset.version}</p>
        </div>
        <div>
          <label className="text-xs text-of-text-dim">Quality Score</label>
          <p className="text-of-text">{selectedAsset.quality_score ?? '—'}</p>
        </div>
        <div>
          <label className="text-xs text-of-text-dim">File</label>
          <p className="text-of-text-muted text-xs truncate">{selectedAsset.file_path}</p>
        </div>

        <button
          onClick={() => deleteAsset(selectedAsset.id)}
          className="w-full mt-4 px-3 py-2 rounded-md text-sm text-of-danger
                     border border-of-danger/30 hover:bg-of-danger/10
                     transition-all duration-150"
        >
          Delete Asset
        </button>
      </div>
    </div>
  );
}

// ── Canvas Placeholder ───────────────────────────────────────────

function CanvasArea({ workspace }: { workspace: WorkspaceId }) {
  if (workspace === 'home') return <LibraryWorkspace />;
  if (workspace === 'image') return <ImageWorkspace />;
  if (workspace === 'animation') return <AnimationWorkspace />;
  if (workspace === 'audio') return <AudioWorkspace />;
  if (workspace === 'checker') return <CheckerWorkspace />;
  if (workspace === 'moveset') return <MovesetWorkspace />;
  if (workspace === 'states') return <StatesWorkspace />;
  if (workspace === 'cutscene') return <CutsceneWorkspace />;
  
  const label = WORKSPACES.find((w) => w.id === workspace)?.label ?? workspace;
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <p className="text-5xl mb-4">{WORKSPACES.find((w) => w.id === workspace)?.icon}</p>
        <h2 className="text-xl font-semibold text-of-text mb-1">{label} Workspace</h2>
        <p className="text-sm text-of-text-dim">Coming in the next phase</p>
      </div>
    </div>
  );
}

// ── App ──────────────────────────────────────────────────────────

export default function App() {
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceId>('image');
  const { currentProject, assets, createProject, loadProject } = useProjectStore();

  const handleCreateProject = async (name: string) => {
    const project = await createProject(name);
    if (project) {
      await loadProject(project.id);
    }
  };

  // No project loaded → show welcome screen
  if (!currentProject) {
    return (
      <div className="h-screen flex flex-col">
        <TopBar
          activeWorkspace={activeWorkspace}
          onWorkspaceChange={setActiveWorkspace}
          projectName=""
        />
        <div className="flex-1 overflow-hidden">
          <WelcomeScreen onCreateProject={handleCreateProject} />
        </div>
        <StatusBar assetCount={0} godotConnected={false} />
      </div>
    );
  }

  // Project loaded → show workspace layout
  return (
    <div className="h-screen flex flex-col">
      <TopBar
        activeWorkspace={activeWorkspace}
        onWorkspaceChange={setActiveWorkspace}
        projectName={currentProject.project_name}
      />
      <div className="flex-1 overflow-hidden">
        <WorkspaceLayout
          sidebar={<Sidebar />}
          canvas={<CanvasArea workspace={activeWorkspace} />}
          inspector={<Inspector />}
        />
      </div>
      <StatusBar assetCount={assets.length} godotConnected={false} />
    </div>
  );
}
