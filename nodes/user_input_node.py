"""
UserInputNode: Validates and sanitizes debate topic input.
"""

import re
from datetime import datetime
from nodes.state_schema import DebateState


class UserInputNode:
    
    
    MIN_LENGTH = 10
    MAX_LENGTH = 500
    
    def __init__(self):
        self.node_name = "UserInputNode"
    
    def sanitize_topic(self, topic: str) -> str:
        
        
        topic = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', topic)
        
        topic = ' '.join(topic.split())
        return topic.strip()
    
    def validate_topic(self, topic: str) -> tuple[bool, str]:
        
        if not topic or not topic.strip():
            return False, "Topic cannot be empty"
        
        if len(topic) < self.MIN_LENGTH:
            return False, f"Topic too short (minimum {self.MIN_LENGTH} characters)"
        
        if len(topic) > self.MAX_LENGTH:
            return False, f"Topic too long (maximum {self.MAX_LENGTH} characters)"
        
        return True, ""
    
    def process(self, state: DebateState) -> DebateState:
        
        topic = state.get('topic', '')
        
        
        sanitized_topic = self.sanitize_topic(topic)
        
        
        is_valid, error_msg = self.validate_topic(sanitized_topic)
        
        if not is_valid:
            raise ValueError(f"Topic validation failed: {error_msg}")
        
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node': self.node_name,
            'action': 'topic_validated',
            'topic': sanitized_topic,
            'original_length': len(topic),
            'sanitized_length': len(sanitized_topic)
        }
        
        
        state['topic'] = sanitized_topic
        state['log_entries'].append(log_entry)
        
        print(f"Topic validated: '{sanitized_topic[:60]}{'...' if len(sanitized_topic) > 60 else ''}'")
        
        return state