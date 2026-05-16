# WF03 — Spritesheet & Animation Editor

> **Prerequisiti:** WF01, WF02 completati
> **Moduli:** MOD02 (Spritesheet & Animation Editor)
> **Output:** Spritesheet packer/slicer, animation player, export .tres per Godot

---

## Scope

1. Bin-packing ottimale con `rectpack` o griglia uniforme
2. Slicer: definisci griglia su spritesheet esistente
3. Animation Player su Konva.js (FPS 1-120, loop modes, onion skinning)
4. Export `.png` + `.tres` (SpriteFrames) per Godot
5. Spritesheet Diff per confronto versioni
6. FPS per singola animazione, loop in/out per animazione, frame hold

---

## Packer — Specifiche

### rectpack Algorithm
```python
from rectpack import newPacker

def pack_frames(frames: list[Image], method: str = "auto") -> PackResult:
    """
    method: "auto" (rectpack bin-packing) o "grid" (griglia uniforme)
    Returns: spritesheet image + frame rects JSON
    """
```
- Bin-packing: minimizza lo spazio vuoto nello spritesheet
- Griglia: tutte le celle hanno la stessa dimensione (pad con trasparente)
- Output: `.png` dello spritesheet + mappa delle coordinate di ogni frame

### Slicer
- Input: spritesheet esistente + definizione griglia (cols, rows, cell_size)
- Assegna nomi alle animation rows (es. row 0 = "idle", row 1 = "walk")
- Preview istantanea di ogni animazione estratta
- Validazione: avviso se i frame hanno dimensioni diverse

---

## Animation Player — Specifiche

### Canvas Konva.js
- Display del frame corrente con bordi del bounding box
- Controlli: play/pause, step forward/back, FPS slider (1-120)
- Loop modes: loop, ping-pong, once
- Timeline con frame thumbnails cliccabili

### Onion Skinning
- Mostra fino a 3 frame precedenti e 3 successivi
- Opacità decrescente (configurabile)
- Toggle on/off
- Ghost mode: solo contorno dei frame fantasma
- Difference mode: evidenzia solo i pixel che cambiano

### Pivot Point
- Visualizzato sul canvas come crosshair
- Drag per riposizionare
- Presets: center, bottom-center (feet), top-left
- Il pivot corrisponde esattamente a `offset` in Godot SpriteFrames

---

## Export Godot — Specifiche

### .tres Generator
```python
def export_sprite_frames(
    spritesheet_path: str,
    animations: dict[str, AnimationDef],
    output_path: str
) -> str:
    """
    Genera un file .tres (SpriteFrames resource) per Godot 4.x.
    Ogni AnimationDef contiene: frames, fps, loop_mode, loop_in, loop_out.
    """
```
- Formato `.tres` text-based (non binary) per leggibilità
- Nomi animazioni preservati
- FPS per animazione (non globale)
- Loop in/out points per animazione
- Frame hold: durata per-frame configurabile

### Spritesheet Diff
- Confronto visivo side-by-side di due versioni
- Evidenzia pixel diversi in overlay colorato
- Utile per rilevare regressioni dopo re-generazione

---

## API Endpoints

- `POST /api/spritesheet/pack` — Pack frame in spritesheet
- `POST /api/spritesheet/slice` — Slice spritesheet in frame
- `POST /api/spritesheet/export-tres` — Genera .tres per Godot
- `POST /api/spritesheet/diff` — Diff tra due spritesheet
- `GET /api/spritesheet/{id}/frames` — Lista frame di uno spritesheet

---

## Checklist

- [ ] `processors/spritesheet.py` (packer + slicer + .tres export)
- [ ] `routers/animation.py`
- [ ] Frontend: `AnimationWorkspace.tsx`
- [ ] Frontend: Animation player Konva.js
- [ ] Frontend: Onion skinning (normal + ghost + diff modes)
- [ ] Frontend: Pivot point editor
- [ ] Frontend: `animationStore.ts`
- [ ] Test: pack 20 frame → spritesheet ottimale
- [ ] Test: export .tres → importabile in Godot senza errori
- [ ] Test: diff tra due spritesheet → evidenzia differenze
