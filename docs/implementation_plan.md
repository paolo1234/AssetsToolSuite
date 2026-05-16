# OmniForge — Implementation Plan

## Problem Statement

Il file `PROGETTO.md` (48KB, 885 righe) è troppo lungo per essere processato efficacemente da agenti AI durante lo sviluppo. Serve:

1. **Splitting** in file .MD modulari e focalizzati
2. **Orchestratore** centrale che coordina i workflow
3. **Implementazione** completa del progetto OmniForge

---

## Proposed Architecture: Documentation Split

Il monolite `PROGETTO.md` verrà sostituito da una struttura a 3 livelli:

```
AssetTools/
├── docs/
│   ├── ORCHESTRATOR.md          ← Entry point per ogni agente AI
│   ├── ARCHITECTURE.md          ← Principi, stack, regole codice
│   ├── workflows/
│   │   ├── WF01_CORE.md         ← Fase 1: Project Manager + FastAPI + Layout
│   │   ├── WF02_AI_ADAPTERS.md  ← Fase 2: AI Adapter Layer + Image Processor
│   │   ├── WF03_SPRITESHEET.md  ← Fase 3: Spritesheet Engine + Animation
│   │   ├── WF04_AUDIO.md        ← Fase 4: Audio Module
│   │   ├── WF05_BRIDGE.md       ← Fase 5: Godot Live Bridge
│   │   ├── WF06_QUALITY.md      ← Fase 6: Checker, Style, Edge, Scale
│   │   ├── WF07_ANIMATION_AI.md ← Fase 7: DNA, Moveset, State Machine
│   │   └── WF08_ADVANCED.md     ← Fase 8: Library, Export, Cutscene
│   └── modules/
│       ├── MOD00_PROJECT.md
│       ├── MOD01_IMAGE.md
│       ├── ...
│       └── MOD20_CUTSCENE.md
├── omniforge/                   ← Actual codebase
│   ├── backend/
│   ├── frontend/
│   └── godot_bridge/
└── PROGETTO.md                  ← Preserved as reference (read-only)
```

### File Sizing Target
- **ORCHESTRATOR.md**: ~200 righe (routing + status tracking)
- **ARCHITECTURE.md**: ~150 righe (principi + stack + regole)
- **Ogni WF**: ~300-400 righe (scope + spec + checklist)
- **Ogni MOD**: ~100-150 righe (spec dettagliata singolo modulo)

> [!IMPORTANT]
> Ogni file workflow è auto-contenuto: un agente AI può ricevere solo `ORCHESTRATOR.md` + il workflow specifico e avere tutto il contesto necessario per implementare quella fase.

---

## Proposed Changes

### Documentation Layer

#### [NEW] [ORCHESTRATOR.md](file:///c:/Users/calam/Documents/AssetTools/docs/ORCHESTRATOR.md)
Entry point per tutti gli agenti AI. Contiene:
- Mappa dei workflow con dipendenze
- Status tracking (NOT_STARTED → IN_PROGRESS → DONE)
- Istruzioni su quale workflow leggere per ogni tipo di task
- Glossario termini chiave (SSOT, DNA, Quality Gate, etc.)

#### [NEW] [ARCHITECTURE.md](file:///c:/Users/calam/Documents/AssetTools/docs/ARCHITECTURE.md)
Principi architetturali + stack tecnico + regole codice. Sempre incluso come contesto base.

#### [NEW] Workflow files (WF01-WF08)
Un file per fase di sviluppo. Ogni file contiene:
- Scope (quali moduli copre)
- Prerequisiti (quali WF devono essere completati)
- Specifiche tecniche dettagliate
- Checklist implementazione
- Test di verifica

#### [NEW] Module files (MOD00-MOD20)
Un file per modulo. Reference dettagliata per implementazione specifica.

---

### Codebase: Phase 1 — Core & Project Manager

#### [NEW] `omniforge/backend/main.py`
FastAPI app + WebSocket server + CORS

#### [NEW] `omniforge/backend/config.py`
Settings globali (porte, path, API keys)

#### [NEW] `omniforge/backend/project/manifest.py`
Lettura/scrittura `omniforge.project.json` (SSOT)

#### [NEW] `omniforge/backend/project/versioning.py`
Cronologia asset (max 10 versioni, rollback)

#### [NEW] `omniforge/backend/routers/project.py`
REST endpoints per Project Manager

#### [NEW] `omniforge/frontend/` (Electron + React + Zustand)
- `package.json` con dipendenze
- `src/store/projectStore.ts` — Zustand store per stato progetto
- `src/layouts/WorkspaceLayout.tsx` — CSS Grid rigido
- `src/App.tsx` — Entry point React
- `electron/main.js` — Entry Electron
- `tailwind.config.js` — Config custom

---

## Development Phases Summary

| Phase | Workflow | Modules | Dependencies |
|-------|----------|---------|-------------|
| 1 | WF01_CORE | 0 (Project Manager) | None |
| 2 | WF02_AI_ADAPTERS | 1 (Image Gen) | WF01 |
| 3 | WF03_SPRITESHEET | 2 (Spritesheet) | WF01, WF02 |
| 4 | WF04_AUDIO | 3 (Audio) | WF01 |
| 5 | WF05_BRIDGE | 5 (Godot Bridge) | WF01 |
| 6 | WF06_QUALITY | 4, 6, 7, 8, 9, 10, 11, 12, 14 | WF01-WF03 |
| 7 | WF07_ANIMATION_AI | 13, 15, 16, 17 | WF03 |
| 8 | WF08_ADVANCED | 18, 19, 20 | WF07 |

---

## Open Questions

> [!IMPORTANT]
> **Ordine di priorità**: Vuoi che implementi prima tutta la documentazione (orchestratore + workflow + moduli) e poi il codice? Oppure documentazione e codice della Fase 1 insieme?

> [!IMPORTANT]
> **Tailwind CSS**: Il progetto specifica Tailwind CSS. Quale versione preferisci? (v3 stable o v4 beta?)

> [!IMPORTANT]
> **Node.js / npm**: Hai Node.js installato? Quale versione? Serve per il frontend Electron+React.

> [!IMPORTANT]
> **Python**: Hai Python 3.11+ installato? Serve per il backend FastAPI.

> [!IMPORTANT]
> **Scope iniziale**: Data la vastità del progetto (20 moduli), vuoi che proceda fase per fase con approvazione intermedia, oppure che prepari solo la documentazione completa e poi implementiamo a blocchi?

---

## Verification Plan

### Per la documentazione
- Ogni workflow è auto-contenuto (un agente può lavorare con solo ORCHESTRATOR + WF specifico)
- Nessun workflow supera le 400 righe
- Le dipendenze tra workflow sono esplicite

### Per il codice (Fase 1)
- `uvicorn main:app --reload` parte senza errori
- `npm run dev` lancia il frontend Electron
- CRUD progetto funzionante via REST API
- Layout CSS Grid rendering corretto senza overlap
