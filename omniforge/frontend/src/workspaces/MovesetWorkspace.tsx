/**
 * OmniForge — MovesetWorkspace
 * Mapping animations to logic states (Idle, Run, Attack).
 */

import { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useLogicStore } from '../store/logicStore';

export default function MovesetWorkspace() {
  const { assets, currentProject } = useProjectStore();
  const { movesets } = useLogicStore();
  
  const states = ['Idle', 'Walk', 'Run', 'Attack', 'Jump', 'Fall', 'Hurt', 'Die'];

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <h2 className="text-sm font-bold text-of-text uppercase tracking-widest">Moveset Manager</h2>
        <div className="h-6 w-[1px] bg-of-border mx-2" />
        <button className="btn-primary px-3 py-1 text-xs">New Moveset</button>
      </div>

      {/* Main Area */}
      <div className="flex-1 p-8 overflow-auto">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Mapping Table */}
          <div className="panel bg-of-bg-800 overflow-hidden">
            <div className="p-4 border-b border-of-border bg-of-bg-900 flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-of-text">Character_Hero_v1</h3>
                <p className="text-xs text-of-text-dim">Mapping animations to logic states</p>
              </div>
              <button className="text-[10px] text-of-accent font-bold uppercase border border-of-accent/30 px-2 py-1 rounded hover:bg-of-accent/10 transition-colors">
                Export DNA
              </button>
            </div>
            
            <div className="divide-y divide-of-border">
              {states.map((state) => (
                <div key={state} className="grid grid-cols-[150px_1fr_120px] items-center p-4 hover:bg-of-bg-900/50 transition-colors group">
                  <span className="text-xs font-bold text-of-text-muted uppercase tracking-wider">{state}</span>
                  
                  <div className="px-4">
                    <select className="w-full bg-of-bg-900 border border-of-border text-xs text-of-text rounded px-3 py-2 focus:border-of-accent outline-none appearance-none cursor-pointer">
                      <option value="">None</option>
                      {assets.filter(a => a.category === 'Spritesheet').map(a => (
                        <option key={a.id} value={a.id}>{a.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-lg hover:scale-110 transition-transform">▶</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Character DNA Summary */}
          <div className="grid grid-cols-3 gap-6">
            <div className="panel p-4 bg-of-bg-800">
              <h4 className="text-[10px] text-of-text-dim uppercase font-bold mb-3">Collision Box</h4>
              <div className="aspect-square bg-of-bg-950 rounded border border-of-border relative flex items-center justify-center">
                <div className="w-12 h-20 border-2 border-of-accent shadow-of-glow opacity-50" />
              </div>
            </div>
            <div className="panel p-4 bg-of-bg-800">
              <h4 className="text-[10px] text-of-text-dim uppercase font-bold mb-3">Pivot Points</h4>
              <div className="aspect-square bg-of-bg-950 rounded border border-of-border relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-of-danger rounded-full shadow-of-glow" />
              </div>
            </div>
            <div className="panel p-4 bg-of-bg-800">
              <h4 className="text-[10px] text-of-text-dim uppercase font-bold mb-3">Logic Tags</h4>
              <div className="flex flex-wrap gap-2">
                {['Playable', 'Physics', 'Gravity', 'Invulnerable'].map(tag => (
                  <span key={tag} className="px-2 py-1 rounded bg-of-bg-900 border border-of-border text-[10px] text-of-text-muted">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
