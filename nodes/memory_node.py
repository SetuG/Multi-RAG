"""
MemoryNode: Maintains and updates debate memory/context.
"""

from datetime import datetime
from typing import List
from nodes.state_schema import DebateState, TurnEntry


class MemoryNode:
    
    
    def __init__(self):
        self.node_name = "MemoryNode"
    
    def extract_key_points(self, turns: List[TurnEntry]) -> str:
        
        if not turns:
            return "No arguments yet."
        
        
        agent_points = {}
        for turn in turns:
            agent = turn['agent']
            if agent not in agent_points:
                agent_points[agent] = []
            
            
            text = turn['text']
            first_sentence = text.split('.')[0] + '.'
            agent_points[agent].append(first_sentence[:100])
        
        
        summary_parts = []
        for agent, points in agent_points.items():
            summary_parts.append(f"{agent}: {len(points)} arguments presented")
            
            if points:
                summary_parts.append(f"  Latest: {points[-1]}")
        
        return "\n".join(summary_parts)
    
    def get_agent_context(self, agent_id: str, turns: List[TurnEntry]) -> str:
        
        if not turns:
            return "Opening statement."
        
        agent_name = "Scientist" if agent_id == "agent_a" else "Philosopher"
        opponent_name = "Philosopher" if agent_id == "agent_a" else "Scientist"
        
    
        opponent_turns = [t for t in turns if t['agent'] == opponent_name]
        
        if not opponent_turns:
            return "Opponent has not yet spoken."
        
        # Get last 2 opponent arguments
        recent_opponent = opponent_turns[-2:] if len(opponent_turns) >= 2 else opponent_turns
        
        context = f"Recent opponent arguments:\n"
        for turn in recent_opponent:
            context += f"- Round {turn['round']}: {turn['text'][:150]}...\n"
        
        return context
    
    def update_summary(self, state: DebateState) -> str:
        
        turns = state['turns']
        
        if not turns:
            return "Debate has not started."
        
        # Create structured summary
        summary = {
            'total_turns': len(turns),
            'agent_a_turns': len([t for t in turns if t['agent'] == 'Scientist']),
            'agent_b_turns': len([t for t in turns if t['agent'] == 'Philosopher']),
            'key_points': self.extract_key_points(turns)
        }
        
        summary_text = f"""Debate Summary (after {len(turns)} turns):
- Scientist has made {summary['agent_a_turns']} arguments
- Philosopher has made {summary['agent_b_turns']} arguments

Key Points:
{summary['key_points']}
"""
        
        return summary_text
    
    def process(self, state: DebateState) -> DebateState:
                
        new_summary = self.update_summary(state)
        state['memory_summary'] = new_summary
        
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node': self.node_name,
            'action': 'memory_updated',
            'total_turns': len(state['turns']),
            'summary_length': len(new_summary)
        }
        state['log_entries'].append(log_entry)
        
        return state