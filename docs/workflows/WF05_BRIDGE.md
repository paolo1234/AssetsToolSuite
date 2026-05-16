# WF05 — Godot Live Bridge

> **Prerequisiti:** WF01 completato
> **Moduli:** MOD05 (Godot Live Bridge)
> **Output:** WebSocket bridge, OmniForgeBridge.gd AutoLoad, Sandbox scene, comandi JSON

---

## Scope

1. WebSocket server dedicato (porta 47832) per comunicazione con Godot
2. `OmniForgeBridge.gd` — AutoLoad script per Godot 4.x
3. `OmniForge_Sandbox.tscn` — Scena isolata per preview
4. Comandi JSON per preview sprite, audio, tilemap, UI
5. Garanzie di sicurezza: sandbox-only, fail silenzioso, toggle on/off

---

## Architettura

```
OmniForge (Backend)           Godot Engine
    │                              │
    │  ws://localhost:47832        │
    ├──────────────────────────────┤
    │                              │
    │  JSON commands ──────────→   │  OmniForgeBridge.gd (AutoLoad)
    │                              │       │
    │  ←────────────── JSON ack    │       ▼
    │                              │  OmniForge_Sandbox.tscn
    │                              │  (scena separata, mai toccata dal dev)
```

---

## Backend — bridge/websocket_server.py

### WebSocket Server
- Porta dedicata 47832 (separata dal frontend)
- Single client connection (un Godot alla volta)
- Heartbeat ogni 5 secondi per rilevare disconnessione
- Buffer comandi: se Godot non è connesso, i comandi vengono accodati (max 20)

### Comandi Supportati
```json
{ "cmd": "preview_sprite", "path": "res://omniforge/hero_run.tres", "animation": "run" }
{ "cmd": "preview_audio", "path": "res://omniforge/theme.ogg" }
{ "cmd": "preview_tilemap", "tileset": "res://omniforge/forest.tres", "map_data": [...] }
{ "cmd": "preview_ui", "scene_path": "res://omniforge/hud_mockup.tscn" }
{ "cmd": "reload_asset", "path": "res://omniforge/hero.png" }
{ "cmd": "preview_state_machine", "tree_path": "res://omniforge/hero_tree.tres" }
{ "cmd": "preview_cutscene", "sequence": [...] }
{ "cmd": "batch_import", "assets": ["hero_idle.tres", "hero_walk.tres"] }
{ "cmd": "close_preview" }
```

### File Sync
- Quando un asset viene esportato, il backend copia automaticamente il file nella cartella `res://omniforge/` del progetto Godot collegato
- Path del progetto Godot preso dal manifest

---

## Godot — OmniForgeBridge.gd

```gdscript
extends Node
## OmniForge Live Bridge — AutoLoad

@export var enabled: bool = true
@export var server_url: str = "ws://localhost:47832"

var _ws: WebSocketPeer
var _sandbox_scene: PackedScene
var _original_scene_path: String
```

### Comportamento
- Si connette al backend all'avvio (se enabled)
- Riceve comandi JSON, li parsa, li esegue
- **preview_sprite**: cambia scena alla sandbox, carica SpriteFrames, riproduce animazione
- **preview_audio**: crea AudioStreamPlayer, riproduce
- **close_preview**: ritorna alla scena originale
- **reload_asset**: invalida la cache della risorsa per forzare il reload
- Se il backend è offline → nessun crash, retry ogni 10 secondi
- Toggle ON/OFF con la variabile `enabled`

---

## Godot — OmniForge_Sandbox.tscn

Scena minimale con:
- `Node2D` root
- `Camera2D` centrata
- `Sprite2D` per preview asset
- `AnimatedSprite2D` per preview animazioni
- `AudioStreamPlayer` per preview audio
- `SubViewport` per preview UI
- Background: checkerboard pattern (trasparenza)

**Garanzia**: questa scena vive in `res://omniforge/` e non viene mai toccata dal dev. OmniForge la genera automaticamente al primo collegamento.

---

## Sicurezza

1. Il bridge opera SOLO nella sandbox scene
2. Tutti i file OmniForge vanno in `res://omniforge/`
3. `.gitignore` auto-generato per `res://omniforge/`
4. Se il backend è offline, il bridge fallisce silenziosamente
5. Nessuna modifica alle scene del progetto dell'utente

---

## Checklist

- [ ] `bridge/websocket_server.py`
- [ ] `godot_bridge/OmniForgeBridge.gd`
- [ ] `godot_bridge/OmniForge_Sandbox.tscn`
- [ ] `godot_bridge/README.md` (istruzioni installazione 1-click)
- [ ] File sync: export → copia in `res://omniforge/`
- [ ] Test: connessione WebSocket stabile
- [ ] Test: preview_sprite funzionante nella sandbox
- [ ] Test: close_preview torna alla scena originale
- [ ] Test: backend offline → nessun crash Godot
