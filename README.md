# ADK Agents Repository

This repository contains multiple agent implementations using Google ADK (Agent Development Kit).

## Structure

```
Agent/
├── 1.adk-quickstart/
│   └── first_agent/
│       ├── __init__.py
│       └── agent.py
└── [other agent folders...]
```

## Agents

### first_agent

A helpful assistant agent using Gemini 2.5 Flash model.

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Each agent folder contains its own implementation. Import and use agents as needed.

## Requirements

- Python 3.x
- Google ADK

## License

[Add your license here]
