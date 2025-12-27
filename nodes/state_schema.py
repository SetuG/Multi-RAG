"""
State schema for the debate workflow.
Defines the shared state structure passed between nodes.
"""

from typing import TypedDict, List, Dict, Optional, Any


class TurnEntry(TypedDict):
    
    round: int
    agent: str
    text: str
    timestamp: str
    meta: Dict[str, Any]


class DebateState(TypedDict):
    
    
    topic: str
    turns: List[TurnEntry]
    current_round: int
    current_turn: str  
    debate_complete: bool
    
    
    memory_summary: str
    
   
    winner: Optional[str]
    judgment: str
    
    
    log_entries: List[Dict[str, Any]]
    timestamp: str