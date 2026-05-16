# WF06 — Quality, Style & Correction Tools

> **Prerequisiti:** WF01, WF02, WF03
> **Moduli:** MOD04, MOD06, MOD07, MOD08, MOD09, MOD10, MOD11, MOD12, MOD14
> **Output:** UI/Tilemap mockup, Consistency Checker, Presets, Positioning, Quality Gate, Style Enforcer, Scale Manager, Edge Cleaner, Context Preview

---

## Scope

Questa fase raggruppa tutti i moduli di qualità, coerenza e correzione asset.

### MOD04 — UI/UX & Level Design Mockup
- Canvas Konva.js con griglia snap e guide magnetiche
- Font .ttf personalizzati con rendering identico a Godot
- 9-patch slicer: definisci margini NinePatchRect, preview stretching
- Tilemap Tester: griglia configurabile, preview parallax

### MOD06 — Asset Consistency Checker
- Palette Audit: scansiona sprite e rileva colori fuori palette
- Resolution Audit: verifica tile multipli della tile-size
- Naming Convention Check
- Godot Compatibility Check (FPS, formato audio, limiti GPU)
- Report HTML/PDF

### MOD07 — Template & Preset System
- Preset stile: "Pixel Art 16x16 RPG", "Vector 2D Platformer", etc.
- Template progetto starter (struttura Godot + manifest)
- Condivisione via file `.omnipreset`

### MOD08 — Smart Positioning & Alignment
- Visual Mass Centering (centroide reale pixel opachi)
- Multi-Asset Alignment Panel (baseline, centerline, distribuzione)
- Snap & Grid con sub-pixel correction
- Pixel-perfect mode (coordinate intere)

### MOD09 — Generation Error Recovery
- QualityGate: ResolutionCheck, TransparencyCheck, ArtifactDetector, StyleConsistencyScore
- Generation History & Seed Tracker, A/B comparison
- Partial Regeneration (keep good parts, inpainting localizzato)

### MOD10 — Style Enforcement Engine
- Style Bible (3-10 immagini master), Style Match Score
- Lighting Direction Lock
- Palette Enforcer (Soft/Hard/Adaptive modes)
- Cross-Asset Style Transfer

### MOD11 — Dimension & Scale Manager
- Character Scale Chart con unità di gioco
- Smart Resize Pipeline (Pixel Art vs HD vs Spritesheet)
- Canvas Normalization (auto-normalize, trim+padding, anchor-aware)

### MOD12 — Edge & Artifact Cleaner
- Fringe Remover, Edge Smoothing, Isolated Pixel Detector
- Alpha Threshold slider
- Background Leakage Detector
- Seam Fixer per inpainting

### MOD14 — Real-Time Context Preview
- Scene Context Compositor (screenshot Godot come background)
- Shader Preview (approssimazione WebGL degli shader Godot)
- Resolution & Viewport Simulator

---

## Checklist

- [ ] `processors/checker.py` — Consistency Checker
- [ ] `processors/image.py` — Extend con edge cleaning, palette enforcer
- [ ] `routers/ui_mockup.py`
- [ ] Frontend: `UIWorkspace.tsx`, `CheckerWorkspace.tsx`
- [ ] Frontend: 9-patch slicer, tilemap tester
- [ ] Frontend: Quality Gate UI, A/B comparison viewer
- [ ] Frontend: Style Bible panel, Scale Chart
