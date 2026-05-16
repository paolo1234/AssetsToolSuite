"""
OmniForge Backend — Logic Processor
Handles state machine definitions, movesets, and DNA metadata.
"""

from __future__ import annotations

from typing import Any, List, Dict
from pydantic import BaseModel


class StateTransition(BaseModel):
    from_state: str
    to_state: str
    trigger: str
    condition: Optional[str] = None


class StateMachine(BaseModel):
    id: str
    name: str
    states: List[str]
    transitions: List[StateTransition]
    initial_state: str


class Moveset(BaseModel):
    id: str
    name: str
    animations: Dict[str, str]  # state_name -> asset_id
    tags: List[str]


class LogicProcessor:
    """
    Logic for managing game character behavior definitions.
    """

    @staticmethod
    def export_godot_state_machine(sm: StateMachine) -> str:
        """
        Generate a Godot 4.x AnimationNodeStateMachine resource string.
        """
        res = [
            '[gd_resource type="AnimationNodeStateMachine" format=3]',
            '',
            '[resource]'
        ]
        
        # In a real app, this would be much more complex
        # involving node positions and transition objects
        for state in sm.states:
            res.append(f'states/{state}/node = SubResource("AnimationNodeAnimation_{state}")')
            res.append(f'states/{state}/position = Vector2(0, 0)')
            
        return "\n".join(res)
