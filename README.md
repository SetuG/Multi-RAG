# Multi-Agent Debate System (LangGraph)

A structured debate system built with LangGraph featuring two AI agents engaging in 8 rounds of argumentation, with automated judging and comprehensive logging.

##  Requirements

- Python 3.8+
- LangGraph 0.0.20+
- See `requirements.txt` for complete list

##  Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd multi-agent-debate
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```


## Usage

### Basic Usage

Run an interactive debate:
```bash
python run_debate.py
```

You'll be prompted to enter a debate topic:
```
Enter topic for debate: Should AI be regulated like medicine?
```
### How to run

** Run**:
```bash
python run_debate.py --seed 42
```

### Node Roles and DAG Structure
System Architecture

The debate system is implemented using a Directed Acyclic Graph (DAG) built with LangGraph.
It consists of 7 specialized nodes, each responsible for a specific stage of the debate workflow.

Node Descriptions
- UserInputNode — Input Validation

Validates and sanitizes the debate topic

Ensures topic length is between 10–500 characters

- RoundsController — Flow Control

Manages and enforces 8 structured debate rounds

Alternates turns between debaters

Ensures logical flow and coherence between responses

- Agent A — Debater (Scientist)

Acts as a scientific debater

Generates evidence-based arguments

Powered by Groq AI

- Agent B — Debater (Philosopher)

Acts as a philosophical debater

Produces conceptual and reasoning-driven arguments

Powered by Groq AI

- MemoryNode — Context Manager

Maintains full debate history

Supplies relevant context to each agent

Ensures arguments remain consistent and contextual

- JudgeNode — Evaluator

Evaluates each round of arguments

Scores based on:

Coherence

Engagement

Argument Strength

- LoggerNode — Data Persistence

Logs entire debate transcript

Stores outputs in:

JSON format

Text files
