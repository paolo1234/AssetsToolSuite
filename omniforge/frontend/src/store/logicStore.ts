/**
 * OmniForge — Logic Store (Zustand)
 * Handles movesets and state machine state.
 */

import { create } from 'zustand';

export interface StateMachine {
  id: string;
  name: string;
  states: string[];
  transitions: any[];
}

export interface Moveset {
  id: string;
  name: string;
  animations: Record<string, string>;
}

interface LogicState {
  stateMachines: StateMachine[];
  movesets: Moveset[];
  
  fetchLogic: (projectId: string) => Promise<void>;
  createStateMachine: (projectId: string, sm: StateMachine) => Promise<void>;
  createMoveset: (projectId: string, ms: Moveset) => Promise<void>;
}

export const useLogicStore = create<LogicState>((set) => ({
  stateMachines: [],
  movesets: [],

  fetchLogic: async (projectId) => {
    try {
      const [smRes, msRes] = await Promise.all([
        fetch(`/api/logic/${projectId}/statemachines`),
        fetch(`/api/logic/${projectId}/movesets`)
      ]);
      const [stateMachines, movesets] = await Promise.all([smRes.json(), msRes.json()]);
      set({ stateMachines, movesets });
    } catch (e) {
      console.error(e);
    }
  },

  createStateMachine: async (projectId, sm) => {
    try {
      await fetch(`/api/logic/${projectId}/statemachines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sm),
      });
      // Refresh list
    } catch (e) {
      console.error(e);
    }
  },

  createMoveset: async (projectId, ms) => {
    try {
      await fetch(`/api/logic/${projectId}/movesets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ms),
      });
    } catch (e) {
      console.error(e);
    }
  },
}));
