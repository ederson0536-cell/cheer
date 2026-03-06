# Knowledge Graph V3.0 for OpenClaw

**OpenClaw Skill** - LLM External Brain & Autonomous Learning System

## ⭐ NEW: LLM Brain

Give the LLM a persistent memory!

```python
from llm_brain import LLMBrain

brain = LLMBrain()

# Query templates
code = brain.query("flask_login")[0]["content"]

# Store knowledge
brain.store(task_type="vue_auth", content=vue_code, tags=["vue", "auth"])

# Search
results = brain.search("authentication")

# Add reflection
brain.add_reflection("Vue Composition API is cleaner")
```

## Quick Start

```bash
# Install
git clone https://github.com/clowbot123-arch/knowledge-graph-v3.git
cd knowledge-graph-v3

# Run LLM Brain Demo
python3 llm_brain.py

# Run Parallel Learning
python3 run_v3.py

# Run Extreme Challenge
python3 extreme_challenge.py
```

## What's Included

| File | Purpose |
|------|---------|
| `llm_brain.py` | ⭐ **LLM External Brain** (16KB) |
| `run_v3.py` | Parallel agents launcher |
| `autonomous_learning_v3.py` | Core learning system |
| `extreme_challenge.py` | Stress test (K8s, Terraform, CI/CD) |

## LLM Brain Features

- Store code templates with confidence scores
- Query by task type or search keywords
- Track usage and success rates
- Add self-reflections
- Persist across sessions

## Performance Results

- **97-99% faster** after learning phase
- Stores 4-22 templates automatically
- Knowledge reused across iterations

## Learn More

See [SKILL.md](SKILL.md) for full documentation.
