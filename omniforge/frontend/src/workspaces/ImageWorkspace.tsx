import { useState, useEffect, useCallback } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useImageStore, type GenerationTask } from '../store/imageStore';
import { useConfigStore } from '../store/configStore';

const WORKFLOW_PRESETS = [
  { id: 'sprite_single', name: 'Single Sprite', icon: '🎮', desc: 'Personaggio, NPC, nemico singolo' },
  { id: 'spritesheet_animation', name: 'Spritesheet Animation', icon: '🎬', desc: 'Sprite sheet animato (walk, attack, idle)' },
  { id: 'background_tileable', name: 'Tileable Background', icon: '🏞️', desc: 'Sfondo seamless per scene' },
  { id: 'ui_icon_button', name: 'UI Icon/Button', icon: '🖼️', desc: 'Elementi UI, icone, bottoni' },
  { id: 'prop_item', name: 'Props & Items', icon: '⚔️', desc: 'Oggetti, armi, artefatti' },
  { id: 'tilemap_tileset', name: 'Tileset', icon: '🗺️', desc: 'Tileset per tilemap' },
  { id: 'vfx_particles', name: 'VFX & Particles', icon: '✨', desc: 'Effetti particellari, spell' },
  { id: 'character_portrait', name: 'Character Portrait', icon: '👤', desc: 'Ritratti e volti' },
];

export default function ImageWorkspace() {
  const [prompt, setPrompt] = useState('');
  const [adapter, setAdapter] = useState('comfyui');
  const [workflowId, setWorkflowId] = useState('sprite_single');
  const [showPresets, setShowPresets] = useState(false);
  const [comfyuiStatus, setComfyuiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [connectionError, setConnectionError] = useState('');
  const { currentProject } = useProjectStore();
  const { config } = useConfigStore();
  const { generateImage, activeTasks, isGenerating, upscaleImage, refineImage, deleteTask } = useImageStore();

  const checkComfyUI = useCallback(async () => {
    if (adapter !== 'comfyui') {
      setComfyuiStatus('connected');
      return;
    }
    setComfyuiStatus('checking');
    try {
      const res = await fetch('/api/generate/comfyui/status');
      const data = await res.json();
      if (data.connected) {
        setComfyuiStatus('connected');
        setConnectionError('');
      } else {
        setComfyuiStatus('disconnected');
        setConnectionError(`ComfyUI non raggiungibile a ${config?.COMFYUI_URL || 'localhost:8188'}`);
      }
    } catch {
      setComfyuiStatus('disconnected');
      setConnectionError('Impossibile contattare il backend. Assicurati che il server sia in esecuzione.');
    }
  }, [adapter, config?.COMFYUI_URL]);

  useEffect(() => {
    checkComfyUI();
    const interval = setInterval(checkComfyUI, 10000);
    return () => clearInterval(interval);
  }, [checkComfyUI]);

  const handleGenerate = async () => {
    if (!currentProject || !prompt) return;
    if (comfyuiStatus === 'disconnected') {
      setConnectionError('ComfyUI non è connesso. Verifica le impostazioni in Settings.');
      return;
    }
    setConnectionError('');
    await generateImage(currentProject.id, prompt, adapter, workflowId);
  };

  const tasks = Object.values(activeTasks).filter(
    (t) => t.project_id === currentProject?.id
  );
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const activeGenerations = tasks.filter(t => t.status !== 'completed');

  const statusColor = comfyuiStatus === 'connected' ? 'bg-green-500' 
    : comfyuiStatus === 'disconnected' ? 'bg-red-500' 
    : 'bg-yellow-500';

  const statusText = comfyuiStatus === 'connected' ? 'ComfyUI Connesso'
    : comfyuiStatus === 'disconnected' ? 'ComfyUI Disconnesso'
    : 'Verifica connessione...';

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* Connection Status Bar */}
      <div className={`h-7 flex items-center px-4 text-[10px] font-bold uppercase tracking-widest ${
        comfyuiStatus === 'connected' ? 'bg-green-900/30 text-green-400'
        : comfyuiStatus === 'disconnected' ? 'bg-red-900/30 text-red-400'
        : 'bg-yellow-900/30 text-yellow-400'
      }`}>
        <div className={`w-1.5 h-1.5 rounded-full ${statusColor} mr-2 ${comfyuiStatus === 'checking' ? 'animate-pulse' : ''}`} />
        {statusText}
        {comfyuiStatus === 'disconnected' && (
          <span className="ml-4 text-red-500/70 font-normal normal-case">
            {config?.COMFYUI_URL || 'http://localhost:8188'} - Vai a Settings per cambiare
          </span>
        )}
      </div>

      {/* ToolBar */}
      <div className="h-16 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <div className="flex-1 flex gap-2 items-center">
          {/* Workflow Preset Selector */}
          <div className="relative">
            <button
              onClick={() => setShowPresets(!showPresets)}
              className="flex items-center gap-2 px-3 py-2 bg-of-bg-900 border border-of-border rounded-md hover:border-of-border-focus transition-colors whitespace-nowrap"
            >
              <span>{WORKFLOW_PRESETS.find(w => w.id === workflowId)?.icon}</span>
              <span className="text-xs text-of-text">{WORKFLOW_PRESETS.find(w => w.id === workflowId)?.name}</span>
              <span className="text-of-text-dim">▼</span>
            </button>
            {showPresets && (
              <div className="absolute top-full left-0 mt-1 w-64 bg-of-bg-800 border border-of-border rounded-md shadow-xl z-50 overflow-hidden">
                {WORKFLOW_PRESETS.map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => { setWorkflowId(preset.id); setShowPresets(false); }}
                    className={`w-full px-3 py-2 text-left hover:bg-of-bg-700 transition-colors ${workflowId === preset.id ? 'bg-of-accent/20' : ''}`}
                  >
                    <div className="flex items-center gap-2">
                      <span>{preset.icon}</span>
                      <span className="text-xs font-semibold text-of-text">{preset.name}</span>
                    </div>
                    <p className="text-[10px] text-of-text-dim pl-6">{preset.desc}</p>
                  </button>
                ))}
              </div>
            )}
          </div>

          <input
            type="text"
            placeholder="Describe the asset you want to generate..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field flex-1 max-w-xl"
            onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
          />
          <select
            value={adapter}
            onChange={(e) => setAdapter(e.target.value)}
            className="bg-of-bg-800 border border-of-border text-of-text text-sm rounded-md px-2 focus:outline-none focus:border-of-border-focus"
          >
            <option value="comfyui">ComfyUI (Local)</option>
            <option value="dalle">DALL-E 3 (Cloud)</option>
          </select>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt || comfyuiStatus === 'disconnected'}
            className="btn-primary disabled:opacity-50"
            title={comfyuiStatus === 'disconnected' ? 'ComfyUI non connesso' : ''}
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {/* Connection Error */}
        {connectionError && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-center gap-3">
            <span>⚠️</span>
            <span>{connectionError}</span>
          </div>
        )}

        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-of-text-dim">
            <span className="text-6xl mb-4">🎨</span>
            <p className="text-lg">No generations yet.</p>
            <p className="text-sm">Select a workflow type and enter a prompt to start.</p>
            <div className="mt-6 flex gap-3 flex-wrap justify-center max-w-lg">
              {WORKFLOW_PRESETS.map(p => (
                <button
                  key={p.id}
                  onClick={() => { setWorkflowId(p.id); setPrompt(''); }}
                  className="px-3 py-1.5 bg-of-bg-800 border border-of-border rounded-full text-xs hover:border-of-accent transition-colors"
                >
                  {p.icon} {p.name}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {activeGenerations.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-of-text-dim uppercase tracking-widest mb-4">Generating...</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {activeGenerations.map((task) => (
                    <GenerationCard key={task.id} task={task} />
                  ))}
                </div>
              </div>
            )}

            {completedTasks.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-of-text-dim uppercase tracking-widest mb-4">
                  Generated Assets ({completedTasks.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {completedTasks.map((task) => (
                    <GenerationCard 
                      key={task.id} 
                      task={task} 
                      onUpscale={upscaleImage} 
                      onRefine={refineImage} 
                      onDelete={deleteTask} 
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function GenerationCard({ task, onUpscale, onRefine, onDelete }: { 
  task: GenerationTask; 
  onUpscale?: (taskId: string) => void;
  onRefine?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div 
      className="panel overflow-hidden group relative"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {showActions && task.status === 'completed' && (
        <div className="absolute top-2 right-2 z-10 flex gap-1">
          {onUpscale && (
            <button
              onClick={() => onUpscale(task.id)}
              className="w-7 h-7 bg-of-bg-800 border border-of-border rounded-full flex items-center justify-center hover:bg-of-accent hover:border-of-accent transition-colors text-xs"
              title="Upscale 4x"
            >
              ↗
            </button>
          )}
          {onRefine && (
            <button
              onClick={() => onRefine(task.id)}
              className="w-7 h-7 bg-of-bg-800 border border-of-border rounded-full flex items-center justify-center hover:bg-of-accent hover:border-of-accent transition-colors text-xs"
              title="Refine"
            >
              ✨
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="w-7 h-7 bg-of-bg-800 border border-of-border rounded-full flex items-center justify-center hover:bg-of-danger hover:border-of-danger transition-colors text-xs"
              title="Delete"
            >
              ✕
            </button>
          )}
        </div>
      )}

      <div className="aspect-square bg-of-bg-800 relative flex items-center justify-center overflow-hidden">
        {task.status === 'completed' && task.result_url ? (
          <img
            src={task.result_url}
            alt={task.prompt}
            className="w-full h-full object-contain"
          />
        ) : task.status === 'failed' ? (
          <div className="p-4 text-center">
            <span className="text-3xl block mb-2">⚠️</span>
            <p className="text-xs text-of-danger">{task.error}</p>
          </div>
        ) : (
          <div className="text-center p-4 w-full">
            <div className="w-full bg-of-bg-900 rounded-full h-1.5 mb-3 overflow-hidden">
              <div
                className="bg-of-accent h-full transition-all duration-300"
                style={{ width: `${task.progress}%` }}
              />
            </div>
            <p className="text-xs text-of-text-muted animate-pulse">
              {task.status === 'processing' ? 'Thinking...' : 'Queued...'}
            </p>
          </div>
        )}
      </div>
      <div className="p-3 border-t border-of-border">
        <div className="flex justify-between items-start mb-1">
          <p className="text-xs font-semibold text-of-text-dim uppercase">
            {task.adapter_id} • {task.workflow_id || 'default'}
          </p>
          <span
            className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold ${
              task.status === 'completed'
                ? 'bg-of-success/20 text-of-success'
                : task.status === 'failed'
                ? 'bg-of-danger/20 text-of-danger'
                : 'bg-of-warning/20 text-of-warning'
            }`}
          >
            {task.status}
          </span>
        </div>
        <p className="text-xs text-of-text line-clamp-2 italic" title={task.prompt}>
          "{task.prompt}"
        </p>
      </div>
    </div>
  );
}