# OmniForge — Architettura & Principi

> Questo file è il contesto di base. Va SEMPRE letto insieme al workflow specifico.

---

## Principi Architetturali

### Principio 1 — Single Source of Truth (SSOT)
Tutti gli asset vivono in un **Project Manifest** (`omniforge.project.json`). Ogni modulo legge e scrive solo da lì. Nessun modulo tiene stato proprio. Questo elimina disallineamenti tra moduli.

### Principio 2 — Preview Always Matches Export
Ogni previewer interno usa **esattamente** gli stessi parametri del file esportato (stessa risoluzione, stesso FPS, stesso pivot point). Il rendering del canvas interno è pixel-perfect. Ciò che vedi = ciò che Godot riceve.

### Principio 3 — UI Layout System Rigido
Il frontend usa un **layout a pannelli bloccati** (simile a Blender/DaVinci): nessun elemento flottante libero. Ogni workspace ha regioni CSS Grid fisse: `sidebar | canvas | inspector`. Mai `position: absolute` fuori dai modali.

### Principio 4 — Adapter Pattern per AI
Ogni motore AI (ComfyUI, DALL-E, Replicate) implementa la stessa interfaccia `AIAdapter`. Cambiare provider = cambiare un valore nel manifest. Zero riscritture.

---

## Stack Tecnico

| Layer | Tecnologia | Motivo |
|---|---|---|
| Backend | Python 3.11 + FastAPI + Uvicorn | Async nativo, ecosistema AI |
| WebSocket | FastAPI WebSocket + `asyncio` | Bassa latenza per Live Bridge |
| Image Processing | Pillow, OpenCV, `rembg`, `rectpack` | Pipeline completa |
| Audio Processing | `pydub`, `librosa` | Pitch/reverb/loop |
| Frontend | Electron + React + Zustand | Desktop-first, stato globale |
| Canvas | Konva.js (2D) | Spritesheet editor, inpainting mask |
| Styling | Tailwind CSS con config custom | Nessun conflitto di stile |
| Godot Bridge | GDScript 4 + WebSocket nativo | Zero dipendenze esterne |
| Persistenza | SQLite (via SQLAlchemy) + JSON manifest | Progetti portabili |

---

## Regole Fondamentali per il Codice

1. **Nessun stato locale nei moduli** — tutto passa per il manifest o lo store Zustand
2. **Preview = Export** — ogni renderer usa identici parametri, zero discrepanze
3. **Layout CSS Grid immutabile** — `position: absolute` solo dentro `[role="dialog"]`
4. **Fail silenzioso verso Godot** — il bridge non crasha mai il gioco in caso di errore
5. **Ogni funzione ha un tipo di ritorno esplicito** — Python type hints + TypeScript strict mode
6. **Test di integrazione obbligatori** per ogni adapter AI (mock responses inclusi)
7. **Quality Gate non bloccante** — avvisa ma non impedisce mai all'utente di procedere
8. **Operazioni distruttive richiedono conferma** + backup automatico nella cronologia versioni
9. **Preview always live** — qualsiasi modifica si vede in tempo reale, senza cliccare "applica"
10. **Undo/Redo globale a 50 step** per ogni workspace
11. **Ogni correzione è non-distruttiva** fino all'export — l'immagine sorgente è preservata

---

## Manifest Schema (omniforge.project.json)

```json
{
  "version": "1.0",
  "project_name": "My Game",
  "target_resolution": { "width": 320, "height": 180 },
  "tile_size": 16,
  "base_fps": 12,
  "godot_project_path": "/path/to/godot/project",
  "palette_reference": "palette.gpl",
  "light_direction_degrees": 30,
  "naming_convention": "{category}_{name}_{variant}",
  "style_bible_images": [],
  "assets": [
    {
      "id": "uuid",
      "name": "hero_idle",
      "type": "spritesheet",
      "category": "character",
      "tags": ["player", "hero"],
      "file_path": "assets/hero_idle.png",
      "hash_md5": "abc123...",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z",
      "version": 1,
      "metadata": {
        "frames": 4,
        "fps": 8,
        "pivot": { "x": 32, "y": 60 },
        "loop_mode": "ping-pong"
      },
      "dna_id": null,
      "quality_score": 85
    }
  ],
  "presets": {},
  "export_history": []
}
```

---

## Comunicazione Backend ↔ Frontend

| Tipo | Protocollo | Uso |
|---|---|---|
| CRUD assets/projects | REST (HTTP) | Operazioni standard |
| Preview live, progress | WebSocket | Aggiornamenti tempo reale |
| File upload | REST multipart | Importazione asset |

**Base URL Backend:** `http://localhost:47831`
**WebSocket Bridge Godot:** `ws://localhost:47832`
**WebSocket Frontend:** `ws://localhost:47831/ws`
