# 🛠️ OmniForge Asset Suite

**OmniForge** è la suite definitiva per lo sviluppo procedurale di asset per videogiochi, progettata specificamente per Godot 4.x ma compatibile con Unity, GameMaker e Phaser. Utilizza l'intelligenza artificiale per automatizzare la creazione di sprite, animazioni, audio e logica di gioco, mantenendo una coerenza visiva assoluta tramite il sistema "DNA Lock".

![OmniForge Header](https://via.placeholder.com/1200x400.png?text=OmniForge+Asset+Suite)

---

## 🚀 Caratteristiche Principali

*   **Generazione AI Coerente**: Crea personaggi, nemici e scenari usando ComfyUI o DALL-E 3. Il sistema **DNA Lock** garantisce che lo stesso personaggio mantenga le sue caratteristiche in ogni animazione o espressione.
*   **Pipeline Animazioni Procedurale**: Trasforma prompt testuali in spritesheet completi, pronti per l'uso, con generazione automatica di frame intermedi.
*   **Studio Audio AI**: Genera effetti sonori (SFX) e musica d'ambiente (BGM) perfettamente sincronizzati con i tuoi asset visivi.
*   **Godot Live Bridge**: Sincronizzazione in tempo reale con l'editor di Godot. Visualizza le modifiche agli asset istantaneamente nel tuo gioco senza dover riavviare.
*   **Gestione Versioni (SSOT)**: Ogni asset ha una cronologia versioni (fino a 10). Il manifest del progetto è l'unica "Fonte di Verità" (Single Source of Truth).
*   **Esportazione Multi-Engine**: Esporta pacchetti ottimizzati per Godot (.tscn), Unity (.meta), GameMaker (.yy) e Phaser (JSON Atlas).

---

## 📦 Installazione

OmniForge richiede **Python 3.10+** e **Node.js 18+**.

### Metodo Automatico (Windows)
Abbiamo incluso degli script "one-click" per facilitare tutto:

1.  Esegui `install.bat` per installare tutte le dipendenze (Python & Node).
2.  Esegui `start.bat` per avviare l'intera suite.

### Metodo Manuale
Se preferisci farlo manualmente:

**Backend:**
```bash
cd omniforge/backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd omniforge/frontend
npm install
npm run dev
```

---

## 🛠️ Configurazione

Puoi configurare OmniForge tramite variabili d'ambiente o modificando `omniforge/backend/config.py`.

| Variabile | Descrizione | Default |
| :--- | :--- | :--- |
| `OMNIFORGE_DATA` | Percorso dove salvare i progetti | `%USERPROFILE%/OmniForge` |
| `OPENAI_API_KEY` | Chiave per DALL-E 3 / GPT-4 | - |
| `COMFYUI_URL` | Indirizzo del server ComfyUI locale | `http://localhost:8188` |
| `ELEVENLABS_API_KEY` | Chiave per la generazione vocale | - |

---

## 🎮 Uso del Godot Bridge

1.  Copia la cartella `omniforge/godot_bridge` nel tuo progetto Godot.
2.  Aggiungi il nodo `OmniForgeBridge.gd` come Singleton (Autoload) o in una scena di test.
3.  OmniForge si connetterà automaticamente tramite WebSocket (Porta 47832).
4.  Ogni asset generato nella suite apparirà istantaneamente nella cartella `res://omniforge_assets/`.

---

## 📂 Struttura del Progetto

```text
OmniForge/
├── omniforge/
│   ├── backend/          # FastAPI Server + AI Processors
│   ├── frontend/         # React + Vite + Tailwind UI
│   └── godot_bridge/     # Script GDScript per l'integrazione
├── docs/                 # Documentazione tecnica e workflow
├── install.bat           # Installer automatico (Windows)
└── start.bat             # Avvio rapido (Windows)
```

---

## 📜 Licenza
Progetto sviluppato per Advanced Agentic Coding. Licenza MIT.

---
*Creato con ❤️ da Antigravity per gli sviluppatori Godot.*
