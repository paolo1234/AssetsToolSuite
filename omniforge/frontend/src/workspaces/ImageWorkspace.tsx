/**
 * OmniForge — ImageWorkspace
 * AI Image Generation & Inpainting interface.
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useImageStore, type GenerationTask } from '../store/imageStore';

export default function ImageWorkspace() {
  const [prompt, setPrompt] = useState('');
  const [adapter, setAdapter] = useState('comfyui');
  const { currentProject } = useProjectStore();
  const { generateImage, activeTasks, isGenerating } = useImageStore();

  const handleGenerate = () => {
    if (!currentProject || !prompt) return;
    generateImage(currentProject.id, prompt, adapter);
  };

  const tasks = Object.values(activeTasks).filter(
    (t) => t.project_id === currentProject?.id
  );

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <div className="flex-1 flex gap-2">
          <input
            type="text"
            placeholder="Describe the asset you want to generate..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field max-w-2xl"
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
            disabled={isGenerating || !prompt}
            className="btn-primary disabled:opacity-50"
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-of-text-dim">
            <span className="text-6xl mb-4">🖼️</span>
            <p className="text-lg">No generations yet.</p>
            <p className="text-sm">Type a prompt above to start creating assets.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {tasks.map((task) => (
              <GenerationCard key={task.id} task={task} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function GenerationCard({ task }: { task: GenerationTask }) {
  return (
    <div className="panel overflow-hidden group">
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
            {task.adapter_id}
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
