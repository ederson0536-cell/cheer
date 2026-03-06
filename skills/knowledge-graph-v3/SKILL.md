# 🧠 Knowledge Graph V3.0 for OpenClaw

**OpenClaw Skill** - Enhanced External Brain for LLM Code Generation

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)
[![Version](https://img.shields.io/badge/Version-3.0.0-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

---

## 📦 OpenClaw Skill

This is an **official OpenClaw skill** that gives the LLM an enhanced persistent external brain:

### ✨ V2.0 ENHANCED FEATURES

| Feature | Description | Impact |
|---------|-------------|--------|
| 🧠 **Semantic Search** | TF-IDF keyword search with scoring | ⭐⭐⭐⭐⭐ |
| 📁 **Project Memory** | Auto-save project structure & dependencies | ⭐⭐⭐⭐⭐ |
| 🐛 **Error Learning** | Record errors with solutions | ⭐⭐⭐⭐ |
| 🔒 **Security Scanner** | Auto-scan for hardcoded secrets, injection risks | ⭐⭐⭐⭐⭐ |
| ⭐ **Code Evaluation** | Success/failure tracking per template | ⭐⭐⭐⭐ |
| 🧪 **Auto-Tests** | Auto-generate tests for stored code | ⭐⭐⭐ |
| 🌍 **Language Profiles** | Best practices per language/framework | ⭐⭐⭐⭐ |
| 📊 **Quality Assessment** | Score code quality automatically | ⭐⭐⭐⭐ |
| 💭 **Reflections** | Self-learning insights | ⭐⭐⭐ |

## Installation

### Via ClawHub (Recommended)
```bash
clawhub install knowledge-graph-v3
```

### Manual Installation
```bash
git clone https://github.com/clowbot123-arch/knowledge-graph-v3.git
cd knowledge-graph-v3
```

## 🎯 For LLM: How to Use the Enhanced Brain

```python
from llm_brain_v2 import LLMBrainV2

brain = LLMBrainV2()

# 1. Store with FULL security scan & quality assessment
result = brain.store(
    content=my_code,
    task_type="flask_login",
    description="User authentication",
    tags=["flask", "auth", "python"],
    language="python",
    framework="flask",
    auto_scan=True  # Security + Quality scanning
)
print(f"Security: {result['security_score']}, Quality: {result['quality_score']}")

# 2. Semantic search (keyword + similarity scoring)
results = brain.search("authentication user login", limit=10)
for r in results:
    print(f"Score: {r['search_score']:.2f} - {r['task_type']}")

# 3. Query with filters
templates = brain.query(
    task_type="api",
    min_confidence=0.7,
    language="python",
    min_security=0.7
)

# 4. Get best template
best = brain.get_best(task_type="flask_login", min_security=0.8)

# 5. Save project structure (auto-detects files & deps)
proj = brain.save_project_structure(
    project_path="/path/to/project",
    name="my-project"
)
# Returns: {name, language, files: 42, dependencies: {"pip": ["flask", "requests"]}}

# 6. Record errors with solutions
brain.record_error(
    error_type="ImportError",
    error_message="No module named 'requests'",
    solution="pip install requests",
    code_context="import requests"
)

# 7. Find solution for an error
fix = brain.get_error_solution("ImportError", "No module named")
print(f"Solution: {fix['solution']}")

# 8. Get language best practices
py = brain.get_python_patterns()
print(f"Naming: {py['naming_convention']}")
print(f"Patterns: {py['patterns']}")

# 9. Record success/failure
brain.record_success(knowledge_id)
brain.record_failure(knowledge_id, error="timeout")

# 10. Add reflections
brain.add_reflection(
    "Vue Composition API is cleaner than Options API",
    context="vue_component"
)

# 11. Get comprehensive stats
stats = brain.get_stats()
# Returns: {knowledge, projects, errors, reflections, tests}
```

## 🚀 Running the Systems

### Enhanced Brain Demo
```bash
python3 llm_brain_v2.py
```
Shows all V2 features in action.

### Standard Learning Experiment
```bash
python3 run_v3.py
```
6 parallel agents learning simultaneously with web research.

### Extreme Challenge (Stress Test)
```bash
python3 extreme_challenge.py
```
E-Commerce Microservices Platform with K8s, Terraform, CI/CD.

## 📊 Results

| System | Before Learning | After Learning | Improvement |
|--------|----------------|----------------|-------------|
| V3.0 Parallel | ~24s/task | ~0.07s/task | **97-99% faster** |
| Extreme Challenge | 60s | 0.09s | **99.9% faster** |
| Knowledge Stored | 0 | 4-22 items | Automatic |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPENCLAW + LLM BRAIN V2.0                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🤖 LLM (You)                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • Store code with security/quality scanning           │  │
│   │  • Semantic search with scoring                        │  │
│   │  • Record errors and find solutions                   │  │
│   │  • Save project structures                             │  │
│   │  • Add reflections on best practices                   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   🧠 LLMBrainV2 (SQLite)                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  Tables:                                               │  │
│   │  • knowledge (templates, scores, metadata)             │  │
│   │  • projects (file structures, deps)                    │  │
│   │  • errors (with solutions)                             │  │
│   │  • language_profiles (best practices)                   │  │
│   │  • reflections (self-learning)                          │  │
│   │  • tests (auto-generated tests)                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   🔍 Semantic Search Engine                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • TF-IDF keyword extraction                           │  │
│   │  • Similarity scoring                                  │  │
│   │  • Boost by confidence & success rate                 │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   🔒 Security Scanner                                          │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • Hardcoded secrets detection                        │  │
│   │  • Injection risk detection                           │  │
│   │  • Code quality assessment                            │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Files

```
knowledge-graph-v3/
├── SKILL.md                    # This file
├── README.md                   # Quick reference
├── llm_brain_v2.py             # ⭐ ENHANCED Brain (35KB)
├── llm_brain.py                # Original V1 (16KB)
├── run_v3.py                   # Parallel agents launcher
├── autonomous_learning_v3.py    # Core learning system
├── extreme_challenge.py         # Stress test
├── data/
│   ├── llm_brain.db            # SQLite knowledge base (V2)
│   ├── llm_brain_v2.db         # SQLite knowledge base (V2)
│   └── templates_v2/          # Stored templates
└── results/                    # Experiment results
```

## 🔧 V2 API Reference

### LLMBrainV2 Methods

| Method | Description |
|--------|-------------|
| `store(content, task_type, ...)` | Store with security/quality scan |
| `search(query, limit)` | Semantic search with scoring |
| `query(task_type, filters)` | Query by type with filters |
| `get_best(task_type)` | Get highest quality template |
| `save_project_structure(path)` | Auto-save project structure |
| `get_project(path)` | Retrieve project memory |
| `record_error(type, message, solution)` | Record error with solution |
| `get_error_solution(type, message)` | Find solution for error |
| `record_success/failure(id)` | Track template performance |
| `get_python_patterns()` | Get Python best practices |
| `get_javascript_patterns()` | Get JS patterns |
| `add_reflection(text, context)` | Add self-learning |
| `get_stats()` | Comprehensive statistics |

## Requirements

- **OpenClaw** with browser capability
- Python 3.8+
- SQLite3
- Internet connection (for web research)

## Troubleshooting

### "Database locked"
```bash
rm -f data/llm_brain_v2.db
python3 llm_brain_v2.py  # Recreate with demo
```

### "Browser not found"
```bash
openclaw browser start --browser-profile openclaw
```

## License

MIT - See LICENSE file

## Author

Created for OpenClaw - The autonomous AI assistant

---

**Part of the OpenClaw ecosystem** 🦞

For more OpenClaw skills: https://clawhub.com
