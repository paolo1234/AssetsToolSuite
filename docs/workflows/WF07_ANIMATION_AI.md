# WF07 — Animation Intelligence Layer

> **Prerequisiti:** WF03 completato
> **Moduli:** MOD13, MOD15, MOD16, MOD17
> **Output:** Animation coherence tools, Character DNA, Moveset Builder, State Machine editor

---

## Scope

### MOD13 — Animation Coherence Tools
- Frame Stabilizer: motion anchor + optical flow (OpenCV)
- Onion Skin Avanzato: 3 frame, ghost mode, difference mode
- Hitbox/Hurtbox Editor: overlay rettangoli, propagazione frame, export JSON
- Foot Planting Lock: ground contact frame, interpolazione correzione

### MOD15 — Character DNA System
- DNA Extraction Pipeline: palette, proporzioni, stile, silhouette hash
- DNA Lock: prompt injection automatico per coerenza
- DNA Drift Detector: confronto post-generazione
- DNA Editor: override manuale, snapshot `.omni-dna`, DNA merge

### MOD16 — Moveset Builder
- Moveset Definition System (JSON): animazioni con frames, fps, loop, directions
- Preset Library: platformer_basic, rpg_topdown, fighting_game, shmup_ship
- Direction Generator: mirror automatico + AI multi-direction
- Pose-First Workflow: key poses → inbetweening (AI/manual/morph)
- Batch Moveset Generation con coda asincrona

### MOD17 — Animation State Machine Preview
- State Machine Editor visuale (nodi = animazioni, frecce = transizioni)
- Export come Godot AnimationTree `.tres`
- Gamepad/Keyboard Live Preview (WASD → transizioni)
- Transition Smoothness Analyzer (score + suggerimenti)

---

## Backend Files

- `processors/dna.py` — CharacterDNA extraction, comparison, merge
- `processors/moveset.py` — Batch generation, direction mirror, inbetween
- `processors/state_machine.py` — Export AnimationTree .tres
- `library/moveset_presets.py` — Preset JSON per generi comuni

---

## Checklist

- [ ] `processors/dna.py`
- [ ] `processors/moveset.py`
- [ ] `processors/state_machine.py`
- [ ] `library/moveset_presets.py`
- [ ] Frontend: `MovesetWorkspace.tsx`
- [ ] Frontend: `StateMachineWorkspace.tsx`
- [ ] Frontend: DNA panel, moveset builder, state machine editor
- [ ] Frontend: gamepad/keyboard live preview
- [ ] Test: DNA extraction → lock → generazione coerente
- [ ] Test: export AnimationTree → importabile in Godot
