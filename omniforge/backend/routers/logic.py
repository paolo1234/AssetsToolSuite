"""
OmniForge Backend — Logic Router
Handles state machine and moveset CRUD operations.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException
from .project import _get_manager
from ..processors.logic import StateMachine, Moveset

router = APIRouter(prefix="/api/logic", tags=["logic"])

@router.get("/{project_id}/statemachines", response_model=List[StateMachine])
async def list_state_machines(project_id: str):
    mgr = _get_manager(project_id)
    return mgr.manifest.presets.get("state_machines", [])

@router.post("/{project_id}/statemachines")
async def create_state_machine(project_id: str, sm: StateMachine):
    mgr = _get_manager(project_id)
    sms = mgr.manifest.presets.get("state_machines", [])
    sms.append(sm.dict())
    mgr.update_manifest({"presets": {**mgr.manifest.presets, "state_machines": sms}})
    return sm

@router.get("/{project_id}/movesets", response_model=List[Moveset])
async def list_movesets(project_id: str):
    mgr = _get_manager(project_id)
    return mgr.manifest.presets.get("movesets", [])

@router.post("/{project_id}/movesets")
async def create_moveset(project_id: str, ms: Moveset):
    mgr = _get_manager(project_id)
    mss = mgr.manifest.presets.get("movesets", [])
    mss.append(ms.dict())
    mgr.update_manifest({"presets": {**mgr.manifest.presets, "movesets": mss}})
    return ms
