import React, { useEffect, useState } from 'react';
import { useConfigStore, GlobalConfig } from '../store/configStore';
import { FiSave, FiServer, FiFolder, FiLock } from 'react-icons/fi';

const SettingsWorkspace: React.FC = () => {
  const { config, isLoading, error, fetchConfig, updateConfig } = useConfigStore();
  const [localConfig, setLocalConfig] = useState<Partial<GlobalConfig>>({});

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  useEffect(() => {
    if (config) {
      setLocalConfig(config);
    }
  }, [config]);

  const handleSave = async () => {
    await updateConfig(localConfig);
    alert("Impostazioni salvate con successo!");
  };

  const handleChange = (key: keyof GlobalConfig, value: string | number) => {
    setLocalConfig(prev => ({ ...prev, [key]: value }));
  };

  if (isLoading && !config) return <div className="p-8 text-of-text-muted">Caricamento configurazione...</div>;

  return (
    <div className="flex-1 flex flex-col h-full bg-of-bg">
      <header className="p-6 border-b border-of-border flex justify-between items-center bg-of-bg-sidebar/50">
        <div>
          <h1 className="text-2xl font-bold text-of-text">Impostazioni Globali</h1>
          <p className="text-of-text-muted text-sm">Configura API, percorsi e parametri di sistema.</p>
        </div>
        <button 
          onClick={handleSave}
          disabled={isLoading}
          className="flex items-center gap-2 bg-of-accent hover:bg-of-accent-hover text-white px-4 py-2 rounded-md transition-all font-medium disabled:opacity-50"
        >
          <FiSave /> {isLoading ? 'Salvataggio...' : 'Salva Modifiche'}
        </button>
      </header>

      <main className="flex-1 overflow-auto p-8 max-w-4xl mx-auto w-full space-y-8 pb-20">
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md">
            Errore: {error}
          </div>
        )}

        {/* --- Server Section --- */}
        <section className="space-y-6 bg-of-surface p-6 rounded-xl border border-of-border">
          <div className="flex items-center gap-2 text-of-accent font-semibold text-lg border-b border-of-border pb-3">
            <FiServer /> Parametri Server
          </div>
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Backend Port</label>
              <input 
                type="number" 
                value={localConfig.BACKEND_PORT || ''} 
                onChange={(e) => handleChange('BACKEND_PORT', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Bridge Port (Godot)</label>
              <input 
                type="number" 
                value={localConfig.BRIDGE_PORT || ''} 
                onChange={(e) => handleChange('BRIDGE_PORT', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
          </div>
        </section>

        {/* --- AI API Section --- */}
        <section className="space-y-6 bg-of-surface p-6 rounded-xl border border-of-border">
          <div className="flex items-center gap-2 text-of-accent font-semibold text-lg border-b border-of-border pb-3">
            <FiLock /> Chiavi API & AI
          </div>
          <div className="space-y-5">
            <div className="space-y-2">
              <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">OpenAI API Key</label>
              <input 
                type="password" 
                value={localConfig.OPENAI_API_KEY || ''} 
                placeholder="sk-..."
                onChange={(e) => handleChange('OPENAI_API_KEY', e.target.value)}
                className="input-field font-mono"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">ComfyUI Server URL</label>
              <input 
                type="text" 
                value={localConfig.COMFYUI_URL || ''} 
                onChange={(e) => handleChange('COMFYUI_URL', e.target.value)}
                className="input-field"
              />
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">ElevenLabs Key</label>
                <input 
                  type="password" 
                  value={localConfig.ELEVENLABS_API_KEY || ''} 
                  onChange={(e) => handleChange('ELEVENLABS_API_KEY', e.target.value)}
                  className="input-field"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Replicate Key</label>
                <input 
                  type="password" 
                  value={localConfig.REPLICATE_API_KEY || ''} 
                  onChange={(e) => handleChange('REPLICATE_API_KEY', e.target.value)}
                  className="input-field"
                />
              </div>
            </div>
          </div>
        </section>

        {/* --- Storage Section --- */}
        <section className="space-y-6 bg-of-surface p-6 rounded-xl border border-of-border">
          <div className="flex items-center gap-2 text-of-accent font-semibold text-lg border-b border-of-border pb-3">
            <FiFolder /> Percorsi & Archiviazione
          </div>
          <div className="space-y-5">
            <div className="space-y-2">
              <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Projects Directory</label>
              <input 
                type="text" 
                value={localConfig.PROJECTS_DIR || ''} 
                onChange={(e) => handleChange('PROJECTS_DIR', e.target.value)}
                className="input-field font-mono"
              />
              <p className="text-[10px] text-of-text-muted italic px-1">Modificare questo percorso sposterà il punto di ricerca dei progetti al prossimo riavvio.</p>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Max Versioni Asset</label>
                <input 
                  type="number" 
                  value={localConfig.MAX_ASSET_VERSIONS || ''} 
                  onChange={(e) => handleChange('MAX_ASSET_VERSIONS', parseInt(e.target.value))}
                  className="input-field"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase text-of-text-muted font-bold tracking-wider">Soglia Quality Gate</label>
                <input 
                  type="number" 
                  value={localConfig.QUALITY_GATE_THRESHOLD || ''} 
                  onChange={(e) => handleChange('QUALITY_GATE_THRESHOLD', parseInt(e.target.value))}
                  className="input-field"
                />
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default SettingsWorkspace;
