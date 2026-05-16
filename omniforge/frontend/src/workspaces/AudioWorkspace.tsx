/**
 * OmniForge — AudioWorkspace
 * AI Audio generation & Waveform editing.
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useAudioStore } from '../store/audioStore';

export default function AudioWorkspace() {
  const [prompt, setPrompt] = useState('');
  const { selectedAsset, currentProject } = useProjectStore();
  const { generateAudio, processAudio, isProcessing } = useAudioStore();

  const handleGenerate = () => {
    if (!currentProject || !prompt) return;
    generateAudio(currentProject.id, prompt);
  };

  const handleNormalize = () => {
    if (!currentProject || !selectedAsset) return;
    processAudio(currentProject.id, selectedAsset.id, [{ op: 'normalize', params: { target_dbfs: -3.0 } }]);
  };

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <div className="flex-1 flex gap-2">
          <input
            type="text"
            placeholder="Describe the sound effect... (e.g. '8-bit jump', 'sci-fi door')"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field max-w-2xl"
          />
          <button
            onClick={handleGenerate}
            disabled={isProcessing || !prompt}
            className="btn-primary disabled:opacity-50"
          >
            Generate SFX
          </button>
        </div>

        <div className="h-6 w-[1px] bg-of-border mx-2" />

        <div className="flex items-center gap-2">
          <button
            onClick={handleNormalize}
            className="px-3 py-1.5 rounded-md text-xs font-semibold bg-of-bg-700 hover:bg-of-surface-hover border border-of-border text-of-text transition-all"
          >
            Normalize
          </button>
          <button className="px-3 py-1.5 rounded-md text-xs font-semibold bg-of-bg-700 hover:bg-of-surface-hover border border-of-border text-of-text transition-all">
            Trim Ends
          </button>
        </div>
      </div>

      {/* Workspace Area */}
      <div className="flex-1 p-8 flex flex-col overflow-hidden">
        {selectedAsset ? (
          <div className="flex-1 flex flex-col gap-8">
            {/* Waveform Visualization (Mock) */}
            <div className="panel flex-1 bg-of-bg-950 flex flex-col relative overflow-hidden group">
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-5 group-hover:opacity-10 transition-opacity">
                <span className="text-[200px]">🔊</span>
              </div>
              
              {/* Fake Waveform */}
              <div className="flex-1 flex items-center justify-center gap-[2px] px-12">
                {Array.from({ length: 80 }).map((_, i) => {
                  const height = Math.random() * 80 + 10;
                  return (
                    <div 
                      key={i} 
                      className="w-1 bg-of-accent rounded-full transition-all duration-300"
                      style={{ height: `${height}%`, opacity: Math.random() * 0.5 + 0.5 }}
                    />
                  );
                })}
              </div>

              {/* Playback Progress */}
              <div className="h-1 bg-of-bg-700 relative">
                <div className="absolute top-0 left-0 bottom-0 w-1/3 bg-of-accent shadow-of-glow" />
              </div>

              <div className="h-12 bg-of-bg-800 border-t border-of-border flex items-center px-4 justify-between">
                <div className="flex items-center gap-4">
                  <button className="text-of-text hover:text-of-accent transition-colors">▶</button>
                  <span className="text-xs text-of-text-dim font-mono">00:01.2 / 00:04.5</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-of-text-dim uppercase font-bold">44.1kHz • 16-bit • WAV</span>
                </div>
              </div>
            </div>

            {/* Audio History / Variants */}
            <div className="h-48 flex gap-4 overflow-x-auto pb-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="panel min-w-[200px] bg-of-bg-800 p-3 flex flex-col justify-between hover:border-of-accent/50 transition-all cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] text-of-text-dim font-bold uppercase">Variant {i+1}</span>
                    <span className="text-xs opacity-0 group-hover:opacity-100 transition-opacity">⭐</span>
                  </div>
                  <div className="flex-1 flex items-center justify-center opacity-30 group-hover:opacity-60 transition-opacity">
                    <div className="flex gap-0.5 items-center">
                      {[12, 24, 18, 30, 15].map((h, j) => (
                        <div key={j} className="w-0.5 bg-of-text rounded-full" style={{ height: h }} />
                      ))}
                    </div>
                  </div>
                  <button className="mt-2 w-full py-1 rounded bg-of-bg-900 text-[10px] uppercase font-bold text-of-text-muted hover:text-of-text transition-colors">
                    Load
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-of-text-dim">
            <span className="text-6xl mb-4">🔊</span>
            <p className="text-lg">No audio asset selected.</p>
            <p className="text-sm">Generate a new sound or select one from the library.</p>
          </div>
        )}
      </div>
    </div>
  );
}
