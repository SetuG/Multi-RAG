"""
JudgeNode: Evaluates the debate and declares a winner.
"""

import random
from datetime import datetime
from typing import Dict, Any, Optional
from nodes.state_schema import DebateState


class JudgeNode:
    """
    Final judge that evaluates the debate and declares a winner.
    
    Evaluation criteria:
    - Logical coherence and consistency
    - Evidence and reasoning quality
    - Direct engagement with opponent's points
    - Clarity and persuasiveness
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.node_name = "JudgeNode"
        if seed is not None:
            random.seed(seed + 999)  # Different seed offset for judge
    
    def evaluate_coherence(self, turns: list, agent_name: str) -> float:
        """
        Evaluate logical coherence of an agent's arguments.
        
        Returns score 0.0-1.0
        """
        agent_turns = [t for t in turns if t['agent'] == agent_name]
        
        if not agent_turns:
            return 0.0
        
        # Check consistency (simple heuristic)
        total_length = sum(len(t['text']) for t in agent_turns)
        avg_length = total_length / len(agent_turns)
        
        # Prefer moderate length (too short or too long is bad)
        if 50 <= avg_length <= 300:
            length_score = 1.0
        elif avg_length < 50:
            length_score = 0.5
        else:
            length_score = 0.8
        
        # Check for variety (not repeating same patterns)
        unique_starts = len(set(t['text'][:20] for t in agent_turns))
        variety_score = min(unique_starts / len(agent_turns), 1.0)
        
        return (length_score + variety_score) / 2
    
    def evaluate_engagement(self, turns: list, agent_name: str) -> float:
        """
        Evaluate how well agent engaged with opponent.
        
        Returns score 0.0-1.0
        """
        agent_turns = [t for t in turns if t['agent'] == agent_name]
        opponent_name = "Philosopher" if agent_name == "Scientist" else "Scientist"
        opponent_turns = [t for t in turns if t['agent'] == opponent_name]
        
        if not agent_turns or not opponent_turns:
            return 0.5
        
        # Check if agent's arguments reference opponent's points
        engagement_count = 0
        
        for i, turn in enumerate(agent_turns):
            # Get opponent's previous turn
            if i < len(opponent_turns):
                opp_text = opponent_turns[i]['text'].lower()
                agent_text = turn['text'].lower()
                
                # Extract key words from opponent
                opp_words = set(opp_text.split())
                agent_words = set(agent_text.split())
                
                # Check overlap (indicates engagement)
                overlap = len(opp_words & agent_words)
                if overlap > 5:  # Meaningful overlap
                    engagement_count += 1
        
        return engagement_count / len(agent_turns) if agent_turns else 0.5
    
    def evaluate_strength(self, turns: list, agent_name: str) -> float:
        """
        Evaluate argument strength (simplified heuristic).
        
        Returns score 0.0-1.0
        """
        agent_turns = [t for t in turns if t['agent'] == agent_name]
        
        if not agent_turns:
            return 0.0
        
        # Check for evidence markers
        evidence_words = [
            'research', 'studies', 'data', 'evidence', 'facts',
            'historically', 'proven', 'demonstrates', 'shows'
        ]
        
        reasoning_words = [
            'therefore', 'because', 'thus', 'consequently',
            'implies', 'suggests', 'indicates', 'means'
        ]
        
        evidence_score = 0
        reasoning_score = 0
        
        for turn in agent_turns:
            text_lower = turn['text'].lower()
            
            # Count evidence markers
            evidence_score += sum(1 for word in evidence_words if word in text_lower)
            reasoning_score += sum(1 for word in reasoning_words if word in text_lower)
        
        # Normalize
        max_possible = len(agent_turns) * 2
        evidence_norm = min(evidence_score / max_possible, 1.0)
        reasoning_norm = min(reasoning_score / max_possible, 1.0)
        
        return (evidence_norm + reasoning_norm) / 2
    
    def generate_summary(self, state: DebateState) -> str:
        """
        Generate a comprehensive debate summary.
        """
        turns = state['turns']
        topic = state['topic']
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    DEBATE SUMMARY                            ║
╚══════════════════════════════════════════════════════════════╝

Topic: {topic}

Total Rounds: {len(turns)}
Duration: {len(turns)} arguments exchanged

Participants:
- Scientist (Agent A): {len([t for t in turns if t['agent'] == 'Scientist'])} arguments
- Philosopher (Agent B): {len([t for t in turns if t['agent'] == 'Philosopher'])} arguments

Key Arguments:
"""
        
        # Add key arguments from each side
        scientist_turns = [t for t in turns if t['agent'] == 'Scientist']
        philosopher_turns = [t for t in turns if t['agent'] == 'Philosopher']
        
        if scientist_turns:
            summary += f"\nScientist's main points:\n"
            for i, turn in enumerate(scientist_turns[:2], 1):
                summary += f"  {i}. {turn['text'][:100]}...\n"
        
        if philosopher_turns:
            summary += f"\nPhilosopher's main points:\n"
            for i, turn in enumerate(philosopher_turns[:2], 1):
                summary += f"  {i}. {turn['text'][:100]}...\n"
        
        return summary
    
    def determine_winner(self, state: DebateState) -> tuple[str, str]:
        """
        Evaluate both agents and determine the winner.
        
        Returns:
            (winner_name, justification)
        """
        turns = state['turns']
        
        # Evaluate both agents
        scientist_scores = {
            'coherence': self.evaluate_coherence(turns, 'Scientist'),
            'engagement': self.evaluate_engagement(turns, 'Scientist'),
            'strength': self.evaluate_strength(turns, 'Scientist')
        }
        
        philosopher_scores = {
            'coherence': self.evaluate_coherence(turns, 'Philosopher'),
            'engagement': self.evaluate_engagement(turns, 'Philosopher'),
            'strength': self.evaluate_strength(turns, 'Philosopher')
        }
        
        # Calculate total scores
        scientist_total = sum(scientist_scores.values())
        philosopher_total = sum(philosopher_scores.values())
        
        # Determine winner
        if scientist_total > philosopher_total:
            winner = "Scientist"
            winner_scores = scientist_scores
            margin = scientist_total - philosopher_total
        elif philosopher_total > scientist_total:
            winner = "Philosopher"
            winner_scores = philosopher_scores
            margin = philosopher_total - scientist_total
        else:
            # Tie - random selection
            winner = random.choice(["Scientist", "Philosopher"])
            winner_scores = scientist_scores if winner == "Scientist" else philosopher_scores
            margin = 0
        
        # Generate justification
        justification = f"""
Winner: {winner}

Evaluation Scores:
┌─────────────┬───────────┬──────────────┐
│ Criterion   │ Scientist │ Philosopher  │
├─────────────┼───────────┼──────────────┤
│ Coherence   │   {scientist_scores['coherence']:.2f}    │    {philosopher_scores['coherence']:.2f}       │
│ Engagement  │   {scientist_scores['engagement']:.2f}    │    {philosopher_scores['engagement']:.2f}       │
│ Strength    │   {scientist_scores['strength']:.2f}    │    {philosopher_scores['strength']:.2f}       │
├─────────────┼───────────┼──────────────┤
│ TOTAL       │   {scientist_total:.2f}    │    {philosopher_total:.2f}       │
└─────────────┴───────────┴──────────────┘

Reasoning:
The {winner} presented arguments with strong {'coherence' if winner_scores['coherence'] > 0.7 else 'engagement' if winner_scores['engagement'] > 0.7 else 'reasoning'}. 
Their arguments were {'well-structured' if winner_scores['coherence'] > 0.6 else 'engaged'} and {'evidence-based' if winner_scores['strength'] > 0.6 else 'logically sound'}.
The margin of victory was {margin:.2f} points, indicating a {'decisive' if margin > 0.5 else 'close but clear' if margin > 0.2 else 'very close'} win.
"""
        
        return winner, justification
    
    def process(self, state: DebateState) -> DebateState:
        """
        Evaluate the debate and produce final judgment.
        
        Args:
            state: Final debate state
            
        Returns:
            State with winner and judgment added
        """
        print("⚖️  Judge evaluating debate...\n")
        
        # Generate summary
        summary = self.generate_summary(state)
        
        # Determine winner
        winner, justification = self.determine_winner(state)
        
        # Update state
        state['winner'] = winner
        state['judgment'] = summary + "\n" + justification
        
        # Log
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node': self.node_name,
            'action': 'judgment_rendered',
            'winner': winner
        }
        state['log_entries'].append(log_entry)
        
        return state