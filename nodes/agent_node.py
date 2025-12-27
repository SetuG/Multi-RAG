"""
Agent nodes for debate participants.
Each agent has a specific persona and generates arguments.
"""

import random
import os
from groq import Groq  
from dotenv import load_dotenv
   
load_dotenv()
from datetime import datetime
from typing import Dict, Any, Optional
from nodes.state_schema import DebateState, TurnEntry


class DebateAgent:
    
    
    def __init__(self, persona_config: Dict[str, Any], seed: Optional[int] = None):
        self.persona = persona_config
        self.agent_id = persona_config['id']
        self.name = persona_config['name']
        self.role = persona_config['role']
        self.style = persona_config.get('style', '')
        
        if seed is not None:
            random.seed(seed + hash(self.agent_id))
    
    def get_relevant_context(self, state: DebateState) -> str:
        """
        Extract relevant context for this agent's next argument.
        
        Returns only:
        - Opponent's previous argument
        - Summary of key points made so far
        """
        turns = state['turns']
        if not turns:
            return "This is the opening statement."
        
        
        opponent_turns = [t for t in turns if t['agent'] != self.name]
        if opponent_turns:
            last_opponent = opponent_turns[-1]
            context = f"Opponent's last point: {last_opponent['text']}\n"
        else:
            context = ""
        
        
        context += f"Current round: {state['current_round'] + 1}/8\n"
        
        
        if state.get('memory_summary'):
            context += f"Key points so far: {state['memory_summary']}\n"
        
        return context
    
    def check_similarity(self, new_argument: str, previous_turns: list) -> bool:
        """
        Check if argument is too similar to previous ones (basic check).
        
        Returns True if argument appears to be a duplicate.
        """
        
        my_turns = [t['text'] for t in previous_turns if t['agent'] == self.name]
        
        if not my_turns:
            return False
        
        
        new_words = set(new_argument.lower().split())
        
        for prev in my_turns:
            prev_words = set(prev.lower().split())
            
            
            overlap = len(new_words & prev_words)
            similarity = overlap / max(len(new_words), len(prev_words))
            
            if similarity > 0.7:
                return True
        
        return False
    
    def generate_argument(self, topic: str, context: str, round_num: int) -> str:
        
        
        
        system_prompt = f"""You are a {self.role} with expertise in {self.persona.get('expertise', 'general knowledge')}.
        Style: {self.style}

You are participating in a structured debate. Generate arguments that are:
- Logical and well-reasoned
- Directly relevant to the topic
- 2-3 sentences long
- Not repetitive of your previous points"""

        user_prompt = f"""Topic: {topic}

Context:
{context}

Generate your argument for round {round_num}."""

        try:
            # Initialize Groq client (correct for Groq!)
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            # Call Groq API
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            argument = response.choices[0].message.content.strip()
            return argument
            
        except Exception as e:
            print(f"  Groq API Error: {e}")
            # Fallback response
            return f"As a {self.role}, I believe the evidence regarding {topic} supports a balanced approach based on {self.persona.get('expertise', 'careful analysis')}."

    
    
    
    def process(self, state: DebateState) -> DebateState:
        
        topic = state['topic']
        round_num = state['current_round'] + 1
        
        
        context = self.get_relevant_context(state)
        
        
        max_attempts = 3
        for attempt in range(max_attempts):
            argument = self.generate_argument(topic, context, round_num)
            
            
            if not self.check_similarity(argument, state['turns']):
                break
            
            if attempt == max_attempts - 1:
                
                argument += f" This point is particularly relevant in round {round_num}."
        
        
        turn: TurnEntry = {
            'round': round_num,
            'agent': self.name,
            'text': argument,
            'timestamp': datetime.now().isoformat(),
            'meta': {
                'agent_id': self.agent_id,
                'role': self.role,
                'context_length': len(context)
            }
        }
        
        
        state['turns'].append(turn)
        
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node': f'{self.agent_id}_node',
            'action': 'argument_generated',
            'round': round_num,
            'agent': self.name,
            'argument_length': len(argument)
        }
        state['log_entries'].append(log_entry)
        
        
        print(f"[Round {round_num}] {self.name}: {argument}\n")
        
        return state


class AgentANode(DebateAgent):
    """Agent A - typically the Scientist persona."""
    
    def __init__(self, persona_config: Dict[str, Any], seed: Optional[int] = None):
        super().__init__(persona_config, seed)


class AgentBNode(DebateAgent):
    """Agent B - typically the Philosopher persona."""
    
    def __init__(self, persona_config: Dict[str, Any], seed: Optional[int] = None):
        super().__init__(persona_config, seed)