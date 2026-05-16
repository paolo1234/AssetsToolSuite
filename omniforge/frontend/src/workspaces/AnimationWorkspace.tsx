/**
 * OmniForge — AnimationWorkspace
 * Spritesheet slicing and real-time animation preview.
 */

import { useState, useEffect } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useAnimationStore } from '../store/animationStore';

export default function AnimationWorkspace() {
  const { selectedAsset, currentProject } = useProjectStore();
  const { isPlaying, currentFrame, fps, grid, togglePlay, setFrame, sliceAsset } = useAnimationStore();
  
  const [frameW, setFrameW] = useState(grid.width);
  const [frameH, setFrameH] = useState(grid.height);

  // Animation Loop logic
  useEffect(() => {
    let interval: any;
    if (isPlaying && selectedAsset?.metadata?.frames) {
      interval = setInterval(() => {
        setFrame((currentFrame + 1) % (selectedAsset.metadata.frames || 1));
      }, 1000 / fps);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentFrame, fps, selectedAsset, setFrame]);

  if (!selectedAsset) {
    return (
      <div className="flex items-center justify-center h-full text-of-text-dim">
        <p>Select a spritesheet to begin</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <div className="flex items-center gap-3">
          <label className="text-xs text-of-text-dim font-bold uppercase">Grid:</label>
          <input
            type="number"
            value={frameW}
            onChange={(e) => setFrameW(parseInt(e.target.value))}
            className="w-16 input-field text-center"
          />
          <span className="text-of-text-dim">×</span>
          <input
            type="number"
            value={frameH}
            onChange={(e) => setFrameH(parseInt(e.target.value))}
            className="w-16 input-field text-center"
          />
          <button
            onClick={() => currentProject && sliceAsset(currentProject.id, selectedAsset.id, frameW, frameH)}
            className="btn-primary px-3"
          >
            Apply Slice
          </button>
        </div>
        
        <div className="h-6 w-[1px] bg-of-border mx-2" />

        <div className="flex items-center gap-4">
          <button
            onClick={togglePlay}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-of-accent hover:bg-of-accent-light text-of-bg-900 transition-colors"
          >
            {isPlaying ? '⏸' : '▶'}
          </button>
          <div className="flex flex-col">
            <span className="text-[10px] text-of-text-dim uppercase font-bold">Playback</span>
            <span className="text-xs text-of-text">{fps} FPS</span>
          </div>
        </div>
      </div>

      {/* Workspace Area */}
      <div className="flex-1 grid grid-cols-2 overflow-hidden">
        {/* Left: Source Sheet */}
        <div className="border-r border-of-border p-8 overflow-auto flex items-center justify-center bg-of-bg-950 relative">
          <div className="relative group">
            <img
              src={`/api/projects/${currentProject?.id}/assets/${selectedAsset.id}/raw`} // Mock raw endpoint
              alt="Source"
              className="max-w-full h-auto border border-of-border shadow-2xl"
              style={{ imageRendering: 'pixelated' }}
            />
            {/* Grid Overlay */}
            <div 
              className="absolute inset-0 pointer-events-none opacity-20"
              style={{
                backgroundImage: `linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)`,
                backgroundSize: `${frameW}px ${frameH}px`
              }}
            />
          </div>
          <span className="absolute top-4 left-4 text-[10px] text-of-text-dim uppercase tracking-widest bg-of-bg-800 px-2 py-1 rounded">
            Source Sheet
          </span>
        </div>

        {/* Right: Preview */}
        <div className="p-8 flex items-center justify-center bg-of-bg-900 relative">
          <div className="panel p-8 flex items-center justify-center bg-of-bg-800 shadow-of-glow">
            <div 
              className="overflow-hidden border border-of-border"
              style={{
                width: frameW * 4,
                height: frameH * 4,
                backgroundImage: `url(/api/projects/${currentProject?.id}/assets/${selectedAsset.id}/raw)`,
                backgroundSize: 'auto 400%', // Rough zoom simulation
                backgroundPosition: `-${(currentFrame % 4) * frameW * 4}px -${Math.floor(currentFrame / 4) * frameH * 4}px`, // Simplified math
                imageRendering: 'pixelated'
              }}
            />
          </div>
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-1">
            {Array.from({ length: selectedAsset.metadata.frames || 0 }).map((_, i) => (
              <div 
                key={i}
                className={`w-1.5 h-1.5 rounded-full transition-all duration-150 ${i === currentFrame ? 'bg-of-accent scale-125' : 'bg-of-border'}`}
              />
            ))}
          </div>
          <span className="absolute top-4 left-4 text-[10px] text-of-text-dim uppercase tracking-widest bg-of-bg-800 px-2 py-1 rounded">
            Animation Preview
          </span>
        </div>
      </div>
    </div>
  );
}
