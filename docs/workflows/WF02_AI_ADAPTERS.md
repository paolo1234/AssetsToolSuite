# WF02 — AI Adapter Layer + Image Processor

> **Prerequisiti:** WF01 completato
> **Moduli:** MOD01 (Image & Sprite Generation)
> **Output:** Adapter AI funzionanti, pipeline image processing, inpainting canvas

---

## Scope

1. Implementazione AIAdapter per ComfyUI e DALL-E
2. PromptBuilder con tag di stile automatici dal progetto
3. Queue di generazione asincrona con priorità
4. Inpainting Canvas con Konva.js (3 layer separati)
5. Post-processing: rembg, Palette Quantizer, Pixel Art Filter, Batch Processing

---

## Adapters — Specifiche

### ComfyUIAdapter (adapters/comfyui.py)
- Connessione a ComfyUI locale via HTTP API (default `http://localhost:8188`)
- Workflow JSON template per txt2img e img2img
- Polling status via WebSocket di ComfyUI
- Download risultato e salvataggio in progetto
- Health check: verifica che il server risponda

### DallEAdapter (adapters/dalle.py)
- OpenAI API (DALL-E 3)
- Supporto parametri: size, quality, style
- Rate limiting per rispettare i limiti API
- Caching delle risposte per evitare rigenerazioni costose

### PromptBuilder (processors/image.py)
```python
class PromptBuilder:
    def build(self, user_prompt: str, project_manifest: ProjectManifest) -> str:
        """Aggiunge automaticamente i tag stilistici del progetto."""
        style_tags = manifest.get_style_tags()  # es. "pixel art, 16-bit, limited palette"
        return f"{user_prompt}, {', '.join(style_tags)}"
```

### GenerationQueue
- Coda asincrona `asyncio.PriorityQueue`
- Priorità: HIGH (utente attende), NORMAL (batch), LOW (background)
- Worker asincroni che processano la coda
- WebSocket notification al frontend per progress/completamento

---

## Inpainting Canvas — Specifiche

- Konva.js con 3 layer separati: `[background] [mask] [overlay]`
- Tool disponibili: pennello maschera, eraser, rettangolo, ellisse
- Dimensione pennello configurabile (1px-100px)
- Opacità maschera configurabile
- Undo/redo per le operazioni di disegno
- Pre-invio all'API: composizione automatica immagine + maschera nel formato corretto per ogni adapter

---

## Post-Processing — Specifiche

### rembg Integration
- Rimozione sfondo con anteprima real-time
- Modelli: `u2net`, `u2net_human_seg`, `isnet-general-use`
- Risultato visibile prima di confermare

### Palette Quantizer
- Import palette: `.pal`, `.gpl`, o estrazione da immagine
- Algoritmo: k-means per matching colori
- Dithering configurabile: None, Floyd-Steinberg, Ordered, Bayer
- Preview split-screen: originale vs quantizzato

### Pixel Art Filter
- Downscale controllato con nearest-neighbor
- Optional outline shader (colore e spessore configurabili)
- Preview live

### Batch Processing
- Seleziona N immagini
- Applica la stessa pipeline (rembg + palette + filter) a tutte
- Progress bar per file
- Risultati disponibili man mano

---

## API Endpoints

- `POST /api/generate/image` — Genera immagine (con adapter specificato)
- `GET /api/generate/queue` — Stato coda generazione
- `POST /api/process/remove-bg` — Rimuovi sfondo
- `POST /api/process/quantize-palette` — Applica palette
- `POST /api/process/pixel-art` — Applica filtro pixel art
- `POST /api/process/batch` — Pipeline batch
- `POST /api/process/inpaint` — Inpainting con maschera

---

## Checklist

- [ ] `adapters/comfyui.py`
- [ ] `adapters/dalle.py`
- [ ] `processors/image.py` (PromptBuilder + rembg + palette + pixel-art)
- [ ] `routers/images.py`
- [ ] Frontend: `ImageWorkspace.tsx`
- [ ] Frontend: Inpainting canvas con Konva.js
- [ ] Frontend: `imageStore.ts`
- [ ] Test: mock adapter con risposte fake
- [ ] Test: pipeline batch su 5 immagini
