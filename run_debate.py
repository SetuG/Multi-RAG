

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from langgraph.graph import StateGraph, END
from nodes.state_schema import DebateState
from nodes.user_input_node import UserInputNode
from nodes.agent_node import AgentANode, AgentBNode
from nodes.rounds_controller import RoundsControllerNode
from nodes.memory_node import MemoryNode
from nodes.judge_node import JudgeNode
from nodes.logger_node import LoggerNode
from utils.config_loader import load_config


def build_debate_graph(config: dict) -> StateGraph:
    """
    Constructs the LangGraph StateGraph for the debate workflow.
    
    Graph structure:
    UserInput -> RoundsController -> [AgentA/AgentB alternating] -> Memory -> Judge -> Logger -> END
    """
    
    user_input = UserInputNode()
    rounds_controller = RoundsControllerNode(max_rounds=8)
    agent_a = AgentANode(config['personas']['agent_a'], config.get('seed'))
    agent_b = AgentBNode(config['personas']['agent_b'], config.get('seed'))
    memory_node = MemoryNode()
    judge_node = JudgeNode(config.get('seed'))
    logger_node = LoggerNode(config['log_path'])
    
    # Create graph
    workflow = StateGraph(DebateState)
    
    # Add nodes
    workflow.add_node("user_input", user_input.process)
    workflow.add_node("rounds_controller", rounds_controller.process)
    workflow.add_node("agent_a", agent_a.process)
    workflow.add_node("agent_b", agent_b.process)
    workflow.add_node("memory", memory_node.process)
    workflow.add_node("judge", judge_node.process)
    workflow.add_node("logger", logger_node.process)
    
    # Set entry point
    workflow.set_entry_point("user_input")
    
    # Define edges
    workflow.add_edge("user_input", "rounds_controller")
    
    
    def route_from_controller(state: DebateState) -> str:
        if state['debate_complete']:
            return "judge"
        elif state['current_turn'] == 'agent_a':
            return "agent_a"
        else:
            return "agent_b"
    
    workflow.add_conditional_edges(
        "rounds_controller",
        route_from_controller,
        {
            "agent_a": "agent_a",
            "agent_b": "agent_b",
            "judge": "judge"
        }
    )
    
    workflow.add_edge("agent_a", "memory")
    workflow.add_edge("agent_b", "memory")
    workflow.add_edge("memory", "rounds_controller")
    
    
    workflow.add_edge("judge", "logger")
    workflow.add_edge("logger", END)
    
    return workflow.compile()


def print_banner():
    """Prints the debate system banner."""
    banner = """
    Multi-Agent Debate System (LangGraph)       
        ATG Technical Assignment     

    """
    print(banner)


def run_debate_cli(config_path: Optional[str] = None, 
                   seed: Optional[int] = None,
                   log_path: Optional[str] = None,
                   topic: Optional[str] = None):
    
    print_banner()
    
    
    config = load_config(config_path or 'config.yaml')
    
    
    if seed is not None:
        config['seed'] = seed
    if log_path is not None:
        config['log_path'] = log_path
    
    
    Path(config['log_path']).parent.mkdir(parents=True, exist_ok=True)
    
    
    print("Building debate workflow graph...")
    graph = build_debate_graph(config)
    
    
    if topic is None:
        print("\n" + "="*60)
        topic = input("Enter topic for debate: ").strip()
        print("="*60 + "\n")
    else:
        print(f"\nDebate Topic: {topic}\n")
    
    if not topic:
        print(" Error: Topic cannot be empty.")
        sys.exit(1)
    
    
    initial_state = {
        'topic': topic,
        'turns': [],
        'current_round': 0,
        'current_turn': 'agent_a',
        'debate_complete': False,
        'memory_summary': '',
        'winner': None,
        'judgment': '',
        'log_entries': [],
        'timestamp': datetime.now().isoformat()
    }
    
    print(f" Starting debate between {config['personas']['agent_a']['name']} "
          f"and {config['personas']['agent_b']['name']}...\n")
    
    
    try:
        final_state = graph.invoke(initial_state)
        
        print("\n" + "="*60)
        print(" DEBATE COMPLETE")
        print("="*60)
        print(f"\n{final_state['judgment']}")
        print(f"\n Full debate log saved to: {config['log_path']}")
        print(f" Total rounds: {final_state['current_round']}")
        
    except Exception as e:
        print(f"\nError during debate execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Parse CLI arguments and run the debate."""
    parser = argparse.ArgumentParser(
        description='Multi-Agent Debate System using LangGraph',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_debate.py
  python run_debate.py --seed 42 --log-path logs/debate_001.json
  python run_debate.py --config custom_config.yaml --seed 12345
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for deterministic behavior'
    )
    
    parser.add_argument(
        '--log-path',
        type=str,
        help='Custom log file path (default: from config)'
    )
    
    parser.add_argument(
        '--topic',
        type=str,
        help='Debate topic (skips interactive input)'
    )
    
    args = parser.parse_args()
    
    run_debate_cli(
        config_path=args.config,
        seed=args.seed,
        log_path=args.log_path,
        topic=args.topic
    )


if __name__ == '__main__':
    main()