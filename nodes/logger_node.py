

import json
from datetime import datetime
from pathlib import Path
from nodes.state_schema import DebateState


class LoggerNode:
    
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.node_name = "LoggerNode"
    
    def serialize_state(self, state: DebateState) -> dict:
        
        return {
            'metadata': {
                'topic': state['topic'],
                'total_rounds': state['current_round'],
                'debate_complete': state['debate_complete'],
                'timestamp': state['timestamp'],
                'log_generated': datetime.now().isoformat()
            },
            'participants': {
                'agent_a': {
                    'name': 'Scientist',
                    'turns': len([t for t in state['turns'] if t['agent'] == 'Scientist'])
                },
                'agent_b': {
                    'name': 'Philosopher',
                    'turns': len([t for t in state['turns'] if t['agent'] == 'Philosopher'])
                }
            },
            'transcript': state['turns'],
            'memory_summary': state['memory_summary'],
            'final_judgment': {
                'winner': state.get('winner'),
                'judgment_text': state.get('judgment', '')
            },
            'node_log': state['log_entries']
        }
    
    def write_log(self, data: dict) -> None:
        """
        Write log data to file in JSON format.
        """
        
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write as formatted JSON
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_text_summary(self, state: DebateState) -> str:
        """
        Generate a human-readable text summary.
        """
        summary = f"""

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Topic: {state['topic']}
Total Rounds: {state['current_round']}
Winner: {state.get('winner', 'Not determined')}

FULL TRANSCRIPT:
"""
        
        for turn in state['turns']:
            summary += f"\n[Round {turn['round']}] {turn['agent']}:\n"
            summary += f"{turn['text']}\n"
            summary += f"({turn['timestamp']})\n"
        
        summary += f"\n\nFINAL JUDGMENT:\n{state.get('judgment', 'Not available')}\n"
        
        return summary
    
    def process(self, state: DebateState) -> DebateState:
       
        print(f"📝 Writing debate log to {self.log_path}...")
        
        try:
            
            log_data = self.serialize_state(state)
            
            
            self.write_log(log_data)
            
            # Optionally write text summary
            text_log_path = self.log_path.with_suffix('.txt')
            text_summary = self.generate_text_summary(state)
            
            with open(text_log_path, 'w', encoding='utf-8') as f:
                f.write(text_summary)
            
            print(f"Log successfully written:")
            print(f"   JSON: {self.log_path}")
            print(f"   Text: {text_log_path}")
            
            # Add final log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'node': self.node_name,
                'action': 'log_written',
                'path': str(self.log_path),
                'size_bytes': self.log_path.stat().st_size
            }
            state['log_entries'].append(log_entry)
            
        except Exception as e:
            print(f" Error writing log: {e}")
            raise
        
        return state