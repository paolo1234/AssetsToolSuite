import { useState, useCallback } from 'react';
import { useProjectStore } from '../store/projectStore';

export default function LibraryWorkspace() {
  const { assets, currentProject, selectAsset, selectedAsset } = useProjectStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('All');
  const [tab, setTab] = useState<'browse' | 'import' | 'fix'>('browse');
  const [scanPath, setScanPath] = useState('');
  const [scanResult, setScanResult] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const [importing, setImporting] = useState(false);
  const [issues, setIssues] = useState<any[]>([]);
  const [fixing, setFixing] = useState(false);

  const categories = ['All', 'Background', 'Character', 'Spritesheet', 'Audio', 'UI', 'Imported'];

  const filteredAssets = assets.filter(a => {
    const ms = a.name.toLowerCase().includes(search.toLowerCase());
    const mf = filter === 'All' || a.category === filter;
    return ms && mf;
  });

  const handleScan = useCallback(async () => {
    if (!scanPath || !currentProject) return;
    setScanning(true);
    setScanResult(null);
    try {
      const res = await fetch(`/api/projects/${currentProject.id}/import/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: scanPath, recursive: true }),
      });
      if (!res.ok) throw new Error('Scan failed');
      setScanResult(await res.json());
    } catch (e: any) {
      alert(`Scan fallito: ${e.message}`);
    }
    setScanning(false);
  }, [scanPath, currentProject]);

  const handleImport = useCallback(async () => {
    if (!scanPath || !currentProject || !scanResult) return;
    setImporting(true);
    try {
      const res = await fetch(`/api/projects/${currentProject.id}/import/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: scanPath, recursive: true }),
      });
      if (!res.ok) throw new Error('Import failed');
      const data = await res.json();
      alert(`Importati ${data.imported} asset da progetto ${data.engine}`);
      window.location.reload();
    } catch (e: any) {
      alert(`Import fallito: ${e.message}`);
    }
    setImporting(false);
  }, [scanPath, currentProject, scanResult]);

  const handleCheckFixes = useCallback(async () => {
    if (!currentProject) return;
    setFixing(true);
    try {
      const res = await fetch(`/api/projects/${currentProject.id}/fix/check`);
      if (!res.ok) throw new Error('Check failed');
      const data = await res.json();
      setIssues(data.issues || []);
    } catch (e: any) {
      alert(`Check fallito: ${e.message}`);
    }
    setFixing(false);
  }, [currentProject]);

  const handleRunFixes = useCallback(async () => {
    if (!currentProject) return;
    setFixing(true);
    try {
      const res = await fetch(`/api/projects/${currentProject.id}/fix/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auto_rename: true, auto_convert: true }),
      });
      if (!res.ok) throw new Error('Fix failed');
      const data = await res.json();
      alert(`Riparati ${data.fixed} asset`);
      setIssues([]);
      window.location.reload();
    } catch (e: any) {
      alert(`Fix fallito: ${e.message}`);
    }
    setFixing(false);
  }, [currentProject]);

  const handleExport = async () => {
    if (!currentProject) return;
    try {
      const res = await fetch(`/api/library/${currentProject.id}/export`, { method: 'POST' });
      const data = await res.json();
      alert(`Progetto esportato in: ${data.path}`);
    } catch (e) { console.error(e); }
  };

  const tabs = [
    { id: 'browse' as const, label: '📁 Sfoglia', count: assets.length },
    { id: 'import' as const, label: '📥 Importa' },
    { id: 'fix' as const, label: `🔧 Ripara${issues.length ? ` (${issues.length})` : ''}` },
  ];

  return (
    <div className="flex flex-col h-full bg-of-bg-900">
      <div className="h-14 border-b border-of-border flex items-center px-6 gap-6 bg-of-bg-800">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded transition-all ${tab === t.id ? 'bg-of-accent text-white' : 'text-of-text-dim hover:text-of-text'}`}>
            {t.label}
          </button>
        ))}
        <div className="flex-1" />
        <button onClick={handleExport} className="btn-primary flex items-center gap-2 px-4 py-1.5 text-xs">
          📦 Export
        </button>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        {tab === 'browse' && (
          <div>
            <div className="flex gap-4 mb-6">
              <input type="text" placeholder="Search assets..." value={search}
                onChange={e => setSearch(e.target.value)} className="input-field flex-1 max-w-md" />
              <div className="flex gap-2">
                {categories.map(cat => (
                  <button key={cat} onClick={() => setFilter(cat)}
                    className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border transition-all ${filter === cat ? 'bg-of-accent border-of-accent text-white' : 'bg-of-bg-900 border-of-border text-of-text-dim hover:text-of-text'}`}>
                    {cat}
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-6">
              {filteredAssets.map(asset => (
                <div key={asset.id} onClick={() => selectAsset(asset)}
                  className={`group flex flex-col cursor-pointer transition-all ${selectedAsset?.id === asset.id ? 'scale-105' : 'hover:scale-102'}`}>
                  <div className={`aspect-square rounded-xl bg-of-bg-800 border-2 mb-3 overflow-hidden flex items-center justify-center relative transition-all ${selectedAsset?.id === asset.id ? 'border-of-accent shadow-of-glow' : 'border-of-border group-hover:border-of-border-focus'}`}>
                    {asset.type === 'audio' ? <span className="text-4xl">🔊</span> :
                      <img src={`/api/projects/${currentProject?.id}/assets/${asset.id}/raw`} alt="" className="max-w-full max-h-full object-contain" />}
                    <div className="absolute inset-0 bg-of-bg-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 backdrop-blur-sm">
                      <span className="text-[10px] font-bold uppercase text-white bg-of-accent px-2 py-0.5 rounded">{asset.category}</span>
                      <span className="text-[10px] text-white/80 font-mono">{asset.metadata?.resolution || ''}</span>
                    </div>
                  </div>
                  <p className="text-xs font-bold text-of-text truncate">{asset.name}</p>
                  <div className="flex gap-1 mt-1 overflow-hidden">
                    {asset.tags?.slice(0, 2).map(tag => (
                      <span key={tag} className="text-[8px] text-of-text-dim bg-of-bg-950 px-1.5 py-0.5 rounded border border-of-border">{tag}</span>
                    ))}
                  </div>
                </div>
              ))}
              <div className="aspect-square rounded-xl border-2 border-dashed border-of-border flex flex-col items-center justify-center gap-2 hover:border-of-accent/50 hover:bg-of-accent/5 transition-all cursor-pointer text-of-text-dim hover:text-of-accent"
                onClick={() => setTab('import')}>
                <span className="text-3xl">+</span>
                <span className="text-[10px] font-bold uppercase">Importa</span>
              </div>
            </div>
          </div>
        )}

        {tab === 'import' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="panel p-6 bg-of-bg-800">
              <h3 className="text-sm font-bold text-of-text mb-4">📥 Importa Asset da Progetto</h3>
              <div className="flex gap-3 mb-4">
                <input type="text" value={scanPath} onChange={e => setScanPath(e.target.value)}
                  placeholder="Percorso cartella progetto (es. C:\Progetti\MyGame)"
                  className="input-field flex-1 font-mono text-sm" />
                <button onClick={handleScan} disabled={scanning || !scanPath}
                  className="btn-primary px-4 disabled:opacity-50 whitespace-nowrap">
                  {scanning ? 'Scansiona...' : '🔍 Scansiona'}
                </button>
              </div>

              {scanResult && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-of-bg-900 p-3 rounded border border-of-border text-center">
                      <p className="text-2xl font-bold text-of-accent">{scanResult.total_assets}</p>
                      <p className="text-[10px] text-of-text-dim uppercase font-bold">Asset Trovati</p>
                    </div>
                    <div className="bg-of-bg-900 p-3 rounded border border-of-border text-center">
                      <p className="text-2xl font-bold text-of-accent">{scanResult.engine}</p>
                      <p className="text-[10px] text-of-text-dim uppercase font-bold">Motore Rilevato</p>
                    </div>
                    <div className="bg-of-bg-900 p-3 rounded border border-of-border text-center">
                      <p className="text-2xl font-bold text-of-accent">{scanResult.issues?.length || 0}</p>
                      <p className="text-[10px] text-of-text-dim uppercase font-bold">Problemi Trovati</p>
                    </div>
                  </div>

                  <div className="max-h-48 overflow-y-auto space-y-1">
                    {scanResult.assets?.slice(0, 50).map((a: any, i: number) => (
                      <div key={i} className="flex items-center gap-3 px-3 py-1.5 bg-of-bg-900 rounded text-xs text-of-text-dim">
                        <span className="w-6 text-center">{a.type === 'image' ? '🖼️' : a.type === 'audio' ? '🔊' : '📄'}</span>
                        <span className="flex-1 truncate">{a.path}</span>
                        <span className="text-[10px]">{a.size_kb} KB</span>
                      </div>
                    ))}
                  </div>

                  <button onClick={handleImport} disabled={importing}
                    className="w-full btn-primary py-3 text-sm disabled:opacity-50">
                    {importing ? 'Importazione in corso...' : `📥 Importa ${scanResult.importable?.length || 0} Asset nel Progetto`}
                  </button>
                </div>
              )}
            </div>

            <div className="panel p-6 bg-of-bg-800">
              <h3 className="text-sm font-bold text-of-text mb-2">💡 Progetti Supportati</h3>
              <p className="text-xs text-of-text-dim">Godot, Unity, GameMaker, Unreal, Phaser e generico. Lo scanner rileva automaticamente il motore e cataloga tutte le risorse.</p>
            </div>
          </div>
        )}

        {tab === 'fix' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="panel p-6 bg-of-bg-800">
              <h3 className="text-sm font-bold text-of-text mb-4">🔧 Riparazione Asset</h3>
              <div className="flex gap-3 mb-6">
                <button onClick={handleCheckFixes} disabled={fixing}
                  className="btn-primary px-4 disabled:opacity-50">
                  {fixing ? 'Controllo...' : '🔍 Controlla Problemi'}
                </button>
                <button onClick={handleRunFixes} disabled={fixing || issues.length === 0}
                  className="px-4 py-2 rounded-md text-xs font-bold uppercase bg-of-danger/20 text-of-danger border border-of-danger/30 hover:bg-of-danger/30 transition-all disabled:opacity-40">
                  🛠️ Auto-Ripara ({issues.length})
                </button>
              </div>

              {issues.length > 0 ? (
                <div className="space-y-2">
                  {issues.map((iss, i) => (
                    <div key={i}
                      className={`flex items-start gap-3 p-3 rounded border text-xs ${iss.severity === 'error' ? 'bg-red-900/20 border-red-500/30 text-red-400' : 'bg-yellow-900/20 border-yellow-500/30 text-yellow-400'}`}>
                      <span>{iss.severity === 'error' ? '❌' : '⚠️'}</span>
                      <div className="flex-1">
                        <p>{iss.message}</p>
                        {iss.suggested && <p className="text-[10px] mt-1 opacity-70">Suggerito: {iss.suggested}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-of-text-dim">
                  <span className="text-4xl block mb-3">✅</span>
                  <p className="text-sm">Nessun problema trovato</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="h-8 bg-of-bg-950 border-t border-of-border flex items-center px-4 justify-between">
        <span className="text-[10px] text-of-text-dim uppercase font-bold">Progetto: {currentProject?.project_name} | Asset: {assets.length}</span>
        <span className="text-[10px] text-of-text-dim uppercase font-bold">Bridge Connesso</span>
      </div>
    </div>
  );
}