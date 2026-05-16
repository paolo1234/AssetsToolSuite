# 📜 OmniForge — Development & Maintenance Guide

Questa guida stabilisce le regole ferree per modificare OmniForge senza introdurre regressioni o rompere l'architettura SSOT (Single Source of Truth).

---

## 1. Regole degli Import (Python)
**MAI usare import relativi.** 
Il backend è configurato per essere eseguito dalla cartella `omniforge/backend` con `PYTHONPATH=.`.

*   ❌ **ERRORE**: `from .config import settings` o `from ..project.manifest import ...`
*   ✅ **CORRETTO**: `from config import settings` o `from project.manifest import ...`

Questo garantisce che il server `uvicorn` e gli script di test funzionino sempre senza errori di "no known parent package".

---

## 2. Modifica del Manifest (SSOT)
Il file `project.json` in ogni progetto è la verità assoluta.
1.  Se aggiungi un campo ai metadati degli asset, aggiorna il modello Pydantic in `backend/project/manifest.py`.
2.  Usa sempre `Optional` e valori di default per garantire la compatibilità con i vecchi progetti.
3.  Ogni modifica al manifest deve passare attraverso `ManifestManager`. Mai scrivere direttamente sul file JSON da altri moduli.

---

## 3. Coerenza Frontend/Backend
OmniForge usa un approccio "API-First":
1.  Definisci l'endpoint in un router FastAPI.
2.  Testa l'endpoint con `pytest` o `curl`.
3.  Crea lo Store Zustand corrispondente in `frontend/src/store/`.
4.  Implementa il Workspace UI.

---

## 4. Gestione Errori
*   **Backend**: Usa `raise HTTPException(status_code=..., detail="...")` per gli errori API.
*   **Frontend**: Gestisci i fallimenti nei blocchi `try/catch` degli store e mostra il messaggio di errore nell'Inspector o in una notifica.

---

## 5. Testing
Prima di fare una commit, esegui sempre i test di integrazione:
```bash
cd omniforge/backend
set PYTHONPATH=.
pytest tests/test_api.py
```
Se i test falliscono, la feature NON è pronta.
