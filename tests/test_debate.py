"""
Unit tests for the debate system.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from nodes.state_schema import DebateState, TurnEntry
from nodes.user_input_node import UserInputNode
from nodes.agent_node import AgentANode, AgentBNode
from nodes.rounds_controller import RoundsControllerNode
from nodes.memory_node import MemoryNode
from nodes.judge_node import JudgeNode
from nodes.logger_node import LoggerNode


class TestUserInputNode:
    """Tests for UserInputNode."""
    
    def test_valid_topic(self):
        node = UserInputNode()
        state = {
            'topic': 'Should AI be regulated?',
            'log_entries': []
        }
        result = node.process(state)
        assert result['topic'] == 'Should AI be regulated?'
        assert len(result['log_entries']) == 1
    
    def test_topic_too_short(self):
        node = UserInputNode()
        state = {
            'topic': 'AI',
            'log_entries': []
        }
        with pytest.raises(ValueError):
            node.process(state)
    
    def test_topic_sanitization(self):
        node = UserInputNode()
        state = {
            'topic': 'Should   AI   be   regulated?  ',
            'log_entries': []
        }
        result = node.process(state)
        assert result['topic'] == 'Should AI be regulated?'


class TestRoundsController:
    """Tests for RoundsControllerNode."""
    
    def test_initial_turn_assignment(self):
        node = RoundsControllerNode(max_rounds=8)
        state = {
            'topic': 'Test topic',
            'turns': [],
            'current_round': 0,
            'current_turn': '',
            'debate_complete': False,
            'log_entries': []
        }
        result = node.process(state)
        assert result['current_turn'] == 'agent_a'
        assert not result['debate_complete']
    
    def test_turn_alternation(self):
        node = RoundsControllerNode(max_rounds=8)
        
        # Simulate Agent A's turn
        turn_a: TurnEntry = {
            'round': 1,
            'agent': 'Scientist',
            'text': 'Test argument A',
            'timestamp': datetime.now().isoformat(),
            'meta': {}
        }
        
        state = {
            'topic': 'Test topic',
            'turns': [turn_a],
            'current_round': 0,
            'current_turn': 'agent_a',
            'debate_complete': False,
            'log_entries': []
        }
        
        result = node.process(state)
        assert result['current_turn'] == 'agent_b'
        assert result['current_round'] == 1
    
    def test_debate_completion(self):
        node = RoundsControllerNode(max_rounds=8)
        
        # Create 8 turns
        turns = []
        for i in range(8):
            agent = 'Scientist' if i % 2 == 0 else 'Philosopher'
            turn: TurnEntry = {
                'round': i + 1,
                'agent': agent,
                'text': f'Argument {i+1}',
                'timestamp': datetime.now().isoformat(),
                'meta': {}
            }
            turns.append(turn)
        
        state = {
            'topic': 'Test topic',
            'turns': turns,
            'current_round': 7,
            'current_turn': 'agent_b',
            'debate_complete': False,
            'log_entries': []
        }
        
        result = node.process(state)
        assert result['debate_complete'] is True
        assert result['current_round'] == 8


class TestAgentNode:
    """Tests for Agent nodes."""
    
    def test_agent_generates_argument(self):
        config = {
            'id': 'agent_a',
            'name': 'Scientist',
            'role': 'Research Scientist',
            'expertise': 'testing',
            'style': 'analytical'
        }
        agent = AgentANode(config, seed=42)
        
        state = {
            'topic': 'Should AI be regulated?',
            'turns': [],
            'current_round': 0,
            'memory_summary': '',
            'log_entries': []
        }
        
        result = agent.process(state)
        assert len(result['turns']) == 1
        assert result['turns'][0]['agent'] == 'Scientist'
        assert result['turns'][0]['round'] == 1
    
    def test_duplicate_detection(self):
        config = {
            'id': 'agent_a',
            'name': 'Scientist',
            'role': 'Research Scientist',
            'expertise': 'testing'
        }
        agent = AgentANode(config, seed=42)
        
        # Create previous turn
        prev_turn: TurnEntry = {
            'round': 1,
            'agent': 'Scientist',
            'text': 'This is a test argument about regulation',
            'timestamp': datetime.now().isoformat(),
            'meta': {}
        }
        
        new_arg = 'This is a test argument about regulation'
        
        is_dup = agent.check_similarity(new_arg, [prev_turn])
        assert is_dup is True


class TestMemoryNode:
    """Tests for MemoryNode."""
    
    def test_memory_update(self):
        node = MemoryNode()
        
        turn: TurnEntry = {
            'round': 1,
            'agent': 'Scientist',
            'text': 'Test argument',
            'timestamp': datetime.now().isoformat(),
            'meta': {}
        }
        
        state = {
            'topic': 'Test topic',
            'turns': [turn],
            'memory_summary': '',
            'log_entries': []
        }
        
        result = node.process(state)
        assert result['memory_summary'] != ''
        assert 'Scientist' in result['memory_summary']
    
    def test_key_points_extraction(self):
        node = MemoryNode()
        
        turns = [
            {
                'round': 1,
                'agent': 'Scientist',
                'text': 'First point about regulation.',
                'timestamp': datetime.now().isoformat(),
                'meta': {}
            },
            {
                'round': 2,
                'agent': 'Philosopher',
                'text': 'Counter-argument about freedom.',
                'timestamp': datetime.now().isoformat(),
                'meta': {}
            }
        ]
        
        key_points = node.extract_key_points(turns)
        assert 'Scientist' in key_points
        assert 'Philosopher' in key_points


class TestJudgeNode:
    """Tests for JudgeNode."""
    
    def test_judge_declares_winner(self):
        node = JudgeNode(seed=42)
        
        turns = []
        for i in range(8):
            agent = 'Scientist' if i % 2 == 0 else 'Philosopher'
            turn: TurnEntry = {
                'round': i + 1,
                'agent': agent,
                'text': f'Strong argument number {i+1} with evidence and reasoning.',
                'timestamp': datetime.now().isoformat(),
                'meta': {}
            }
            turns.append(turn)
        
        state = {
            'topic': 'Should AI be regulated?',
            'turns': turns,
            'current_round': 8,
            'debate_complete': True,
            'memory_summary': 'Test summary',
            'log_entries': []
        }
        
        result = node.process(state)
        assert result['winner'] in ['Scientist', 'Philosopher']
        assert result['judgment'] != ''
        assert 'Winner:' in result['judgment']


class TestLoggerNode:
    """Tests for LoggerNode."""
    
    def test_log_writing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / 'test_log.json'
            node = LoggerNode(str(log_path))
            
            state = {
                'topic': 'Test topic',
                'turns': [],
                'current_round': 0,
                'debate_complete': True,
                'memory_summary': 'Test',
                'winner': 'Scientist',
                'judgment': 'Test judgment',
                'log_entries': [],
                'timestamp': datetime.now().isoformat()
            }
            
            result = node.process(state)
            
            assert log_path.exists()
            assert log_path.stat().st_size > 0
            
            # Check text log also created
            text_log = log_path.with_suffix('.txt')
            assert text_log.exists()


class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_full_debate_workflow(self):
        
        
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])