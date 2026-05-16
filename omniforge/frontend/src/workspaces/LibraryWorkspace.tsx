/**
 * OmniForge — Library Workspace
 * Global asset management, search, and export.
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';

export default function LibraryWorkspace() {
  const { assets, currentProject, selectAsset, selectedAsset } = useProjectStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('All');

  const categories = ['All', 'Background', 'Character', 'Spritesheet', 'Audio', 'UI'];

  const filteredAssets = assets.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'All' || a.category === filter;
    return matchesSearch && matchesFilter;
  });

  const handleExport = async () => {
    if (!currentProject) return;
    try {
      const res = await fetch(`/api/library/${currentProject.id}/export`, { method: 'POST' });
      const data = await res.json();
      alert(`Project exported to: ${data.path}`);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-16 border-b border-of-border flex items-center px-6 gap-6 bg-of-bg-800">
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search assets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-10"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-of-text-dim text-lg">🔍</span>
        </div>

        <div className="flex gap-2">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all border ${
                filter === cat 
                  ? 'bg-of-accent border-of-accent text-white' 
                  : 'bg-of-bg-900 border-of-border text-of-text-dim hover:text-of-text'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex-1" />

        <button 
          onClick={handleExport}
          className="btn-primary flex items-center gap-2 px-4 py-2"
        >
          <span>📦</span>
          <span>Global Export</span>
        </button>
      </div>

      {/* Grid Content */}
      <div className="flex-1 p-8 overflow-auto">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
          {filteredAssets.map(asset => (
            <div
              key={asset.id}
              onClick={() => selectAsset(asset)}
              className={`group flex flex-col cursor-pointer transition-all ${
                selectedAsset?.id === asset.id ? 'scale-105' : 'hover:scale-102'
              }`}
            >
              <div className={`aspect-square rounded-xl bg-of-bg-800 border-2 mb-3 overflow-hidden flex items-center justify-center relative transition-all ${
                selectedAsset?.id === asset.id ? 'border-of-accent shadow-of-glow' : 'border-of-border group-hover:border-of-border-focus'
              }`}>
                {asset.category === 'Audio' ? (
                  <span className="text-4xl">🔊</span>
                ) : (
                  <img src={`/api/projects/${currentProject?.id}/assets/${asset.id}/raw`} alt="" className="max-w-full max-h-full object-contain" />
                )}
                
                {/* Overlay Info */}
                <div className="absolute inset-0 bg-of-bg-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 backdrop-blur-sm">
                  <span className="text-[10px] font-bold uppercase text-white bg-of-accent px-2 py-0.5 rounded">
                    {asset.category}
                  </span>
                  <span className="text-[10px] text-white/80 font-mono">
                    {asset.metadata.resolution || 'N/A'}
                  </span>
                </div>
              </div>
              
              <div className="px-1">
                <p className="text-xs font-bold text-of-text truncate">{asset.name}</p>
                <div className="flex gap-1 mt-1 overflow-hidden">
                  {asset.tags.slice(0, 2).map(tag => (
                    <span key={tag} className="text-[8px] text-of-text-dim bg-of-bg-950 px-1.5 py-0.5 rounded border border-of-border">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}

          {/* Add New Mock */}
          <div className="aspect-square rounded-xl border-2 border-dashed border-of-border flex flex-col items-center justify-center gap-2 hover:border-of-accent/50 hover:bg-of-accent/5 transition-all cursor-pointer text-of-text-dim hover:text-of-accent">
            <span className="text-3xl">+</span>
            <span className="text-[10px] font-bold uppercase">Import</span>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-of-bg-950 border-t border-of-border flex items-center px-4 justify-between">
        <div className="flex items-center gap-4">
          <span className="text-[10px] text-of-text-dim uppercase font-bold">Project: {currentProject?.project_name}</span>
          <span className="text-of-border">|</span>
          <span className="text-[10px] text-of-text-dim uppercase font-bold">Total Assets: {assets.length}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
          <span className="text-[10px] text-of-text-dim uppercase font-bold">Bridge Connected</span>
        </div>
      </div>
    </div>
  );
}
