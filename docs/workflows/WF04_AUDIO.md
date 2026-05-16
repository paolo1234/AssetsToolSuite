# WF04 — Audio Module

> **Prerequisiti:** WF01 completato
> **Moduli:** MOD03 (Audio Module)
> **Output:** Adapter audio AI, waveform player, loop point editor, export .ogg/.wav

---

## Scope

1. Adapter AI per generazione audio: AudioLDM, MusicGen, ElevenLabs, Suno
2. Audio Tester con waveform visualizer e cursor scrubbing
3. Loop point editor visuale per gamedev
4. Effetti non-distruttivi: pitch shift, reverb, low-pass
5. Variazione casuale (N varianti di un SFX)
6. Export `.ogg` (compresso) e `.wav` (lossless)

---

## Audio Adapters

### AudioLDMAdapter (adapters/audio/audioldm.py)
- Generazione SFX locale via AudioLDM
- Parametri: prompt testuale, durata, num_inference_steps
- Output: `.wav` raw

### MusicGenAdapter
- Meta MusicGen per musica di sottofondo
- Parametri: prompt, durata, BPM target, temperature
- Output: `.wav` stereo

### ElevenLabsAdapter (adapters/audio/elevenlabs.py)
- Voice generation e SFX via API ElevenLabs
- Parametri: testo, voce, stabilità, similarity
- Output: `.mp3` → convertito in `.ogg`

### SunoAdapter
- Generazione musica via API Suno
- Parametri: prompt, genere, durata, strumentazione

---

## Audio Tester — Specifiche

### Waveform Visualizer
- Canvas HTML5 con rendering della waveform
- Cursor scrubbing: click/drag per posizionarsi nel file
- Zoom orizzontale per dettaglio
- Indicatore posizione corrente in secondi

### Loop Point Editor
- Marker visivi per loop in e loop out sulla waveform
- Drag per riposizionare i marker
- Preview del loop: riproduce la sezione in loop continuo
- Snap a zero-crossing per evitare click audio
- Export con metadata corretti per Godot `AudioStreamOGGVorbis.loop_begin/end`

### Effetti Non-Distruttivi
- **Pitch shift**: ±24 semitoni (via `pydub` o `librosa`)
- **Reverb**: room size, damping, wet/dry mix
- **Low-pass filter**: frequenza di taglio configurabile
- Tutti i parametri salvati nel manifest, applicati solo all'export
- Preview live: l'utente sente l'effetto in tempo reale

### Variazione Casuale
- Genera N varianti di un SFX (es. 5 "footstep" diversi)
- Variazioni: micro pitch shift random, timing leggero, lieve EQ change
- Output: N file numerati (footstep_001.ogg ... footstep_005.ogg)
- Utile per evitare ripetizione in-game

---

## API Endpoints

- `POST /api/audio/generate` — Genera audio (con adapter)
- `POST /api/audio/process` — Applica effetti
- `POST /api/audio/loop-points` — Imposta loop in/out
- `POST /api/audio/variations` — Genera N varianti
- `POST /api/audio/export` — Export in .ogg o .wav
- `GET /api/audio/{id}/waveform` — Dati waveform per visualizzazione

---

## Checklist

- [ ] `adapters/audio/audioldm.py`
- [ ] `adapters/audio/elevenlabs.py`
- [ ] `processors/audio.py` (effetti, variazioni, loop points)
- [ ] `routers/audio.py`
- [ ] Frontend: `AudioWorkspace.tsx`
- [ ] Frontend: Waveform visualizer
- [ ] Frontend: Loop point editor
- [ ] Frontend: `audioStore.ts`
- [ ] Test: genera SFX → visualizza waveform → imposta loop → export .ogg
