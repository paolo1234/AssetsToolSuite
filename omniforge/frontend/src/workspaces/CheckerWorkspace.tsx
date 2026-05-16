/**
 * OmniForge — CheckerWorkspace
 * Quality analysis, style consistency, and batch correction tools.
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useQualityStore } from '../store/qualityStore';

export default function CheckerWorkspace() {
  const { assets, currentProject, selectedAsset } = useProjectStore();
  const { analyzeAsset, lastAnalysis, isAnalyzing, applyBatchCorrection } = useQualityStore();
  
  const [brightness, setBrightness] = useState(1.0);
  const [contrast, setContrast] = useState(1.0);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleApplyBatch = () => {
    if (!currentProject || selectedIds.length === 0) return;
    applyBatchCorrection(currentProject.id, selectedIds, { brightness, contrast });
  };

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setSelectedIds(assets.map(a => a.id))}
            className="text-xs text-of-text-dim hover:text-of-text uppercase font-bold"
          >
            Select All
          </button>
          <span className="text-of-border">|</span>
          <span className="text-xs text-of-text font-bold">
            {selectedIds.length} Selected
          </span>
        </div>

        <div className="h-6 w-[1px] bg-of-border mx-2" />

        {/* Batch Controls */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-[10px] text-of-text-dim uppercase font-bold">Brightness</label>
            <input 
              type="range" min="0.5" max="1.5" step="0.1" 
              value={brightness} onChange={(e) => setBrightness(parseFloat(e.target.value))}
              className="w-24 accent-of-accent"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-[10px] text-of-text-dim uppercase font-bold">Contrast</label>
            <input 
              type="range" min="0.5" max="1.5" step="0.1" 
              value={contrast} onChange={(e) => setContrast(parseFloat(e.target.value))}
              className="w-24 accent-of-accent"
            />
          </div>
          <button 
            onClick={handleApplyBatch}
            disabled={selectedIds.length === 0}
            className="btn-primary px-3 py-1 text-xs disabled:opacity-40"
          >
            Apply Batch
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 grid grid-cols-[1fr_350px] overflow-hidden">
        {/* Asset Grid */}
        <div className="p-6 overflow-auto border-r border-of-border">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {assets.map((asset) => (
              <div 
                key={asset.id}
                onClick={() => toggleSelect(asset.id)}
                className={`panel p-2 cursor-pointer transition-all duration-150 relative ${
                  selectedIds.includes(asset.id) ? 'border-of-accent ring-1 ring-of-accent bg-of-accent/5' : 'hover:border-of-border-focus'
                }`}
              >
                <div className="aspect-square bg-of-bg-800 rounded mb-2 overflow-hidden flex items-center justify-center">
                  <img src={`/api/projects/${currentProject?.id}/assets/${asset.id}/raw`} alt="" className="max-w-full max-h-full object-contain" />
                </div>
                <p className="text-[10px] font-medium text-of-text truncate">{asset.name}</p>
                {asset.quality_score && (
                  <div className="absolute top-1 right-1 px-1 rounded bg-of-bg-950 text-[8px] font-bold text-of-accent">
                    {asset.quality_score}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Quality Analysis Panel */}
        <aside className="bg-of-bg-800 p-4 overflow-auto">
          <div className="panel-header mb-4">Quality Analysis</div>
          
          {selectedAsset ? (
            <div className="space-y-6">
              <button 
                onClick={() => currentProject && analyzeAsset(currentProject.id, selectedAsset.id)}
                disabled={isAnalyzing}
                className="w-full btn-primary py-2 text-sm disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing...' : 'Run Deep Analysis'}
              </button>

              {lastAnalysis && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <div className="flex items-end gap-2 mb-4">
                    <span className="text-4xl font-bold text-of-accent">{lastAnalysis.score}</span>
                    <span className="text-sm text-of-text-dim pb-1">/ 100 Quality Score</span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-[10px] text-of-text-dim uppercase font-bold mb-2 tracking-widest">Metrics</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {Object.entries(lastAnalysis.metrics).map(([key, val]) => (
                          <div key={key} className="bg-of-bg-900 p-2 rounded border border-of-border">
                            <p className="text-[8px] text-of-text-muted uppercase">{key}</p>
                            <p className="text-xs text-of-text font-mono">{String(val)}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-[10px] text-of-text-dim uppercase font-bold mb-2 tracking-widest">Suggestions</h4>
                      <ul className="space-y-1.5">
                        {lastAnalysis.suggestions.map((s, i) => (
                          <li key={i} className="text-xs text-of-text-muted flex gap-2">
                            <span className="text-of-accent">•</span> {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-of-text-dim text-center mt-12 italic">
              Select an asset to analyze quality
            </p>
          )}
        </aside>
      </div>
    </div>
  );
}
