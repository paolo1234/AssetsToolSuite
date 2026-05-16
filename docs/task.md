# OmniForge — Task Tracker

## Phase 0: Documentation Split
- [x] Create ORCHESTRATOR.md
- [x] Create ARCHITECTURE.md
- [x] Create WF01_CORE.md
- [x] Create WF02_AI_ADAPTERS.md
- [x] Create WF03_SPRITESHEET.md
- [x] Create WF04_AUDIO.md
- [x] Create WF05_BRIDGE.md
- [x] Create WF06_QUALITY.md
- [x] Create WF07_ANIMATION_AI.md
- [x] Create WF08_ADVANCED.md

## Phase 1: Core & Project Manager (Backend)
- [x] backend/main.py — FastAPI + WebSocket + Godot Bridge
- [x] backend/config.py — Settings singleton
- [x] backend/project/manifest.py — SSOT manifest with Pydantic
- [x] backend/project/versioning.py — Asset versioning (10 versions)
- [x] backend/routers/project.py — REST endpoints (CRUD + rollback + conflicts)
- [x] backend/adapters/base.py — AIAdapter ABC
- [x] backend/requirements.txt

## Phase 1: Core & Project Manager (Frontend)
- [x] Frontend scaffolding (Vite + React + TypeScript)
- [x] package.json + tsconfig + vite.config + tailwind.config + postcss
- [x] src/store/projectStore.ts — Zustand store
- [x] src/layouts/WorkspaceLayout.tsx — CSS Grid layout
- [x] src/App.tsx — Full app with workspace tabs, welcome, sidebar, inspector
- [x] src/index.css — Global styles + component classes
- [x] electron/main.js — Electron wrapper

## Phase 2: AI Adapter Layer + Image Processor [x]
- [x] backend/adapters/comfyui.py
- [x] backend/adapters/dalle.py
- [x] backend/processors/image.py
- [x] backend/routers/images.py
- [x] frontend/workspaces/ImageWorkspace.tsx
- [x] frontend/store/imageStore.ts

## Phase 3: Spritesheet & Animation [x]
- [x] backend/processors/spritesheet.py
- [x] backend/routers/animations.py
- [x] frontend/workspaces/AnimationWorkspace.tsx
- [x] frontend/store/animationStore.ts

## Phase 4: Audio Module [x]
- [x] backend/processors/audio.py
- [x] backend/routers/audio.py
- [x] frontend/workspaces/AudioWorkspace.tsx
- [x] frontend/store/audioStore.ts

## Phase 5: Godot Live Bridge [x]
- [x] backend/bridge/websocket_server.py
- [x] godot_bridge/OmniForgeBridge.gd
- [x] godot_bridge/OmniForge_Sandbox.tscn
- [x] frontend/store/bridgeStore.ts

## Phase 6: Quality, Style & Corrections [x]
- [x] backend/processors/quality.py
- [x] backend/routers/quality.py
- [x] frontend/workspaces/CheckerWorkspace.tsx
- [x] frontend/store/qualityStore.ts

## Phase 7: Advanced Animation & State Machines [x]
- [x] backend/processors/logic.py
- [x] backend/routers/logic.py
- [x] frontend/workspaces/MovesetWorkspace.tsx
- [x] frontend/workspaces/StatesWorkspace.tsx
- [x] frontend/store/logicStore.ts

## Phase 8: Library, Export & Finalization [x]
- [x] backend/routers/library.py
- [x] frontend/workspaces/LibraryWorkspace.tsx
- [x] frontend/store/libraryStore.ts
- [x] package.json build scripts
- [x] README.md (Italian) and technical docs
- [x] one-click installer (install.bat)
- [x] one-click launcher (start.bat)
- [x] Final project verification

## Pending: Verification
- [x] Install Python deps & verify backend starts
- [x] Install npm deps & verify frontend starts
- [x] Test CRUD API endpoints
