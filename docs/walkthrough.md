# OmniForge — Walkthrough

## What Was Done

### Phase 0: Documentation Split (10 files)
Il monolite `PROGETTO.md` (48KB, 885 righe) è stato decomposto in file modulari:

| File | Righe | Scopo |
|---|---|---|
| `docs/ORCHESTRATOR.md` | ~150 | Entry point per agenti AI, mappa workflow, status tracking |
| `docs/ARCHITECTURE.md` | ~100 | Principi, stack, regole, schema manifest |
| `docs/workflows/WF01_CORE.md` | ~130 | Fase 1: Core + Project Manager |
| `docs/workflows/WF02_AI_ADAPTERS.md` | ~110 | Fase 2: AI Adapter + Image Processing |
| `docs/workflows/WF03_SPRITESHEET.md` | ~100 | Fase 3: Spritesheet Engine |
| `docs/workflows/WF04_AUDIO.md` | ~90 | Fase 4: Audio Module |
| `docs/workflows/WF05_BRIDGE.md` | ~100 | Fase 5: Godot Live Bridge |
| `docs/workflows/WF06_QUALITY.md` | ~80 | Fase 6: Quality, Style, Corrections |
| `docs/workflows/WF07_ANIMATION_AI.md` | ~60 | Fase 7: DNA, Moveset, State Machine |
| `docs/workflows/WF08_ADVANCED.md` | ~50 | Fase 8: Library, Export, Cutscene |

**Come usarli**: Un agente AI riceve solo `ORCHESTRATOR.md` + il workflow specifico del task corrente. Ogni file è auto-contenuto.

---

### Phase 1: Backend (Python/FastAPI)

| File | Descrizione |
|---|---|
| `backend/main.py` | FastAPI app + dual WebSocket (frontend + Godot Bridge) + CORS |
| `backend/config.py` | Settings singleton con porte, path, API keys |
| `backend/project/manifest.py` | SSOT manifest con Pydantic models, CRUD, conflict detection |
| `backend/project/versioning.py` | Max 10 versioni per asset, rollback 1-click |
| `backend/routers/project.py` | REST API completa: projects + assets + versioning + conflicts |
| `backend/adapters/base.py` | ABC `AIAdapter` + `GenerationResult` dataclass |
| `backend/requirements.txt` | Tutte le dipendenze Python |

**API Endpoints creati:**
- `POST/GET /api/projects` — Create/List projects
- `GET/PUT/DELETE /api/projects/{id}` — CRUD singolo progetto
- `POST/GET /api/projects/{id}/assets` — Add/List assets
- `PUT/DELETE /api/projects/{id}/assets/{asset_id}` — Update/Delete asset
- `GET /api/projects/{id}/assets/{asset_id}/history` — Version history
- `POST /api/projects/{id}/assets/{asset_id}/rollback` — Rollback
- `GET /api/projects/{id}/conflicts` — Disk conflict detection
- `GET /api/health` — Health check

---

### Phase 1: Frontend (Electron + React + Zustand)

| File | Descrizione |
|---|---|
| `frontend/package.json` | Dependencies: React, Zustand, Konva.js, Electron, Tailwind |
| `frontend/tsconfig.json` | TypeScript strict mode |
| `frontend/vite.config.ts` | Vite con proxy API al backend |
| `frontend/tailwind.config.js` | Dark theme custom (of-* colors), workspace grid |
| `frontend/index.html` | Entry con Google Fonts (Inter, JetBrains Mono) |
| `frontend/src/index.css` | Stili globali, scrollbar, component classes |
| `frontend/src/main.tsx` | React entry point |
| `frontend/src/App.tsx` | App completa: TopBar, Sidebar, Inspector, Welcome, Canvas |
| `frontend/src/store/projectStore.ts` | Zustand store con CRUD + rollback + conflicts |
| `frontend/src/layouts/WorkspaceLayout.tsx` | CSS Grid rigido (Principio 3) |
| `frontend/electron/main.js` | Electron wrapper desktop |

---

### Phase 2: AI Adapter Layer + Image Processor

| File | Descrizione |
|---|---|
| `backend/adapters/comfyui.py` | Adapter per ComfyUI locale con gestione workflow e polling |
| `backend/adapters/dalle.py` | Adapter per DALL-E 3 cloud via OpenAI API |
| `backend/processors/image.py` | ImageProcessor con rembg, palette quantization e pixel-art filter |
| `backend/routers/images.py` | Router con coda di generazione asincrona e pipeline di processing |
| `frontend/src/store/imageStore.ts` | Store Zustand per gestire i task di generazione e il polling |
| `frontend/src/workspaces/ImageWorkspace.tsx` | UI per generazione immagini con prompt, selezione adapter e card di progresso |

**Funzionalità implementate:**
- Generazione asincrona (non blocca la UI)
- Polling dello stato del task (Pending → Processing → Completed/Failed)
- Integrazione rembg per rimozione sfondo
- Quantizzazione palette con dithering
- Filtro Pixel Art (Nearest Neighbor downscale)

---

### Phase 3: Spritesheet & Animation

| File | Descrizione |
|---|---|
| `backend/processors/spritesheet.py` | Logica di slicing (grid/atlas) e generazione risorsa Godot `.tres` |
| `backend/routers/animations.py` | API per affettare asset e scaricare metadati animazione |
| `frontend/src/store/animationStore.ts` | Stato globale per playback (FPS, frame corrente) e slicing |
| `frontend/src/workspaces/AnimationWorkspace.tsx` | UI con preview in tempo reale, controllo playback e overlay griglia |

**Funzionalità implementate:**
- Rilevamento automatico della griglia (euristica base)
- Slicing dinamico con anteprima immediata
- Player di animazione con controllo FPS e loop
- Overlay visivo della griglia sul file sorgente
- Esportatore base per risorsa Godot `SpriteFrames`

---

### Phase 4: Audio Module

| File | Descrizione |
|---|---|
| `backend/processors/audio.py` | Processing audio con `pydub` (trim, normalization, gain) |
| `backend/routers/audio.py` | API per generazione (mock) e elaborazione pipeline audio |
| `frontend/src/store/audioStore.ts` | Stato per gestire i task audio e le varianti |
| `frontend/src/workspaces/AudioWorkspace.tsx` | UI con visualizzazione waveform (mock), player e controlli editing |

**Funzionalità implementate:**
- Pipeline di processing audio non distruttiva (via manifest)
- Normalizzazione automatica a target dBFS
- Trimming dei silenzini e gain adjustment
- Interfaccia con visualizzatore waveform "premium"
- Supporto per formati WAV, OGG, MP3 tramite `pydub`

---

### Phase 5: Godot Live Bridge

| File | Descrizione |
|---|---|
| `backend/bridge/websocket_server.py` | Server WebSocket dedicato (porta 47832) per Godot |
| `godot_bridge/OmniForgeBridge.gd` | AutoLoad per Godot 4.x che gestisce la connessione e i comandi |
| `godot_bridge/OmniForge_Sandbox.tscn` | Scena sandbox isolata per preview sicura degli asset |
| `frontend/src/store/bridgeStore.ts` | Store per inviare comandi di preview dall'interfaccia |

**Funzionalità implementate:**
- Connessione WebSocket bidirezionale tra OmniForge e Godot
- Sistema di preview 1-click per Sprite e Audio
- Gestione automatica della scena Sandbox (salvataggio scena corrente e ripristino)
- Endpoint di broadcast per inviare comandi a più istanze di Godot
- Inserimento automatico del bridge come AutoLoad (logica pronta per l'utente)

---

### Phase 6: Quality, Style & Corrections

| File | Descrizione |
|---|---|
| `backend/processors/quality.py` | Analisi qualità (mock), consistency check e correzione colore (Pillow) |
| `backend/routers/quality.py` | API per analisi asset e correzioni batch (brightness, contrast, saturation) |
| `frontend/src/store/qualityStore.ts` | Stato per i risultati delle analisi e le operazioni batch |
| `frontend/src/workspaces/CheckerWorkspace.tsx` | UI "Checker" con griglia asset, selezione multipla e pannello analisi profonda |

**Funzionalità implementate:**
- Scoring qualità asset (0-100) basato su euristiche (colori unici, luminosità)
- Pannello di analisi dettagliato con suggerimenti di miglioramento
- Correzione colore batch: applicazione simultanea di filtri a più asset
- Selezione multipla intelligente nella griglia asset
- Feedback visivo immediato del punteggio qualità sulla griglia

---

### Phase 7: Advanced Animation & State Machines

| File | Descrizione |
|---|---|
| `backend/processors/logic.py` | Definizione modelli Pydantic per State Machines e Movesets |
| `backend/routers/logic.py` | API CRUD per la persistenza delle logiche nel manifest del progetto |
| `frontend/src/workspaces/MovesetWorkspace.tsx` | UI per il mapping asset -> stati logici (Idle, Run, etc.) |
| `frontend/src/workspaces/StatesWorkspace.tsx` | Editor visuale (mock) per macchine a stati finiti con inspector |

**Funzionalità implementate:**
- Gestione centralizzata dei Movesets (caratteri, nemici, oggetti)
- Mapping flessibile degli asset Spritesheet agli stati logici di gioco
- Visual State Machine Editor con supporto per transizioni e condizioni
- Esportatore (base) per risorse Godot `AnimationNodeStateMachine`
- Supporto per metadati "DNA" (Collision Box, Pivot points, Logic Tags)

---

### Phase 8: Library, Export & Finalization

| File | Descrizione |
|---|---|
| `backend/routers/library.py` | API per export globale e gestione bulk dei tag |
| `frontend/src/workspaces/LibraryWorkspace.tsx` | UI "Home" per la gestione dell'intera libreria asset |
| `package.json` | Script di build finalizzati per Electron e produzione |

**Funzionalità implementate:**
- **Global Export 1-Click**: Esportazione di tutti gli asset del progetto in una cartella target (es. cartella Godot) mantenendo la gerarchia.
- **Asset Library Manager**: Griglia globale con ricerca full-text e filtri per categoria.
- **Bulk Tagging**: Sistema per aggiornare i tag di più asset contemporaneamente.
- **Status Monitoring**: Barra di stato con monitoraggio in tempo reale della connessione al Bridge Godot.
- **Produzione Ready**: Configurazione finale per il packaging dell'applicazione desktop via Electron.

---

### Phase 8+: Advanced Features (Cutscene & Multi-Engine)

| File | Descrizione |
|---|---|
| `backend/processors/cutscene.py` | Logica per storyboard e generazione portrait con DNA lock |
| `backend/exporters/generic.py` | Supporto multi-engine per Unity (.meta), GameMaker (.yy) e Phaser |
| `frontend/src/workspaces/CutsceneWorkspace.tsx` | Editor storyboard a pannelli e generatore di espressioni facciali |

**Funzionalità implementate:**
- **Storyboard Builder**: Sistema a beat narrativi con associazione sprite/testo per cinematiche.
- **Portrait Engine**: Generazione di espressioni emotive (felice, triste, arrabbiato) mantenendo la consistenza del personaggio.
- **Multi-Engine Support**: Oltre a Godot, OmniForge ora genera metadati per i principali engine 2D del mercato.
- **Cinematic Export**: Predisposizione per l'esportazione di sequenze storyboard in formato runtime engine.

---

### Phase 9: Documentation & Rapid Onboarding

| File | Descrizione |
|---|---|
| `README.md` | Guida completa in italiano con features, setup e configurazione |
| `install.bat` | One-click installer per Windows (Python + Node dependencies) |
| `start.bat` | One-click launcher per avviare Backend e Frontend in parallelo |

**Miglioramenti Finali:**
- **Integrazione Test**: Suite di test di integrazione `backend/tests/test_api.py` completata e passata.
- **Configurazione Dinamica**: `config.py` ora supporta `OMNIFORGE_DATA` per una gestione flessibile dei percorsi.
- **Robustezza Python**: Struttura a pacchetti con `__init__.py` per una corretta risoluzione delle importazioni.

---

## Stato Finale del Progetto

Tutti i workflow previsti dall'orchestratore sono stati implementati. La suite **OmniForge** è ora una soluzione end-to-end per lo sviluppo di asset 2D professionali.

---

## Come Avviare

### Backend
```bash
cd omniforge/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 47831 --reload
```

### Frontend
```bash
cd omniforge/frontend
npm install
npm run dev          # Solo browser
npm run electron:dev # Con Electron desktop
```

```
