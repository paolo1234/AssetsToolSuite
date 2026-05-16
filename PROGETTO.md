# OmniForge: Game Assets Tool Suite — Prompt di Sistema v2.0

## RUOLO
Agisci da Lead Tools Engineer e Senior Full-Stack Developer specializzato in Game Dev Tooling. Costruisci **OmniForge**: una suite desktop locale per la creazione, gestione e test di asset per videogiochi, con integrazione nativa 1-click per **Godot Engine 4.x**.

---

## PRINCIPI ARCHITETTURALI FONDAMENTALI
*(Questi vincoli prevengono i problemi di incoerenza e overlap citati)*

### Principio 1 — Single Source of Truth (SSOT)
Tutti gli asset vivono in un **Project Manifest** (`omniforge.project.json`). Ogni modulo legge e scrive solo da lì. Nessun modulo tiene stato proprio. Questo elimina disallineamenti tra moduli.

### Principio 2 — Preview Always Matches Export
Ogni previewer interno usa **esattamente** gli stessi parametri del file esportato (stessa risoluzione, stesso FPS, stesso pivot point). Il rendering del canvas interno è pixel-perfect: nessun anti-aliasing non richiesto, nessuna interpolazione nascosta. Ciò che vedi = ciò che Godot riceve.

### Principio 3 — UI Layout System rigido
Il frontend usa un **layout a pannelli bloccati** (simile a Blender/DaVinci): nessun elemento flottante libero può sovrapporsi ad altri senza essere in un layer modale esplicito. Ogni workspace ha regioni CSS Grid fisse: `sidebar | canvas | inspector`. Mai `position: absolute` fuori dai modali.

### Principio 4 — Adapter Pattern per AI
Ogni motore AI (ComfyUI, DALL-E, Replicate) implementa la stessa interfaccia `AIAdapter`. Cambiare provider = cambiare un valore nel manifest. Zero riscritture.

---

## STACK TECNICO

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

## MODULI — SPECIFICHE COMPLETE

### MODULO 0 — Project Manager *(nuovo, mancava)*
- Crea/apri/chiudi progetti OmniForge (ogni progetto = cartella autonoma)
- Il manifest JSON tiene: risoluzione target del gioco, palette di riferimento, FPS base, path del progetto Godot collegato, lista asset con hash MD5
- **Funzionalità critica aggiunta:** Rilevamento automatico conflitti — se un asset esterno cambia su disco, OmniForge avvisa prima di sovrascrivere
- Tag system per gli asset (personaggio, environment, UI, SFX, musica)
- Cronologia versioni per asset (max 10 versioni, rollback 1-click)

---

### MODULO 1 — Image & Sprite Generation

**Generazione:**
- Adapter multipli: `ComfyUIAdapter`, `DallEAdapter`, `ReplicateAdapter`, `StableDiffusionLocalAdapter`
- Ogni richiesta passa per un `PromptBuilder` che aggiunge automaticamente i tag di stile del progetto (es. "pixel art, 16-bit, limited palette") — coerenza visiva garantita senza sforzo manuale
- Queue di generazione con priorità: non blocca l'UI durante l'attesa

**Inpainting Canvas:**
- Usa Konva.js con layer separati: `[background] [mask] [overlay]` — mai sovrapposti accidentalmente
- Tool: pennello maschera, eraser, forma rettangolo/ellisse
- Prima di inviare all'API, il backend compone automaticamente immagine + maschera nel formato corretto per ogni adapter

**Post-Processing (nuovo e più strutturato):**
- `rembg` per rimozione sfondo con anteprima real-time
- **Palette Quantizer:** importa una palette di riferimento (file `.pal`, `.gpl` o immagine) e applica dithering configurabile
- **Pixel Art Filter:** downscale controllato con nearest-neighbor + optional outline shader
- **Batch Processing:** applica la stessa pipeline a N immagini in una volta

---

### MODULO 2 — Spritesheet & Animation Editor

**Problemi prevenuti:**
- Il pivot point (origin) è sempre visualizzato e configurabile — corrisponde esattamente a `offset` in Godot `SpriteFrames`
- La risoluzione del frame è forzata a essere uniforme prima dell'export (avviso se i frame hanno dimensioni diverse)

**Funzionalità:**
- **Packer:** algoritmo `rectpack` per bin-packing ottimale, oppure griglia uniforme (scelta utente)
- **Slicer:** definisci griglia su uno spritesheet esistente, assegna nomi alle animation row, preview istantanea
- **Animation Player interno:** canvas Konva.js con controlli FPS (1-120), loop/ping-pong/once, onion skinning (mostra frame precedente/successivo in trasparenza)
- **Export formato Godot:** genera `.png` + `.tres` (SpriteFrames resource) già configurato con i nomi delle animazioni — nessuna configurazione manuale in Godot
- **Spritesheet Diff** *(nuovo)*: confronta visivamente due versioni dello stesso spritesheet per rilevare regressioni

---

### MODULO 3 — Audio Module

**Generazione:**
- Adapter: `AudioLDMAdapter`, `MusicGenAdapter`, `ElevenLabsAdapter`, `SunoAdapter`
- Parametri: durata, mood, BPM, strumenti, tipo (SFX/loop/jingle)

**Audio Tester (più robusto):**
- Waveform visualizer con cursor scrubbing
- **Loop point editor** *(critico per gamedev)*: definisci visivamente i punti di loop in/out — esporta già con i metadata corretti per Godot `AudioStreamOGGVorbis.loop_begin/end`
- Pitch shift (semitoni), reverb (room size, damping), low-pass filter — tutti non-distruttivi
- **Variazione casuale** *(nuovo)*: genera N varianti di un SFX (es. 5 versioni di "footstep") per evitare ripetizione in-game
- Export in `.ogg` (compresso, per Godot) e `.wav` (lossless, per editing)

---

### MODULO 4 — UI/UX & Level Design Mockup

**UI Mockup:**
- Canvas Konva.js con griglia snap e guide magnetiche
- Importa font `.ttf` personalizzati e previewa il testo con rendering identico a Godot (`theme_override_font`)
- **9-patch slicer** *(nuovo, fondamentale)*: definisci i margini di una NinePatchRect direttamente nel tool e pre-visualizza lo stretching — export con i valori esatti per Godot
- Esporta ogni elemento come PNG ritagliato + JSON con coordinate (compatibile con `AtlasTexture`)

**Tilemap Tester:**
- Griglia configurabile (dimensione tile, layer)
- **Preview parallax** *(migliorato)*: imposta velocità di scroll per layer e simulala con animazione nel canvas — ciò che vedi corrisponde al `ParallaxBackground` di Godot con gli stessi valori
- **Problema prevenuto:** il canvas usa la stessa risoluzione base del progetto (definita nel manifest), quindi il rapporto di scala è sempre 1:1 con Godot

---

### MODULO 5 — Godot Live Bridge *(ridisegnato)*

**Problema del design originale:** il bridge originale era fragile perché istanziava nodi "al volo" senza contesto. La nuova versione usa una **scena sandbox dedicata**.

**Architettura:**

```
OmniForge (Backend)
    │  WebSocket ws://localhost:47832
    ▼
OmniForgeBridge.gd (AutoLoad in Godot)
    │  legge comandi JSON
    ▼
OmniForge_Sandbox.tscn  ← scena separata, mai toccata dal dev
    │  istanzia preview nodes
    ▼
Ritorna alla scena di gioco originale al close
```

**Comandi WebSocket supportati:**
```json
{ "cmd": "preview_sprite", "path": "res://omniforge/hero_run.tres", "animation": "run" }
{ "cmd": "preview_audio", "path": "res://omniforge/theme.ogg" }
{ "cmd": "preview_tilemap", "tileset": "res://omniforge/forest.tres", "map_data": [...] }
{ "cmd": "preview_ui", "scene_path": "res://omniforge/hud_mockup.tscn" }
{ "cmd": "reload_asset", "path": "res://omniforge/hero.png" }
{ "cmd": "close_preview" }
```

**Garanzie di sicurezza del Bridge:**
- Opera SOLO nella sandbox scene — non modifica mai la scena corrente del progetto
- Tutti i file OmniForge vanno in `res://omniforge/` (cartella dedicata, ignorata da git tramite `.gitignore` auto-generato)
- Se il backend è offline, il bridge fallisce silenziosamente (nessun crash)
- Toggle ON/OFF nell'Editor Godot con una singola variabile `@export var enabled: bool`

---

### MODULO 6 — Asset Consistency Checker *(nuovo, critico)*

Questo modulo risolve il problema "le cose differiscono dal gioco":

- **Palette Audit:** scansiona tutti gli sprite del progetto e rileva frame che escono dalla palette di riferimento
- **Resolution Audit:** verifica che tutti i tile abbiano dimensioni multiple della tile-size del progetto
- **Naming Convention Check:** verifica che tutti i file rispettino il naming scheme configurato (es. `[category]_[name]_[variant].png`)
- **Godot Compatibility Check:** verifica che le animazioni abbiano FPS compatibili con quelli del progetto Godot, che i file audio siano in formato `.ogg`, che le texture non superino i limiti GPU configurati
- Report esportabile in HTML/PDF

---

### MODULO 7 — Template & Preset System *(nuovo)*

- Preset di stile salvabili: "Pixel Art 16x16 RPG", "Vector 2D Platformer", "UI Dark Theme" — ogni preset configura l'intera pipeline
- Template di progetto starter scaricabili (struttura cartelle Godot + manifest pre-compilato)
- Condivisione preset via file `.omnipreset` (JSON zippato)

---

## STRUTTURA CARTELLE

```
omniforge/
├── backend/
│   ├── main.py                  # FastAPI app + WebSocket server
│   ├── config.py                # Settings globali (porte, path, API keys)
│   ├── project/
│   │   ├── manifest.py          # Lettura/scrittura omniforge.project.json
│   │   └── versioning.py        # Cronologia asset
│   ├── adapters/
│   │   ├── base.py              # AIAdapter interface (ABC)
│   │   ├── comfyui.py
│   │   ├── dalle.py
│   │   ├── replicate.py
│   │   └── audio/
│   │       ├── audioldm.py
│   │       └── elevenlabs.py
│   ├── processors/
│   │   ├── image.py             # rembg, palette, pixel-art filter
│   │   ├── spritesheet.py       # packing, slicing, export .tres
│   │   ├── audio.py             # pydub, loop points, varianti
│   │   └── checker.py           # Asset Consistency Checker
│   ├── bridge/
│   │   └── websocket_server.py  # Gestione comandi Godot Bridge
│   └── routers/
│       ├── images.py
│       ├── animation.py
│       ├── audio.py
│       ├── ui_mockup.py
│       └── project.py
├── frontend/
│   ├── src/
│   │   ├── store/               # Zustand stores (un file per modulo)
│   │   ├── layouts/
│   │   │   └── WorkspaceLayout.tsx   # CSS Grid rigido, nessun overlap
│   │   ├── workspaces/
│   │   │   ├── ImageWorkspace.tsx
│   │   │   ├── AnimationWorkspace.tsx
│   │   │   ├── AudioWorkspace.tsx
│   │   │   ├── UIWorkspace.tsx
│   │   │   └── CheckerWorkspace.tsx
│   │   └── components/          # Componenti atomici riusabili
│   └── electron/
│       └── main.js              # Entry Electron
└── godot_bridge/
    ├── OmniForgeBridge.gd       # AutoLoad script
    ├── OmniForge_Sandbox.tscn   # Scena preview isolata
    └── README.md                # Istruzioni installazione 1-click
```

---

## METODOLOGIA DI SVILUPPO (FASI)

**Fase 1 — Core & Project Manager**
Setup FastAPI, WebSocket server, sistema manifest, struttura cartelle frontend Electron+React, CSS Grid layout system. Nessun overlap possibile da qui in poi.

**Fase 2 — AI Adapter Layer + Image Processor**
Implementa `AIAdapter` ABC, i primi due adapter (ComfyUI + DALL-E), pipeline image processor con rembg e palette.

**Fase 3 — Spritesheet Engine**
Slicer, packer, animation player su Konva.js, export `.tres` per Godot. Include test automatici sulla coerenza frame/pivot.

**Fase 4 — Audio Module**
Adapter audio, waveform player, loop point editor, export `.ogg`.

**Fase 5 — Godot Live Bridge**
WebSocket server lato backend, `OmniForgeBridge.gd` con sandbox scene, comandi JSON completi.

**Fase 6 — Consistency Checker & Polish**
Asset audit, report, preset system, template starter.

---

## REGOLE FONDAMENTALI PER IL CODICE

1. **Nessun stato locale nei moduli** — tutto passa per il manifest o lo store Zustand
2. **Preview = Export** — ogni renderer usa identici parametri, zero discrepanze
3. **Layout CSS Grid immutabile** — `position: absolute` solo dentro `[role="dialog"]`
4. **Fail silenzioso verso Godot** — il bridge non crasha mai il gioco in caso di errore
5. **Ogni funzione ha un tipo di ritorno esplicito** — Python type hints + TypeScript strict mode
6. **Test di integrazione obbligatori** per ogni adapter AI (mock responses inclusi)

---

**Inizia dalla Fase 1:** scrivi `main.py` (FastAPI + WebSocket), `config.py`, `manifest.py` e il layout base React con CSS Grid. Commenta ogni sezione non-ovvia.

---

Le aggiunte chiave rispetto al tuo originale sono il **Modulo 0** (Project Manager con SSOT, che previene tutti i disallineamenti), il **Modulo 6** (Consistency Checker, che rileva le differenze prima che arrivino in Godot), il **9-patch slicer**, il **loop point editor** per l'audio, la **sandbox scene isolata** per il bridge (che protegge il tuo progetto da modifiche accidentali) e il **Principio 3** che rende strutturalmente impossibile l'overlap dell'UI.

# OmniForge — Estensione v2.1: Asset Correction & Coherence Layer

## MODULO 8 — Smart Positioning & Alignment System

Questo modulo risolve il problema fondamentale: un asset generato raramente è "pronto" — ha il pivot sbagliato, è fuori scala, o è posizionato male rispetto agli altri asset della scena.

### 8.1 Visual Mass Centering
Il centro geometrico di un bounding box non è il centro visivo. Un personaggio con una spada lunga a destra ha il bounding box spostato, ma il "peso visivo" è sul torso.

- Algoritmo di calcolo del **centro di massa visiva**: analizza la distribuzione dei pixel opachi per trovare il centroide reale dell'asset
- Propone automaticamente il pivot point corretto (es. "piedi" per personaggi, "centro" per oggetti, "angolo in basso a sinistra" per tile)
- Override manuale con drag del pivot nel canvas
- Il pivot calcolato viene scritto direttamente nei metadati del `.tres` di Godot (`offset` in `SpriteFrames`)

### 8.2 Multi-Asset Alignment Panel
Quando hai più sprite sullo schermo contemporaneamente:

- **Allineamento relativo:** seleziona N sprite e allineali per baseline (piedi), centerline (busto), o topline (testa)
- **Distribuzione uniforme:** distribuisci N asset con spaziatura equa orizzontale o verticale
- **Reference locking:** marca un asset come "ancora" — tutti gli altri si allineano a lui, non il contrario
- **Scale comparator:** mostra tutti gli asset selezionati sovrapposti su una griglia con unità di misura (es. "il boss è 3x il personaggio principale") — permette di correggere le proporzioni relative prima dell'export

### 8.3 Snap & Grid System con Sub-Pixel Correction
- Griglia configurabile per progetto (es. 16x16 per pixel art, 32x32 per tile standard)
- **Sub-pixel correction:** se un asset è sfalsato di meno di 2px rispetto alla griglia, viene corretto automaticamente — con avviso visivo
- **Pixel-perfect mode:** blocca qualsiasi trasformazione a valori interi — nessuna coordinata `.5` che causa blurring in Godot

---

## MODULO 9 — Generation Error Recovery System

La generazione AI fallisce in modi prevedibili. Questo modulo li anticipa tutti.

### 9.1 Generation Monitor con Diagnostica Automatica
Ogni richiesta di generazione passa per un **Quality Gate** prima di essere mostrata all'utente:

```python
class QualityGate:
    checks = [
        ResolutionCheck(),       # Dimensioni corrispondono al target?
        TransparencyCheck(),     # Background rimosso correttamente?
        ArtifactDetector(),      # Pixel isolati, bordi allucinati?
        StyleConsistencyScore(), # Distanza stilistica dalla palette di riferimento
        SaturationCheck(),       # Colori troppo saturi/desaturati vs riferimento?
        SymmetryCheck(),         # Per sprite che dovrebbero essere simmetrici
    ]
    
    def evaluate(self, image) -> QualityReport:
        # Restituisce score 0-100 + lista problemi rilevati
```

Se lo score scende sotto soglia configurabile (default 70/100), OmniForge mostra automaticamente:
- Il problema specifico rilevato ("bordo fantasma sul lato sinistro", "background non rimosso al 100%", "stile non coerente: saturazione troppo alta")
- Le **azioni rapide** per correggerlo (vedi sezioni successive)
- Un pulsante "Rigenera con fix automatico" che riscrive il prompt correttivo e riprova

### 9.2 Generation History & Seed Tracker
- Ogni generazione salva: prompt completo, seed (se disponibile), adapter usato, parametri, timestamp, score qualità
- **Riproduzione garantita:** puoi riottenere esattamente lo stesso risultato (con stesso adapter/seed)
- **A/B Comparison viewer:** affianca fino a 4 varianti della stessa generazione con differenze evidenziate
- **Differential prompt:** mostra esattamente cosa è cambiato tra due prompt che hanno prodotto risultati diversi — utile per capire quale modifica ha migliorato l'output
- Pin dei risultati migliori per non perderli durante l'esplorazione

### 9.3 Partial Regeneration (Keep Good Parts)
Il problema più frustrante: il 90% dell'immagine è perfetto ma c'è un dettaglio sbagliato (una mano storta, un'ombra allucinata, un colore fuori palette).

- Strumento di **selezione parziale** sul canvas: disegna una maschera sulla zona da correggere
- Il backend compone automaticamente: immagine originale + maschera + prompt correttivo → inpainting localizzato
- **Blend automatico:** il risultato viene fuso con l'originale con feathering configurabile per evitare cuciture visibili
- Storico delle correzioni parziali: puoi annullare singole correzioni senza perdere le altre

---

## MODULO 10 — Style Enforcement Engine

Il problema della coerenza visiva tra asset generati in sessioni diverse o con prompt diversi.

### 10.1 Style Reference System
- Ogni progetto ha uno **Style Bible**: collezione di 3-10 immagini "master" che definiscono l'estetica del gioco
- OmniForge calcola e memorizza le caratteristiche stilistiche di ogni immagine master:
  - Palette dominante (k-means clustering dei colori)
  - Range di saturazione e luminosità
  - Frequenza spaziale media (misura quanto il disegno è "dettagliato")
  - Direzionalità della luce (analisi degli highlight/shadow)
- Ogni nuovo asset generato viene automaticamente confrontato con la Style Bible e riceve un **Style Match Score**

### 10.2 Lighting Direction Lock
Uno dei problemi più sottili: asset generati separatamente hanno luce da direzioni diverse, risultando incoerenti nella stessa scena.

- Definisci nel progetto la **direzione globale della luce** (angolo in gradi, es. "luce da sinistra a 30°")
- Il sistema aggiunge automaticamente al prompt di generazione i modificatori corretti ("directional light from upper left, strong shadows on right side")
- **Lighting Audit:** per gli asset già presenti nel progetto, analisi automatica della direzione della luce percepita e flag degli asset incoerenti
- Per gli asset fuori palette: suggerimento di re-generazione vs correzione manuale con il Color Harmonizer

### 10.3 Palette Enforcer (più potente del v2.0)
- **Modalità Soft:** rimappa i colori dell'immagine generata verso i colori più vicini nella palette di riferimento (dithering opzionale)
- **Modalità Hard:** rifiuta i pixel che escono dalla palette e li sostituisce con il colore più vicino — zero eccezioni
- **Modalità Adaptive:** apprende dai tuoi "approva" e "rifiuta" su singoli asset quale varianza stilistica è accettabile
- Preview in split-screen: originale a sinistra, palette-enforced a destra, con indicatore dei pixel modificati sovrapposto

### 10.4 Cross-Asset Style Transfer
- Seleziona un asset già approvato come "stile sorgente"
- Seleziona uno o più asset "destinazione"
- OmniForge trasferisce lo stile (texture, livello di dettaglio, range tonale) mantenendo il contenuto dell'asset destinazione
- Basato su un adapter configurabile: local (Stable Diffusion img2img) o API esterna

---

## MODULO 11 — Dimension & Scale Manager

### 11.1 Character Scale Chart
- Canvas dedicato con una **scala visiva di riferimento**: una barra verticale con unità di gioco configurabili
- Trascina qualsiasi sprite nel canvas e vedi immediatamente la sua altezza in "unità di gioco"
- **Scale constraints:** definisci regole (es. "i nemici volanti devono essere tra 0.5x e 0.8x il personaggio principale") — OmniForge avvisa se un nuovo asset viola i vincoli
- **Silhouette comparator:** sovrappone i profili di tutti i personaggi principali con opacità ridotta per verificare la leggibilità delle sagome a colpo d'occhio

### 11.2 Smart Resize Pipeline
Il resize naif distrugge la pixel art e introduce artefatti. Pipeline corretta per tipo di asset:

```
Pixel Art    → Nearest-neighbor resize → Palette re-enforce
             → Verifica che i bordi siano ancora a pixel singolo
             
Painted/HD   → Real-ESRGAN upscale (2x/4x) → Sharpen localizzato
             → Downscale con Lanczos se necessario
             
Spritesheet  → Resize frame-by-frame → Riallineamento pivot post-resize
             → Verifica uniformità dimensioni frame
```

- Ogni pipeline è configurabile e il risultato è sempre comparato con l'originale prima di sovrascrivere
- **Batch resize:** applica la stessa pipeline a tutti gli asset di una categoria con un click

### 11.3 Canvas Normalization
Il problema comune: frame di un'animazione con dimensioni leggermente diverse (es. un frame è 64x65, un altro 64x63).

- **Auto-normalize:** porta tutti i frame alla dimensione massima presente, aggiungendo padding trasparente — il pivot viene ricalcolato automaticamente
- **Trim con padding:** rimuove il trasparente inutile e aggiunge un padding configurabile (es. 2px su tutti i lati) per evitare clipping ai bordi in Godot
- **Anchor-aware padding:** il padding non è uniforme se hai definito un pivot — viene aggiunto asimmetricamente per preservare il pivot point nella posizione corretta

---

## MODULO 12 — Edge & Artifact Cleaner

Il problema più comune dopo `rembg`: bordi sporchi, aloni, fringe colorati, pixel isolati.

### 12.1 Edge Refinement Suite
- **Fringe Remover:** rileva e rimuove l'alone di colore che `rembg` lascia spesso attorno ai capelli e ai bordi sottili (operazione: desaturazione dell'alone + alpha multiplication)
- **Edge Smoothing:** smoothing selettivo dei bordi dell'alpha channel — configurabile tra "sharp pixel" (per pixel art) e "anti-aliased" (per asset HD)
- **Isolated Pixel Detector:** trova pixel completamente isolati con alpha > 0 a distanza > N pixel dal corpo principale dell'asset — li mostra evidenziati e offre rimozione batch
- **Alpha Threshold:** slider per definire la soglia sotto cui l'alpha viene azzerato — risolve il problema del "semi-trasparente che in Godot appare come grigio"

### 12.2 Background Leakage Detector
`rembg` a volte lascia frammenti di background nell'immagine. Il detector:
- Campiona il colore del background originale (cliccando sull'immagine prima della rimozione)
- Dopo la rimozione, cerca cluster di pixel con colore simile al background che sono rimasti → li evidenzia in rosso
- Rimozione automatica con tolleranza configurabile

### 12.3 Seam Fixer per Inpainting
Quando si usa il partial regeneration (Modulo 9.3), la giuntura tra la parte originale e quella rigenerata può essere visibile.

- Rilevamento automatico della seam dopo ogni inpainting
- **Blur selettivo sulla seam:** applica Gaussian blur solo nei 3-5 pixel attorno alla maschera, preservando il dettaglio interno
- **Color match alla seam:** campiona i colori ai bordi della maschera e fa un blending graduale di 2px per nascondere la transizione

---

## MODULO 13 — Animation Coherence Tools

### 13.1 Frame Stabilizer
Il problema comune nelle animazioni AI-generate: i frame "vibrano" perché ogni frame è leggermente sfalsato rispetto al precedente.

- **Motion anchor:** definisci un punto di riferimento su un frame (es. "il punto centrale del busto") — OmniForge allinea automaticamente tutti gli altri frame a quel punto
- **Optical flow stabilization:** algoritmo di optical flow (OpenCV) che analizza il movimento tra frame consecutivi e corregge i micro-sfasamenti involontari
- **Before/after player:** riproduci l'animazione prima e dopo la stabilizzazione in loop per confrontare

### 13.2 Onion Skin Avanzato
- Mostra fino a 3 frame precedenti e 3 successivi con opacità decrescente
- **Ghost mode:** mostra solo il profilo esterno dei frame fantasma (contorno), non il fill — meno confusione visiva
- **Difference mode:** mostra solo i pixel che cambiano da un frame all'altro (come un diff visivo) — identifica immediatamente cosa si muove e cosa rimane statico

### 13.3 Hitbox/Hurtbox Editor
- Overlay sul frame con strumento per disegnare rettangoli di hitbox/hurtbox
- Le box si propagano a tutti i frame (con possibilità di overriding per frame)
- Export come JSON separato compatibile con i formati comuni di Godot per collision shape data
- Visualizzazione: hitbox in rosso semitrasparente, hurtbox in blu semitrasparente

### 13.4 Foot Planting Lock
Il "character sliding" è uno dei bug visivi più fastidiosi nelle animazioni di camminata.

- Definisci il "ground contact frame" (es. frame 2 e frame 5 di una camminata)
- OmniForge blocca la posizione verticale dei piedi in quei frame e interpola dolcemente la correzione verticale negli altri frame
- Funziona per correzione post-generazione su spritesheet esistenti

---

## MODULO 14 — Real-Time Context Preview

Il problema di fondo: un asset approvato in isolamento può risultare sbagliato nella scena reale del gioco.

### 14.1 Scene Context Compositor
- Carica uno screenshot della tua scena di Godot come background di riferimento
- Posiziona gli asset da approvare sopra lo screenshot in scala reale
- Vedrai immediatamente se il personaggio è troppo grande rispetto ai tile, se lo stile clasha, se l'illuminazione è incoerente
- **Problema prevenuto:** nessuna sorpresa una volta importato in Godot — il contesto è visibile prima

### 14.2 Shader Preview
Gli asset in Godot vengono spesso modificati da shader (outline, rim lighting, color correction, dithering). Vedendo l'asset senza shader in OmniForge si introduce una discrepanza.

- Importa il codice GLSL/shader di Godot nel progetto OmniForge
- Il frontend applica una **approssimazione WebGL** dello shader sull'asset nel previewer
- Supporta le operazioni più comuni: outline, color modulation, dissolve, scanline, CRT filter
- Il risultato è un'anteprima "as it will look in Godot" — non identica pixel-perfect, ma visivamente equivalente

### 14.3 Resolution & Viewport Simulator
- Simula come l'asset appare a diverse risoluzioni di gioco (1080p, 720p, 480p, retro 320x240)
- Simula lo zoom della telecamera di Godot (`zoom` del `Camera2D`)
- **Leggibilità check:** a quale zoom minimo l'asset rimane leggibile? — test automatico con feedback "✓ leggibile a 0.5x zoom"

---

## REGOLE AGGIUNTIVE AL CODICE (per questi moduli)

6. **Quality Gate non bloccante:** il gate avvisa ma non impedisce mai all'utente di procedere — è advisory, non mandatory
7. **Operazioni distruttive richiedono conferma** + backup automatico nella cronologia versioni (Modulo 0)
8. **Preview always live:** qualsiasi modifica nei moduli di correzione si vede in tempo reale sul canvas, senza dover cliccare "applica"
9. **Undo/Redo globale a 50 step** per ogni workspace — nessuna operazione è permanente senza salvataggio esplicito
10. **Ogni correzione è non-distruttiva** fino all'export: i parametri vengono salvati nel manifest, l'immagine sorgente è sempre preservata

---

Queste estensioni coprono tutti i punti critici: la **generazione fallisce** → Modulo 9 la recupera; l'**asset è fuori stile** → Modulo 10 lo corregge; le **dimensioni sono sbagliate** → Modulo 11 le normalizza; i **bordi sono sporchi** → Modulo 12 li pulisce; l'**animazione trema** → Modulo 13 la stabilizza; l'**asset è sbagliato in contesto** → Modulo 14 lo rivela prima di arrivare in Godot.

Ottimo, ho analizzato tutto AutoSprite in profondità. Le loro idee chiave (single sprite → full moveset, character DNA locking, pose-first workflow, batch multi-character, gamepad preview) sono tutte replicabili in locale gratuitamente. Ecco l'estensione:

---

# OmniForge — Estensione v2.2: Animation Intelligence Layer
*(ispirato ad AutoSprite, reingegnerizzato per essere completamente locale e gratuito)*

---

## MODULO 15 — Character DNA System
*(la feature più importante di AutoSprite, implementata localmente)*

AutoSprite mantiene la coerenza del personaggio tra animazioni estraendo implicitamente le sue caratteristiche. OmniForge lo fa esplicitamente e in modo controllabile.

### 15.1 DNA Extraction Pipeline

Quando carichi o generi uno sprite "master" (es. il personaggio fermo di fronte), OmniForge esegue automaticamente:

```python
class CharacterDNA:
    """
    Fingerprint visivo completo di un personaggio.
    Calcolato una volta, usato per TUTTE le generazioni successive.
    """
    # Analisi colore
    palette: list[Color]           # K colori dominanti (k-means, k=16)
    skin_tone_range: ColorRange    # Range HSV della carnagione rilevata
    clothing_colors: list[Color]   # Colori degli indumenti separati dalla pelle
    outline_color: Color           # Colore del bordo/contorno principale
    
    # Analisi proporzioni
    head_to_body_ratio: float      # Es. 0.28 (testa = 28% altezza totale)
    limb_proportions: dict         # Braccia/gambe relative al torso
    bounding_box: Size             # Dimensione del canvas di riferimento
    visual_center: Point           # Centro di massa visiva (non geometrico)
    
    # Analisi stile
    line_weight: float             # Spessore medio del tratto
    detail_frequency: float        # Quanto è "dettagliato" (FFT spatial freq)
    shading_style: str             # "flat" | "cel" | "gradient" | "painted"
    light_angle: float             # Angolo luce percepita in gradi
    
    # Analisi strutturale (per consistency check)
    silhouette_hash: str           # Hash della silhouette per confronto rapido
    color_histogram: np.ndarray    # Distribuzione colori per similarity score
```

### 15.2 DNA Lock → Generazione Consistente

Una volta estratto il DNA, ogni nuova generazione (walk, run, attack...) riceve automaticamente un **DNA Injection Prompt**:

```python
def build_dna_prompt(dna: CharacterDNA, animation: str) -> str:
    return f"""
    SAME CHARACTER as reference. Strict consistency required:
    - Color palette: {dna.palette_description}  
    - Proportions: head {dna.head_to_body_ratio:.0%} of body height
    - Art style: {dna.shading_style} shading, line weight {dna.line_weight:.1f}px
    - Light source: {dna.light_angle}° from reference image
    - Outline color: {dna.outline_color.hex}
    Animation: {animation}. Transparent background. Same canvas size {dna.bounding_box}.
    """
```

**DNA Drift Detector:** dopo ogni frame generato, confronta il DNA estratto dal frame con il DNA master. Se la distanza supera una soglia, il frame viene flaggato con il motivo specifico ("colore capelli cambiato", "proporzioni gambe diverse") prima di essere mostrato.

### 15.3 DNA Editor
- Visualizza il DNA estratto in un pannello human-readable
- Override manuale di qualsiasi parametro (es. "forza skin tone a questo esatto range HSV")
- **DNA Snapshot:** salva il DNA di un personaggio come file `.omni-dna` — riapplicabile in un altro progetto o condivisibile col team
- **DNA Merge:** hai due stili? Fai il merge pesato dei loro DNA (es. 70% stile A, 30% stile B) per creare un ibrido controllato

---

## MODULO 16 — Moveset Builder (Single Sprite → Full Character)

L'idea centrale di AutoSprite, eseguita localmente con pipeline ComfyUI.

### 16.1 Moveset Definition System

```json
{
  "moveset": {
    "idle": {
      "frames": 4,
      "fps": 8,
      "loop": "ping-pong",
      "loop_in": 0,
      "loop_out": 3,
      "directions": ["right"],
      "description": "Breathing idle, slight bob"
    },
    "walk": {
      "frames": 8,
      "fps": 12,
      "loop": "loop",
      "loop_in": 0,
      "loop_out": 7,
      "directions": ["right", "left", "up", "down"],
      "description": "Walk cycle, foot plant on frames 0 and 4"
    },
    "run": { "frames": 6, "fps": 16, "loop": "loop", ... },
    "jump": {
      "frames": 5,
      "fps": 10,
      "loop": "once",
      "loop_in": 2,
      "loop_out": 2,
      "description": "Anticipation → peak → fall. Hold frame 2 at apex."
    },
    "attack_slash": { ... },
    "hurt": { ... },
    "death": { "loop": "once", ... }
  }
}
```

**Preset Moveset Library:** template predefiniti per generi comuni:
- `platformer_basic`: idle, walk, run, jump, fall, attack, hurt, death
- `rpg_topdown`: idle ×4 dir, walk ×4 dir, run ×4 dir, attack ×4 dir
- `fighting_game`: idle, walk_fwd, walk_bck, jump, crouch, 6 attack types, block, hurt, ko
- `shmup_ship`: idle, tilt_left, tilt_right, thrust, explode
- Custom: costruisci il tuo da zero

### 16.2 Direction Generator (Mirror + AI)

Generare manualmente tutte le direzioni è il lavoro più noioso del gamedev. Due approcci:

**Mirror automatico (gratuito, istantaneo):**
- Flippa orizzontalmente per ottenere la direzione opposta
- `flip_direction_fix`: correzione post-flip degli elementi asimmetrici (fodero della spada, emblema sul petto) tramite inpainting localizzato su quelle zone

**AI multi-direction (locale, ComfyUI):**
- Dato il frame frontale/laterale, genera le direzioni mancanti mantenendo il DNA lock
- Pipeline: frame sorgente + maschera direzione + DNA prompt → img2img controllato
- Configurabile: genera solo le direzioni mancanti, non rigenera quelle già approvate

### 16.3 Pose-First Animation Workflow
*(ispirato alla Poses API di AutoSprite)*

Il metodo più controllabile per animazioni complesse:

1. **Define key poses:** definisci le pose chiave dell'animazione (es. per una camminata: contatto_sinistro, passing, contatto_destro, passing_2)
2. **Generate each pose:** OmniForge genera ogni posa chiave come immagine statica indipendente, con DNA lock
3. **Inbetweening:** per i frame intermedi, scegli tra:
   - **AI inbetween:** il modello genera i frame di transizione dati due pose chiave come reference
   - **Manual inbetween:** canvas di disegno semplificato per completare i frame a mano
   - **Morph inbetween:** cross-dissolve + warp ottico tra due pose (buono per effetti, non per personaggi)
4. **Assembly:** tutte le pose + inbetween vengono assemblate nello spritesheet finale

### 16.4 Batch Moveset Generation (Advanced Mode)
*(AutoSprite Advanced Mode, ma locale)*

- Definisci una lista di N personaggi (ognuno con il suo DNA)
- Definisci il moveset comune
- OmniForge genera tutti i moveset in una coda batch asincrona
- Progress tracker con ETA per frame
- Risultati disponibili man mano che completano — non aspetti il batch intero
- Pausa/ripresa della coda in qualsiasi momento

---

## MODULO 17 — Animation State Machine Preview
*(il "gamepad preview" di AutoSprite, ma interattivo e integrato con Godot)*

### 17.1 State Machine Editor visuale

Canvas dove costruisci la logica di transizione tra animazioni del tuo personaggio:

```
[idle] ──(move input)──→ [walk] ──(sprint)──→ [run]
  ↑                        │                    │
  └──────(no input)────────┘◄────(no sprint)────┘
  
[walk] ──(jump)──→ [jump_rise] ──(apex)──→ [jump_fall] ──(land)──→ [idle]
         │                                                  │
         └──────────────────────────────────────────────────┘
```

- Nodi = animazioni del personaggio
- Frecce = transizioni con condizione testuale (es. "velocity.x > 0")
- Ogni transizione ha: blend time configurabile, frame di uscita (exit on frame N o exit on end)
- **Export come Godot AnimationTree:** esporta la state machine direttamente come risorsa `.tres` compatibile con `AnimationTree` + `AnimationNodeStateMachine` — zero configurazione in Godot

### 17.2 Gamepad/Keyboard Live Preview

Player integrato nel frontend che simula il comportamento del personaggio nel gioco:

- Tasti `WASD` o gamepad → triggera le transizioni della state machine
- Il personaggio si muove su uno sfondo configurabile (puoi caricare uno screenshot del tuo livello)
- Velocità di movimento configurabile per corrispondere alle unità di Godot
- **Collision preview:** disegna la hitbox del personaggio e vedi se clippa con le piattaforme dello screenshot
- **Problema prevenuto:** vedi esattamente come l'animazione "si sente" in movimento PRIMA di andare in Godot

### 17.3 Transition Smoothness Analyzer

Il problema comune: le animazioni sembrano ok singolarmente ma "saltano" nelle transizioni.

- Analizza automaticamente le coppie (last frame di A, first frame di B) per ogni transizione della state machine
- Calcola uno "smoothness score" basato sulla differenza visiva tra i frame di transizione
- Score basso → suggerisce: aumenta il blend time, o rigenera il primo/ultimo frame per avvicinarlo alla posa di transizione
- Visualizza la transizione in slow motion (2fps) per identificare il "jump" visivamente

---

## MODULO 18 — Asset Library & Non-Character Sprites
*(la Asset Library di AutoSprite, espansa)*

AutoSprite gestisce solo personaggi. OmniForge gestisce tutto il resto con la stessa logica.

### 18.1 Categorie Asset Library

```
asset_library/
├── characters/          # Personaggi giocabili e NPC
├── enemies/             # Con moveset dedicati
├── items/               # Oggetti raccoglibili, powerup
│   └── [animati]       # Coin spin, gem sparkle, potion bubble
├── projectiles/         # Bullets, arrows, fireballs
├── effects/             # VFX: explosioni, smoke, magie
├── environment/
│   ├── tiles/           # Tileset con varianti
│   ├── props/           # Oggetti di scena (barili, casse, torce)
│   └── backgrounds/     # Layer parallax
├── ui/                  # Buttons, panels, icons, cursors
└── audio/               # SFX e musica organizzati per scena
```

### 18.2 Effect Animation Generator

Gli effetti VFX hanno regole di animazione diverse dai personaggi. Pipeline dedicata:

- **Particle-style effects** (spark, smoke, blood): genera N frame di dispersione con alpha decrescente — export come spritesheet già configurato per `GPUParticles2D` in Godot
- **Impact effects** (slash, punch, explosion): genera la sequenza esplosione → dissolvenza con timing configurabile
- **Loop effects** (fire, water, magic aura): genera loop seamless automatico — il frame finale blenda col primo
- **Parametric VFX** *(nuovo)*: definisci l'effetto con parametri (colore primario, scala, durata ms) → genera varianti dello stesso effetto con quei parametri (es. "fuoco verde da magia", "esplosione piccola per nemico debole")

### 18.3 Item & Prop Animator

- **Idle animations** per oggetti statici che devono "vivere": una torcia che brucia, una moneta che ruota, un cristallo che pulsa
- **Collected/destroyed animations:** genera automaticamente la sequenza di raccolta (pickup flash) e distruzione (break apart) per ogni item
- **Consistent item style:** tutti gli item di un progetto condividono il DNA stilistico (stesso spessore outline, stessa direzione luce, stessa palette limitata)

### 18.4 Re-Export with New Art
*(feature chiave di AutoSprite)*

Il problema: aggiorni lo sprite base del personaggio (cambio costume, fix proporzioni) e devi rigenerare tutte le N animazioni.

- OmniForge traccia per ogni animazione quale "sprite master" ha usato come riferimento
- Quando aggiorni il master, mostra quali animazioni sono "stale" (basate sul vecchio master)
- **Re-generate stale:** rigenera le animazioni stale mantenendo esattamente lo stesso moveset e timing — solo il look cambia
- **Diff view:** confronto side-by-side vecchia/nuova versione di ogni animazione per approvazione prima dell'overwrite
- **Partial re-export:** puoi scegliere di rigenerare solo alcune animazioni, non tutte

---

## MODULO 19 — Naming Convention & Export Pipeline

AutoSprite garantisce nomi coerenti tra export. OmniForge lo standardizza e lo rende configurabile.

### 19.1 Naming Convention System

Template configurabile per ogni progetto:

```
# Template: {category}_{character}_{animation}_{direction}_{frame}
hero_idle_right_000.png
hero_idle_right_001.png
hero_walk_right_000.png
hero_walk_left_000.png

# Oppure stile Godot-native:
hero/idle/right/frame_000.png

# Oppure stile GameMaker:
spr_hero_idle_0.png
```

- Rinomina batch di tutti gli asset esistenti al cambio convention — senza rompere i riferimenti nel manifest
- Validazione: OmniForge avvisa se un file non rispetta la convention prima dell'export
- Convention per tipo di asset: i personaggi usano una convention, i tile un'altra, i VFX un'altra

### 19.2 Multi-Engine Export Pack

Un click esporta lo stesso asset in formato nativo per tutti gli engine supportati:

| Engine | Spritesheet | Metadata | Note |
|---|---|---|---|
| Godot 4 | `.png` | `.tres` (SpriteFrames) | pivot, loop_in/out, fps per animation |
| Unity | `.png` | `.meta` + Sprite Atlas JSON | slice rects, pivot, Animator clips |
| GameMaker | `.png` | `.yy` (Sprite asset) | frame order, playback speed |
| Phaser 3 | `.png` | Atlas JSON (array format) | frame keys, durations |
| RPG Maker MZ | `.png` | Character sheet format | 3×4 grid rispettato |
| Generic | `.png` | JSON standard (FrameData) | per engine custom |

**Problema prevenuto:** non devi conoscere il formato interno di ogni engine — OmniForge genera i file corretti automaticamente.

### 19.3 Versioned Export History

- Ogni export viene archiviato con timestamp, versione del manifest, hash di tutti gli asset
- **Roll-forward/rollback:** ripristina esattamente un export precedente in un click
- **Export diff:** confronta due export per vedere cosa è cambiato (utile per QA)
- **Export notes:** aggiungi note a ogni export ("build per playtest v0.3", "fix animazione morte")

---

## MODULO 20 — Cutscene & Storyboard Tool
*(AutoSprite ha un AI Cutscene Generator — OmniForge lo fa localmente)*

### 20.1 Storyboard Builder

- Canvas diviso in pannelli (3, 4, 6 pannelli configurabili)
- In ogni pannello: posiziona sprite già nel progetto + sfondi + testo dialog
- Indica la direzione di movimento con frecce disegnabili
- Esporta lo storyboard come PNG/PDF per condivisione

### 20.2 Cutscene Sequence Generator

- Definisci la sequenza narrativa: "Personaggio A entra da sinistra → si avvicina a B → dialogo → B attacca → A schiva"
- OmniForge genera le **pose chiave** necessarie per ogni beat narrativo usando il Character DNA
- Le pose vengono assemblate in una sequenza temporizzata
- Export come: sequenza PNG numerata, o direttamente come `AnimationPlayer` track data per Godot

### 20.3 Dialog Portrait Generator

- Genera varianti del ritratto del personaggio per il sistema di dialoghi: neutro, felice, arrabbiato, triste, sorpreso
- Mantiene il DNA lock — tutte le espressioni sono inequivocabilmente lo stesso personaggio
- Formato export: singolo spritesheet con tutte le espressioni, o file separati
- Compatibile con i più comuni dialog system di Godot (Dialogic, etc.)

---

## AGGIORNAMENTI AI MODULI PRECEDENTI

### Aggiornamento Modulo 2 (Spritesheet) — da AutoSprite

- **FPS per singola animazione:** non più un FPS globale per lo spritesheet — ogni animation row ha il suo FPS indipendente, esattamente come AutoSprite
- **Loop in/out per animazione:** i punti di loop sono definiti per animazione, non globalmente, ed esportati come metadati nel `.tres` di Godot (`SpriteFrames.set_animation_loop`)
- **Frame hold:** definisci frame specifici da "tenere" più a lungo (es. frame di impatto di un attacco) senza aumentare l'FPS globale — export con durata per-frame nel JSON

### Aggiornamento Modulo 5 (Godot Bridge) — da AutoSprite

Aggiunta compatibilità con le risorse prodotte dai nuovi moduli:

```json
{ "cmd": "preview_state_machine", "tree_path": "res://omniforge/hero_tree.tres" }
{ "cmd": "preview_cutscene", "sequence": [...] }
{ "cmd": "batch_import", "assets": ["hero_idle.tres", "hero_walk.tres", "hero_run.tres"] }
```

### Aggiornamento Modulo 7 (Preset System) — da AutoSprite

- **Moveset Preset:** salva non solo i parametri stilistici ma l'intero moveset definition JSON come preset condivisibile
- **Team sync:** i preset sono file `.omnipreset` esportabili — tutto il team usa gli stessi naming convention, timing, e loop points senza configurazione manuale

---

## STRUTTURA CARTELLE AGGIORNATA (nuovi moduli)

```
omniforge/
├── backend/
│   ├── processors/
│   │   ├── dna.py               # CharacterDNA extraction e comparison
│   │   ├── moveset.py           # Batch generation, direction mirror, inbetween
│   │   ├── state_machine.py     # Export AnimationTree per Godot
│   │   └── cutscene.py          # Storyboard e portrait generation
│   ├── exporters/               # Nuovo: un file per engine
│   │   ├── godot.py             # .tres SpriteFrames + AnimationTree
│   │   ├── unity.py             # .meta + Atlas JSON
│   │   ├── gamemaker.py         # .yy Sprite asset
│   │   ├── phaser.py            # Atlas JSON array format
│   │   └── generic.py           # JSON standard
│   └── library/
│       ├── moveset_presets.py   # Preset moveset (platformer, rpg, etc.)
│       └── asset_library.py     # Gestione categorie asset
└── frontend/
    └── workspaces/
        ├── MovesetWorkspace.tsx     # Moveset builder + batch generation
        ├── StateMachineWorkspace.tsx # State machine editor visuale
        ├── CutsceneWorkspace.tsx    # Storyboard e sequencer
        └── LibraryWorkspace.tsx     # Asset library browser
```

---

Le differenze chiave rispetto ad AutoSprite: tutto gira **localmente e gratuitamente** (nessun credito da acquistare), il DNA System è **esplicito e modificabile** (non una black box), la State Machine si **esporta direttamente** in Godot senza riconfigurare nulla, e il Moveset Builder gestisce **qualsiasi tipo di asset** (non solo personaggi). Ciò che AutoSprite fa in secondi pagando API cloud, OmniForge lo fa localmente via ComfyUI con più controllo.