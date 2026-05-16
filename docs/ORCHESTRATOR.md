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
| WF01_CORE | 0 | ✅ DONE | Completato |
| WF02_AI_ADAPTERS | 1 | ✅ DONE | Completato |
| WF03_SPRITESHEET | 2 | ✅ DONE | Completato |
| WF04_AUDIO | 3 | ✅ DONE | Completato |
| WF05_BRIDGE | 5 | ✅ DONE | Completato |
| WF06_QUALITY | 4,6,7,8,9,10,11,12,14 | ✅ DONE | Completato |
| WF07_ANIMATION_AI | 13,15,16,17 | ✅ DONE | Completato |
| WF08_ADVANCED | 18,19,20 | ✅ DONE | Completato |
| WF10_SETTINGS | - | ✅ DONE | Gestione parametri globali |

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
| Configurazione API, porte, percorsi storage | WF10 | - |

---

## ComfyUI Workflow Presets

I workflow professionali sono in `comfy_workflows/` e vengono caricati automaticamente dall'adapter.

| Preset ID | Nome | Descrizione | Dimensione Default |
|---|---|---|---|
| `sprite_single` | Single Sprite | Personaggio, NPC, nemico singolo | 512x512 |
| `spritesheet_animation` | Spritesheet Animation | Sprite sheet animato (walk, attack, idle) | 1024x1024 |
| `background_tileable` | Tileable Background | Sfondo seamless per scene | 512x512 |
| `ui_icon_button` | UI Icon/Button | Elementi UI, icone, bottoni | 256x256 |
| `prop_item` | Props & Items | Oggetti, armi, artefatti | 512x512 |
| `tilemap_tileset` | Tileset | Tileset per tilemap | 256x256 |
| `vfx_particles` | VFX & Particles | Effetti particellari, spell | 512x512 |
| `character_portrait` | Character Portrait | Ritratti e volti | 512x512 |

**用法:** Passare `workflow_id` nei parametri di generazione.

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
│   │   ├── config_manager.py   # Gestione configurazioni
│   │   └── versioning.py        # Cronologia asset
│   ├── adapters/
│   │   ├── base.py              # AIAdapter ABC
│   │   ├── comfyui.py           # ComfyUI con workflow preset
│   │   └── dalle.py
│   ├── processors/
│   │   ├── image.py             # rembg, palette, pixel-art
│   │   ├── spritesheet.py       # packing, slicing, .tres
│   │   ├── audio.py             # pydub, loop points
│   │   ├── quality.py           # Quality gate
│   │   ├── logic.py             # Logica business
│   │   ├── cutscene.py          # Storyboard
│   │   └── .py
│   ├── bridge/
│   │   └── websocket_server.py
│   ├── exporters/
│   │   ├── generic.py
│   │   └── __init__.py
│   ├── routers/
│       ├── images.py
│       ├── animations.py
│       ├── audio.py
│       ├── quality.py
│       ├── logic.py
│       ├── library.py
│       ├── bridge.py
│       └── config.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── store/
│   │   ├── layouts/
│   │   │   └── WorkspaceLayout.tsx
│   │   └── workspaces/
│   │       ├── ImageWorkspace.tsx
│   │       ├── AnimationWorkspace.tsx
│   │       ├── AudioWorkspace.tsx
│   │       ├── CheckerWorkspace.tsx
│   │       ├── MovesetWorkspace.tsx
│   │       ├── StatesWorkspace.tsx
│   │       ├── CutsceneWorkspace.tsx
│   │       ├── LibraryWorkspace.tsx
│   │       └── SettingsWorkspace.tsx
│   └── electron/
│       └── main.js
├── godot_bridge/
│   ├── OmniForgeBridge.gd
│   └── ...
├── comfy_workflows/             # Workflow ComfyUI professionali
│   ├── sprite_single.json
│   ├── spritesheet_animation.json
│   ├── background_tileable.json
│   ├── ui_icon_button.json
│   ├── prop_item.json
│   ├── tilemap_tileset.json
│   ├── vfx_particles.json
│   └── character_portrait.json
```
