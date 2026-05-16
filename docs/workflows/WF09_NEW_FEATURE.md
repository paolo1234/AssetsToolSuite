# 🚀 Workflow 09 — Aggiungere una Nuova Feature

Segui questo percorso per aggiungere un nuovo modulo (es. "Video Generator" o "Texture Mapping") a OmniForge.

---

## Passo 1: Backend Processor
Crea la logica pura in `backend/processors/{feature_name}.py`.
*   Usa classi con metodi `@staticmethod` dove possibile.
*   Mantieni il processore indipendente dalle API (deve poter funzionare anche come script standalone).

## Passo 2: API Router
Crea il router in `backend/routers/{feature_name}.py`.
*   Importa il processore e il `ManifestManager`.
*   Registra il router nel file `backend/main.py`.

## Passo 3: Frontend Store
Crea lo store Zustand in `frontend/src/store/{feature_name}Store.ts`.
*   Definisci l'interfaccia dello stato.
*   Implementa le chiamate `fetch()` agli endpoint creati nel Passo 2.

## Passo 4: UI Workspace
Crea il componente React in `frontend/src/workspaces/{FeatureName}Workspace.tsx`.
*   Usa il layout standard:
    ```tsx
    <div className="flex-1 flex flex-col h-full">
       <header className="p-4 border-b border-of-border"> ... </header>
       <main className="flex-1 overflow-auto p-4"> ... </main>
    </div>
    ```

## Passo 5: Registrazione Workspace
Aggiungi il nuovo workspace in `frontend/src/App.tsx`:
1.  Importa il componente.
2.  Aggiungilo alla lista `WORKSPACES`.
3.  Aggiungi l'icona corrispondente nella Sidebar.

---

## Checklist di Verifica
- [ ] Gli import sono assoluti? (es. `from config import settings`)
- [ ] I nuovi modelli Pydantic hanno valori di default per la compatibilità?
- [ ] `npm run build` passa senza errori TypeScript?
- [ ] Il backend si avvia senza `ImportError`?
