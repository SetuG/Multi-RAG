#!/usr/bin/env python3
"""
Generate DAG visualization for the debate workflow.
"""

from graphviz import Digraph
from pathlib import Path


def create_debate_dag():
    
    dot = Digraph(comment='Multi-Agent Debate DAG', format='png')
    dot.attr(rankdir='TB')  # Top to bottom
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', fontname='Arial')
    
    
    colors = {
        'input': '#E3F2FD',      
        'controller': '#FFF3E0',  # Light orange
        'agent': '#E8F5E9',       # Light green
        'memory': '#F3E5F5',      # Light purple
        'judge': '#FCE4EC',       # Light pink
        'logger': '#F5F5F5',      # Light gray
    }
    
    # Add nodes
    dot.node('start', 'START', shape='ellipse', fillcolor='#4CAF50', fontcolor='white')
    dot.node('user_input', 'UserInputNode\n(Validate Topic)', fillcolor=colors['input'])
    dot.node('controller', 'RoundsController\n(Enforce Turns)', fillcolor=colors['controller'])
    dot.node('agent_a', 'AgentA\n(Scientist)', fillcolor=colors['agent'])
    dot.node('agent_b', 'AgentB\n(Philosopher)', fillcolor=colors['agent'])
    dot.node('memory', 'MemoryNode\n(Update Context)', fillcolor=colors['memory'])
    dot.node('judge', 'JudgeNode\n(Evaluate & Decide)', fillcolor=colors['judge'])
    dot.node('logger', 'LoggerNode\n(Write Log)', fillcolor=colors['logger'])
    dot.node('end', 'END', shape='ellipse', fillcolor='#F44336', fontcolor='white')
    
    
    dot.edge('start', 'user_input', label='1. Initialize')
    dot.edge('user_input', 'controller', label='2. Topic validated')
    
    
    dot.edge('controller', 'agent_a', label='3a. AgentA turn')
    dot.edge('controller', 'agent_b', label='3b. AgentB turn')
    dot.edge('controller', 'judge', label='3c. Debate complete\n(8 rounds)')
    
    
    dot.edge('agent_a', 'memory', label='4. Argument added')
    dot.edge('agent_b', 'memory', label='4. Argument added')
    
    
    dot.edge('memory', 'controller', label='5. Memory updated\n(Loop until complete)', style='dashed')
    
    
    dot.edge('judge', 'logger', label='6. Judgment ready')
    dot.edge('logger', 'end', label='7. Log written')
    
    # Add legend
    with dot.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Workflow Legend', style='dashed')
        legend.node('leg1', 'Input/Output', shape='box', style='rounded,filled', fillcolor=colors['input'])
        legend.node('leg2', 'Control', shape='box', style='rounded,filled', fillcolor=colors['controller'])
        legend.node('leg3', 'Agents', shape='box', style='rounded,filled', fillcolor=colors['agent'])
        legend.node('leg4', 'Processing', shape='box', style='rounded,filled', fillcolor=colors['memory'])
        legend.attr(rank='same')
    
    return dot


def main():
    
    print(" Generating debate workflow DAG visualization...")
    
    # Create DAG
    dag = create_debate_dag()
    
    # Ensure output directory exists
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG and SVG
    output_path = output_dir / 'debate_dag'
    dag.render(output_path, cleanup=True)
    
    print(f"DAG visualization saved:")
    print(f"   {output_path}.png")
    
    # Also save the source
    with open(output_dir / 'debate_dag.dot', 'w') as f:
        f.write(dag.source)
    print(f"   {output_dir / 'debate_dag.dot'}")


if __name__ == '__main__':
    main()