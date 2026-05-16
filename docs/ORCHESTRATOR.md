# OmniForge — Orchestratore Agenti AI

## ISTRUZIONI PER L'AGENTE
Questo è il file di ingresso. Leggilo SEMPRE per primo.
1. Identifica il task richiesto dall'utente
2. Consulta la **Mappa Workflow** per trovare il workflow corretto
3. Leggi `docs/ARCHITECTURE.md` per i principi fondamentali
4. Leggi il workflow specifico in `docs/workflows/WFxx_NOME.md`
5. Se servono dettagli di un modulo, leggi `docs/modules/MODxx_NOME.md`
6. Implementa seguendo la checklist del workflow

> **REGOLA D'ORO**: Non leggere mai PROGETTO.md. Tutta l'informazione è stata decomposta nei file sotto `docs/`.

---

## Panoramica Progetto

**OmniForge** è una suite desktop locale per creazione, gestione e test di asset per videogiochi con integrazione nativa 1-click per Godot Engine 4.x.

| Componente | Tecnologia | Cartella |
|---|---|---|
| Backend | Python 3.11 + FastAPI | `omniforge/backend/` |
| Frontend | Electron + React + Zustand | `omniforge/frontend/` |
| Godot Bridge | GDScript 4 + WebSocket | `omniforge/godot_bridge/` |

---

## Mappa Workflow & Dipendenze

```
WF01_CORE ─────────┬──→ WF02_AI_ADAPTERS ──→ WF03_SPRITESHEET ──→ WF07_ANIMATION_AI ──→ WF08_ADVANCED
                    │                                │
                    ├──→ WF04_AUDIO                  │
                    │                                │
                    ├──→ WF05_BRIDGE                 │
                    │                                ▼
                    └──────────────────────────→ WF06_QUALITY
```

---

## Status Tracking

| Workflow | Moduli | Stato | Note |
|---|---|---|---|
| WF01_CORE | 0 | 🟡 IN_PROGRESS | Fase 1 — Core infra |
| WF02_AI_ADAPTERS | 1 | ⚪ NOT_STARTED | Richiede WF01 |
| WF03_SPRITESHEET | 2 | ⚪ NOT_STARTED | Richiede WF01, WF02 |
| WF04_AUDIO | 3 | ⚪ NOT_STARTED | Richiede WF01 |
| WF05_BRIDGE | 5 | ⚪ NOT_STARTED | Richiede WF01 |
| WF06_QUALITY | 4,6,7,8,9,10,11,12,14 | ⚪ NOT_STARTED | Richiede WF01-WF03 |
| WF07_ANIMATION_AI | 13,15,16,17 | ⚪ NOT_STARTED | Richiede WF03 |
| WF08_ADVANCED | 18,19,20 | ⚪ NOT_STARTED | Richiede WF07 |

---

## Routing per Tipo di Task

| Se l'utente chiede... | Leggi workflow... | Moduli coinvolti |
|---|---|---|
| Setup progetto, manifest, tag, versioni | WF01 | MOD00 |
| Generare immagini, inpainting, post-processing | WF02 | MOD01 |
| Spritesheet, animazioni, packing, slicing | WF03 | MOD02 |
| Audio, SFX, loop, musica | WF04 | MOD03 |
| Connessione Godot, preview live, sandbox | WF05 | MOD05 |
| UI mockup, tilemap, 9-patch | WF06 | MOD04 |
| Consistency check, palette audit, naming | WF06 | MOD06, MOD07 |
| Positioning, alignment, scale, resize | WF06 | MOD08, MOD11 |
| Quality gate, error recovery, seed tracking | WF06 | MOD09 |
| Style enforcement, palette enforcer, lighting | WF06 | MOD10 |
| Edge cleaning, artifact removal, fringe | WF06 | MOD12 |
| Context preview, shader preview, viewport sim | WF06 | MOD14 |
| Animation stabilization, hitbox, foot planting | WF07 | MOD13 |
| Character DNA, consistency lock, DNA merge | WF07 | MOD15 |
| Moveset builder, direction gen, batch | WF07 | MOD16 |
| State machine, gamepad preview, transitions | WF07 | MOD17 |
| Asset library, VFX, item animation, re-export | WF08 | MOD18 |
| Naming convention, multi-engine export | WF08 | MOD19 |
| Cutscene, storyboard, dialog portraits | WF08 | MOD20 |

---

## Glossario Rapido

| Termine | Significato |
|---|---|
| **SSOT** | Single Source of Truth — tutto nel manifest JSON |
| **DNA** | Fingerprint visivo di un personaggio (palette, proporzioni, stile) |
| **Quality Gate** | Controllo automatico qualità post-generazione (advisory, non bloccante) |
| **Moveset** | Set completo di animazioni per un personaggio |
| **Adapter** | Interfaccia comune per motori AI diversi (ComfyUI, DALL-E, etc.) |
| **Bridge** | Connessione WebSocket bidirezionale OmniForge ↔ Godot |
| **Sandbox** | Scena Godot isolata per preview — non tocca mai il progetto |

---

## Struttura Cartelle Progetto

```
omniforge/
├── backend/
│   ├── main.py                  # FastAPI + WebSocket
│   ├── config.py                # Settings globali
│   ├── project/
│   │   ├── manifest.py          # SSOT manifest
│   │   └── versioning.py        # Cronologia asset
│   ├── adapters/
│   │   ├── base.py              # AIAdapter ABC
│   │   ├── comfyui.py
│   │   ├── dalle.py
│   │   ├── replicate.py
│   │   └── audio/
│   │       ├── audioldm.py
│   │       └── elevenlabs.py
│   ├── processors/
│   │   ├── image.py             # rembg, palette, pixel-art
│   │   ├── spritesheet.py       # packing, slicing, .tres
│   │   ├── audio.py             # pydub, loop points
│   │   ├── checker.py           # Asset Consistency
│   │   ├── dna.py               # CharacterDNA
│   │   ├── moveset.py           # Batch generation
│   │   ├── state_machine.py     # AnimationTree export
│   │   └── cutscene.py          # Storyboard
│   ├── bridge/
│   │   └── websocket_server.py
│   ├── exporters/
│   │   ├── godot.py
│   │   ├── unity.py
│   │   ├── gamemaker.py
│   │   ├── phaser.py
│   │   └── generic.py
│   ├── library/
│   │   ├── moveset_presets.py
│   │   └── asset_library.py
│   └── routers/
│       ├── images.py
│       ├── animation.py
│       ├── audio.py
│       ├── ui_mockup.py
│       └── project.py
├── frontend/
│   ├── src/
│   │   ├── store/
│   │   ├── layouts/
│   │   │   └── WorkspaceLayout.tsx
│   │   ├── workspaces/
│   │   │   ├── ImageWorkspace.tsx
│   │   │   ├── AnimationWorkspace.tsx
│   │   │   ├── AudioWorkspace.tsx
│   │   │   ├── UIWorkspace.tsx
│   │   │   ├── CheckerWorkspace.tsx
│   │   │   ├── MovesetWorkspace.tsx
│   │   │   ├── StateMachineWorkspace.tsx
│   │   │   ├── CutsceneWorkspace.tsx
│   │   │   └── LibraryWorkspace.tsx
│   │   └── components/
│   └── electron/
│       └── main.js
└── godot_bridge/
    ├── OmniForgeBridge.gd
    ├── OmniForge_Sandbox.tscn
    └── README.md
```
