# WF08 — Advanced Features: Library, Export, Cutscene

> **Prerequisiti:** WF07 completato
> **Moduli:** MOD18, MOD19, MOD20
> **Output:** Asset Library, Multi-Engine Export, Cutscene & Storyboard tool

---

## Scope

### MOD18 — Asset Library & Non-Character Sprites
- Categorie: characters, enemies, items, projectiles, effects, environment, ui, audio
- Effect Animation Generator: particle, impact, loop effects, parametric VFX
- Item & Prop Animator: idle, collected/destroyed animations
- Re-Export with New Art: tracking master → stale detection → re-generate

### MOD19 — Naming Convention & Export Pipeline
- Template naming configurabile: `{category}_{character}_{animation}_{direction}_{frame}`
- Multi-Engine Export: Godot (.tres), Unity (.meta), GameMaker (.yy), Phaser (JSON), RPG Maker MZ, Generic JSON
- Versioned Export History: rollback, diff, notes

### MOD20 — Cutscene & Storyboard Tool
- Storyboard Builder: canvas a pannelli, sprite + sfondi + testo
- Cutscene Sequence Generator: beat narrativi → pose chiave → timeline
- Dialog Portrait Generator: espressioni (neutral, happy, angry, sad, surprised) con DNA lock

---

## Backend Files

- `processors/cutscene.py` — Storyboard, portrait generation
- `exporters/godot.py` — .tres SpriteFrames + AnimationTree
- `exporters/unity.py` — .meta + Atlas JSON
- `exporters/gamemaker.py` — .yy Sprite asset
- `exporters/phaser.py` — Atlas JSON array format
- `exporters/generic.py` — JSON standard
- `library/asset_library.py` — Gestione categorie e browse

---

## Checklist

- [ ] `processors/cutscene.py`
- [ ] `exporters/godot.py`, `unity.py`, `gamemaker.py`, `phaser.py`, `generic.py`
- [ ] `library/asset_library.py`
- [ ] Frontend: `CutsceneWorkspace.tsx`, `LibraryWorkspace.tsx`
- [ ] Frontend: Storyboard canvas, portrait generator
- [ ] Frontend: Multi-engine export dialog
- [ ] Test: export stesso asset in 5 formati engine
