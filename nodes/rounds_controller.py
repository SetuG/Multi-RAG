"""
RoundsControllerNode: Enforces turn order and validates debate progress.
"""

from datetime import datetime
from nodes.state_schema import DebateState


class RoundsControllerNode:
   
    
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds
        self.node_name = "RoundsControllerNode"
    
    def validate_turn_order(self, state: DebateState) -> bool:
        
        turns = state['turns']
        
        if not turns:
            return True 
        
        last_turn = turns[-1]
        current_agent = state['current_turn']
        
        
        if last_turn['agent'] == 'Scientist' and current_agent != 'agent_b':
            return False
        if last_turn['agent'] == 'Philosopher' and current_agent != 'agent_a':
            return False
        
        return True
    
    def check_logical_coherence(self, state: DebateState) -> tuple[bool, str]:
        
        turns = state['turns']
        
        if not turns:
            return True, ""
        
        last_turn = turns[-1]
        text = last_turn['text']
        topic = state['topic']
        
        
        if len(text) < 20:
            return False, "Argument too short (< 20 characters)"
        
        
        if len(text) > 1000:
            return False, "Argument too long (> 1000 characters)"
        
        
        topic_words = set(topic.lower().split())
        text_words = set(text.lower().split())
        
        
        if not (topic_words & text_words):
            return False, "Argument doesn't reference debate topic"
        
        
        agent_name = last_turn['agent']
        agent_turns = [t['text'].lower() for t in turns if t['agent'] == agent_name]
        
        if len(agent_turns) > 1:
            
            positive_words = {'should', 'must', 'essential', 'necessary', 'important'}
            negative_words = {'should not', 'must not', "shouldn't", "mustn't", 'unnecessary'}
            
            has_positive = any(word in ' '.join(agent_turns[:-1]) for word in positive_words)
            has_negative = any(word in agent_turns[-1] for word in negative_words)
            
            if has_positive and has_negative:
                
                return True, "Possible contradiction detected (logged for review)"
        
        return True, ""
    
    def determine_next_turn(self, state: DebateState) -> str:
        
        turns = state['turns']
        
        if not turns:
            return 'agent_a'  
        
        last_turn = turns[-1]
        
        
        if last_turn['agent'] == 'Scientist':
            return 'agent_b'
        else:
            return 'agent_a'
    
    def process(self, state: DebateState) -> DebateState:
        
        current_round = state['current_round']
        turns = state['turns']
        
        if len(turns) > current_round:
            
            is_coherent, issue = self.check_logical_coherence(state)
            
            if not is_coherent:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'node': self.node_name,
                    'action': 'coherence_issue',
                    'issue': issue,
                    'round': current_round + 1
                }
                state['log_entries'].append(log_entry)
                print(f"⚠️  Coherence warning (Round {current_round + 1}): {issue}")
            elif issue:
                
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'node': self.node_name,
                    'action': 'coherence_warning',
                    'warning': issue,
                    'round': current_round + 1
                }
                state['log_entries'].append(log_entry)
            
            
            state['current_round'] = len(turns)
        
        
        if state['current_round'] >= self.max_rounds:
            state['debate_complete'] = True
            state['current_turn'] = ''
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'node': self.node_name,
                'action': 'debate_completed',
                'total_rounds': state['current_round']
            }
            state['log_entries'].append(log_entry)
            
            print(f"\n Debate complete after {state['current_round']} rounds.\n")
            
        else:
            
            next_turn = self.determine_next_turn(state)
            state['current_turn'] = next_turn
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'node': self.node_name,
                'action': 'turn_assigned',
                'next_turn': next_turn,
                'round': state['current_round'] + 1
            }
            state['log_entries'].append(log_entry)
        
        return state