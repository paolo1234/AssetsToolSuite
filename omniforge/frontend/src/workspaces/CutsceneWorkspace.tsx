/**
 * OmniForge — CutsceneWorkspace
 * Storyboard builder and portrait generator.
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';

export default function CutsceneWorkspace() {
  const { assets, currentProject } = useProjectStore();
  const [beats, setBeats] = useState([
    { id: '1', text: 'In a distant galaxy...', imageId: null },
    { id: '2', text: 'A hero rises from the dust.', imageId: null },
  ]);

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <h2 className="text-sm font-bold text-of-text uppercase tracking-widest">Storyboard Builder</h2>
        <div className="h-6 w-[1px] bg-of-border mx-2" />
        <button className="btn-primary px-3 py-1 text-xs">New Sequence</button>
        <button className="btn-secondary px-3 py-1 text-xs">Export Video (WIP)</button>
      </div>

      {/* Main Area */}
      <div className="flex-1 grid grid-cols-[1fr_300px] overflow-hidden">
        {/* Storyboard Timeline */}
        <div className="p-8 overflow-auto">
          <div className="flex flex-wrap gap-8 justify-center">
            {beats.map((beat, index) => (
              <div key={beat.id} className="flex flex-col gap-3 w-64 group">
                <div className="flex items-center justify-between px-1">
                  <span className="text-[10px] text-of-text-dim font-bold uppercase">Beat {index + 1}</span>
                  <button className="text-xs opacity-0 group-hover:opacity-100 transition-opacity">❌</button>
                </div>
                
                <div className="aspect-video bg-of-bg-950 rounded-lg border-2 border-of-border flex items-center justify-center relative overflow-hidden group-hover:border-of-accent transition-colors cursor-pointer">
                  <span className="text-of-text-dim text-3xl opacity-20">🖼️</span>
                  <div className="absolute inset-0 bg-of-bg-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button className="text-[10px] bg-of-accent text-white px-2 py-1 rounded font-bold uppercase">Choose Image</button>
                  </div>
                </div>

                <textarea
                  value={beat.text}
                  onChange={(e) => {
                    const newBeats = [...beats];
                    newBeats[index].text = e.target.value;
                    setBeats(newBeats);
                  }}
                  className="bg-of-bg-800 border border-of-border rounded p-3 text-xs text-of-text focus:border-of-accent outline-none resize-none h-24"
                  placeholder="Subtitle text..."
                />
              </div>
            ))}

            <button 
              onClick={() => setBeats([...beats, { id: Date.now().toString(), text: '', imageId: null }])}
              className="w-64 h-[350px] border-2 border-dashed border-of-border rounded-lg flex flex-col items-center justify-center gap-2 text-of-text-dim hover:border-of-accent hover:text-of-accent transition-all"
            >
              <span className="text-4xl">+</span>
              <span className="text-[10px] font-bold uppercase">Add Beat</span>
            </button>
          </div>
        </div>

        {/* Portrait Generator Side Panel */}
        <aside className="bg-of-bg-800 border-l border-of-border p-4 flex flex-col">
          <h3 className="text-xs font-bold text-of-text uppercase tracking-widest border-b border-of-border pb-2 mb-6">Portrait Engine</h3>
          
          <div className="flex-1 space-y-8">
            {/* Character Selection */}
            <div>
              <label className="text-[10px] text-of-text-dim uppercase font-bold block mb-2">Base Character</label>
              <select className="input-field py-2">
                <option value="">Select Character...</option>
                {assets.filter(a => a.category === 'Character').map(a => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>

            {/* Expression Grid */}
            <div>
              <label className="text-[10px] text-of-text-dim uppercase font-bold block mb-3">Expression Matrix</label>
              <div className="grid grid-cols-2 gap-3">
                {['Happy', 'Angry', 'Sad', 'Shocked'].map(exp => (
                  <div key={exp} className="panel p-3 bg-of-bg-900 border-of-border flex flex-col items-center justify-center gap-2 group cursor-pointer hover:border-of-accent transition-all">
                    <span className="text-xl opacity-40 group-hover:opacity-100 transition-opacity">🎭</span>
                    <span className="text-[10px] text-of-text-muted font-bold uppercase">{exp}</span>
                  </div>
                ))}
              </div>
            </div>

            <button className="w-full btn-primary py-3 text-sm flex items-center justify-center gap-2">
              <span>⚡</span>
              <span>Generate Expressions</span>
            </button>
          </div>

          <div className="mt-auto p-4 bg-of-bg-950 rounded-lg border border-of-border">
            <p className="text-[10px] text-of-text-dim italic leading-relaxed">
              * portrait generation uses **DNA Lock** to ensure consistent facial features across all emotional states.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
