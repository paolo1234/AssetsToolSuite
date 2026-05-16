# WF01 — Core & Project Manager

> **Prerequisiti:** Nessuno (prima fase)
> **Moduli:** MOD00 (Project Manager)
> **Output:** Backend FastAPI funzionante, Frontend Electron+React con layout, sistema manifest SSOT

---

## Scope

Questa fase costruisce le fondamenta dell'intera suite:
1. Backend Python/FastAPI con WebSocket server
2. Sistema manifest SSOT (Single Source of Truth)
3. Asset versioning (max 10 versioni, rollback 1-click)
4. Frontend Electron + React + Zustand con CSS Grid layout rigido
5. Tag system per gli asset
6. Rilevamento conflitti su disco (hash MD5)

---

## Backend — Specifiche

### main.py
- FastAPI app con CORS abilitato per `http://localhost:*`
- WebSocket endpoint su `/ws` per aggiornamenti real-time al frontend
- WebSocket server separato sulla porta 47832 per il Godot Bridge (preparazione)
- Startup: verifica che la cartella di lavoro esista

### config.py
- Dataclass `Settings` con:
  - `BACKEND_PORT`: 47831
  - `BRIDGE_PORT`: 47832
  - `PROJECTS_DIR`: `~/OmniForge/projects`
  - `MAX_ASSET_VERSIONS`: 10
  - `QUALITY_GATE_THRESHOLD`: 70
  - API keys (opzionali, da .env)

### project/manifest.py
- Classe `ProjectManifest` che gestisce `omniforge.project.json`
- Metodi: `create()`, `load()`, `save()`, `add_asset()`, `remove_asset()`, `update_asset()`, `get_asset_by_id()`, `get_assets_by_tag()`, `check_disk_conflicts()`
- Calcolo hash MD5 per ogni asset per rilevamento conflitti
- Validazione schema all'apertura

### project/versioning.py
- Classe `AssetVersionManager`
- Salva fino a 10 versioni di ogni asset in `{project}/.versions/{asset_id}/`
- Metodi: `create_version()`, `rollback()`, `get_history()`, `cleanup_old()`
- Ogni versione = copia del file + snapshot dei metadati nel manifest

### routers/project.py
- `POST /api/projects` — Crea nuovo progetto
- `GET /api/projects` — Lista progetti
- `GET /api/projects/{id}` — Dettagli progetto
- `PUT /api/projects/{id}` — Aggiorna settings progetto
- `DELETE /api/projects/{id}` — Elimina progetto
- `POST /api/projects/{id}/assets` — Aggiungi asset
- `GET /api/projects/{id}/assets` — Lista asset (con filtri tag/categoria)
- `PUT /api/projects/{id}/assets/{asset_id}` — Aggiorna asset
- `DELETE /api/projects/{id}/assets/{asset_id}` — Rimuovi asset
- `POST /api/projects/{id}/assets/{asset_id}/rollback` — Rollback versione
- `GET /api/projects/{id}/conflicts` — Check conflitti disco

### adapters/base.py
- ABC `AIAdapter` con metodi astratti:
  - `async generate(prompt, params) -> GenerationResult`
  - `async check_health() -> bool`
  - `get_name() -> str`
  - `get_supported_params() -> list[str]`

---

## Frontend — Specifiche

### Scaffolding
- Vite + React 18 + TypeScript strict
- Electron wrapper
- Zustand per stato globale
- Tailwind CSS v3 con config custom (colori dark theme)
- Konva.js (installato, usato dai workspace successivi)

### Layout System (WorkspaceLayout.tsx)
```
┌──────────────────────────────────────────────┐
│  TopBar (project name, workspace tabs)        │
├────────┬─────────────────────┬───────────────┤
│Sidebar │     Canvas/Main     │   Inspector   │
│ 250px  │     flex: 1         │    300px      │
│        │                     │               │
│        │                     │               │
├────────┴─────────────────────┴───────────────┤
│  StatusBar (connection, progress, messages)    │
└──────────────────────────────────────────────┘
```
- CSS Grid: `grid-template-columns: 250px 1fr 300px`
- Sidebar, canvas e inspector sono regioni fisse, MAI flottanti
- Solo i modali possono usare `position: absolute/fixed`
- Sidebar collassabile con animazione

### Store (projectStore.ts)
- Stato: `currentProject`, `assets`, `selectedAsset`, `isLoading`, `error`
- Actions: `createProject()`, `loadProject()`, `addAsset()`, `deleteAsset()`, `rollbackAsset()`
- Tutti comunicano col backend via fetch/WebSocket

### App.tsx
- Router con workspace tabs: Image, Animation, Audio, UI, Checker, Moveset, StateMachine, Cutscene, Library
- Il workspace attivo occupa l'area canvas del layout
- Welcome screen se nessun progetto aperto

---

## Checklist Implementazione

- [ ] Creare `omniforge/backend/main.py`
- [ ] Creare `omniforge/backend/config.py`
- [ ] Creare `omniforge/backend/project/__init__.py`
- [ ] Creare `omniforge/backend/project/manifest.py`
- [ ] Creare `omniforge/backend/project/versioning.py`
- [ ] Creare `omniforge/backend/routers/__init__.py`
- [ ] Creare `omniforge/backend/routers/project.py`
- [ ] Creare `omniforge/backend/adapters/__init__.py`
- [ ] Creare `omniforge/backend/adapters/base.py`
- [ ] Creare `omniforge/backend/requirements.txt`
- [ ] Scaffolding frontend (Vite + React + Electron)
- [ ] `src/store/projectStore.ts`
- [ ] `src/layouts/WorkspaceLayout.tsx`
- [ ] `src/App.tsx`
- [ ] `electron/main.js`
- [ ] Verificare: `uvicorn main:app` parte
- [ ] Verificare: `npm run dev` lancia il frontend
- [ ] Verificare: CRUD progetto funzionante via API
