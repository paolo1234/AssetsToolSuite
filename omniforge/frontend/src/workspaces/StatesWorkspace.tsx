/**
 * OmniForge — StatesWorkspace
 * Visual State Machine Editor.
 */

import { useState } from 'react';

export default function StatesWorkspace() {
  const [nodes] = useState([
    { id: 'idle', name: 'IDLE', x: 100, y: 100 },
    { id: 'walk', name: 'WALK', x: 400, y: 100 },
    { id: 'run', name: 'RUN', x: 400, y: 300 },
    { id: 'attack', name: 'ATTACK', x: 100, y: 300 },
  ]);

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      {/* ToolBar */}
      <div className="h-14 border-b border-of-border flex items-center px-4 gap-4 bg-of-bg-800">
        <h2 className="text-sm font-bold text-of-text uppercase tracking-widest">State Machine</h2>
        <div className="h-6 w-[1px] bg-of-border mx-2" />
        <button className="btn-primary px-3 py-1 text-xs">Export to Godot</button>
      </div>

      {/* Editor Canvas */}
      <div className="flex-1 relative overflow-hidden bg-[radial-gradient(#1e222d_1px,transparent_1px)] bg-[size:20px_20px]">
        {/* Mock Nodes */}
        {nodes.map(node => (
          <div 
            key={node.id}
            className="absolute panel p-4 bg-of-bg-800 border-of-border hover:border-of-accent transition-all cursor-move shadow-xl"
            style={{ left: node.x, top: node.y, width: 140 }}
          >
            <div className="text-[10px] text-of-text-dim uppercase font-bold mb-2 tracking-tighter">State</div>
            <div className="text-xs font-bold text-of-text">{node.name}</div>
            
            <div className="mt-4 space-y-1">
              <div className="h-1.5 w-full bg-of-bg-900 rounded-full overflow-hidden">
                <div className="h-full w-2/3 bg-of-accent" />
              </div>
              <div className="flex justify-between text-[8px] text-of-text-dim uppercase">
                <span>Transition</span>
                <span>Active</span>
              </div>
            </div>

            {/* Ports */}
            <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-of-bg-700 border border-of-border rounded-full" />
            <div className="absolute -right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-of-bg-700 border border-of-border rounded-full" />
          </div>
        ))}

        {/* Mock Connections (SVG) */}
        <svg className="absolute inset-0 pointer-events-none w-full h-full">
          <path d="M 240 120 L 400 120" stroke="#4f46e5" strokeWidth="2" fill="none" strokeDasharray="4 4" className="animate-pulse" />
          <path d="M 470 140 L 470 300" stroke="#4f46e5" strokeWidth="2" fill="none" />
          <path d="M 400 320 L 240 320" stroke="#4f46e5" strokeWidth="2" fill="none" />
          <path d="M 170 300 L 170 140" stroke="#4f46e5" strokeWidth="2" fill="none" />
        </svg>

        {/* Inspector (Floating) */}
        <div className="absolute top-6 right-6 w-72 panel bg-of-bg-800/90 backdrop-blur-md p-4 border-of-border shadow-2xl">
          <h3 className="text-xs font-bold text-of-text mb-4 uppercase tracking-widest border-b border-of-border pb-2">Properties</h3>
          
          <div className="space-y-4">
            <div>
              <label className="text-[10px] text-of-text-dim uppercase font-bold block mb-1">State Name</label>
              <input type="text" value="IDLE" readOnly className="input-field py-1" />
            </div>
            
            <div>
              <label className="text-[10px] text-of-text-dim uppercase font-bold block mb-1">Animation</label>
              <select className="input-field py-1">
                <option>hero_idle_v1</option>
                <option>hero_run_v1</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-of-text-dim uppercase font-bold block mb-1">Transitions</label>
              <div className="space-y-1">
                <div className="p-2 bg-of-bg-900 rounded border border-of-border text-[10px] flex justify-between">
                  <span>To WALK</span>
                  <span className="text-of-accent">if speed {'>'} 0.1</span>
                </div>
                <div className="p-2 bg-of-bg-900 rounded border border-of-border text-[10px] flex justify-between">
                  <span>To ATTACK</span>
                  <span className="text-of-accent">on action_1</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
