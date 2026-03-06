#!/usr/bin/env python3
"""
🚀 LLM BRAIN HELPER - Quick Training & Query
=============================================
Easy-to-use wrapper for LLM Brain integration.

Usage:
    from brain_helper import brain, train, query

    # Query before coding
    code = query("flask login pattern")
    
    # Store after coding
    train("flask_login", my_code, "Flask login with sessions")
    
    # Record errors
    brain.record_error("ImportError", solution="pip install X")

Quick one-liners:
    python3 brain_helper.py "search query"
    python3 brain_helper.py --store flask_login "code here"
"""

import sys, os
from pathlib import Path

# Add to path
WORKSPACE = Path("/home/david/.openclaw/workspace/skills/knowledge-graph-improved")
sys.path.insert(0, str(WORKSPACE))

from llm_brain_v2 import LLMBrainV2

# Global brain instance
_brain = None

def get_brain():
    """Get or create brain instance."""
    global _brain
    if _brain is None:
        _brain = LLMBrainV2()
    return _brain

def query(search_term: str, limit: int = 5):
    """Quick search."""
    brain = get_brain()
    results = brain.search(search_term, limit=limit)
    for r in results:
        print(f"\n--- {r['task_type']} (score: {r['search_score']:.2f}) ---")
        print(f"Confidence: {r['confidence']}, Security: {r.get('security_score', 'N/A')}")
        print(f"Code:\n{r['content'][:500]}...")
    return results

def train(task_type: str, code: str, description: str = "", 
          tags: list = None, language: str = None):
    """Quick store."""
    brain = get_brain()
    result = brain.store(
        content=code,
        task_type=task_type,
        description=description,
        tags=tags,
        language=language
    )
    print(f"✅ Stored: {task_type}")
    print(f"   Security: {result['security_score']}, Quality: {result['quality_score']}")
    if result.get('security_issues'):
        print(f"   Issues: {result['security_issues']}")
    return result

def record_error(error_type: str, message: str = "", solution: str = ""):
    """Quick error record."""
    brain = get_brain()
    result = brain.record_error(error_type, message, solution)
    print(f"✅ Error recorded: {error_type}")
    if result['action'] == 'updated':
        print(f"   Occurrences: {result['occurrences']}")

def add_reflection(text: str, context: str = ""):
    """Quick reflection."""
    brain = get_brain()
    brain.add_reflection(text, context)
    print("✅ Reflection added")

def stats():
    """Show stats."""
    brain = get_brain()
    s = brain.get_stats()
    print(f"\n📊 LLM Brain Stats:")
    print(f"   Knowledge: {s['knowledge']['total']} items")
    print(f"   High Confidence: {s['knowledge']['high_confidence']}")
    print(f"   Projects: {s['projects']}")
    print(f"   Errors: {s['errors']['total']} (fixed: {s['errors']['fixed']})")
    print(f"   Reflections: {s['reflections']}")

def best(task_type: str = None):
    """Get best template."""
    brain = get_brain()
    result = brain.get_best(task_type)
    if result:
        print(f"\n⭐ Best: {result['task_type']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Success Rate: {result['success_rate']}")
        print(f"   Code:\n{result['content'][:400]}...")
    return result

def help():
    print("""
🚀 LLM BRAIN HELPER

Usage:
    python3 brain_helper.py <command> [args]

Commands:
    python3 brain_helper.py "search query"     Query templates
    python3 brain_helper.py --store type code Store template
    python3 brain_helper.py --error type msg  Record error
    python3 brain_helper.py --reflect text    Add reflection
    python3 brain_helper.py --stats           Show statistics
    python3 brain_helper.py --best [type]     Get best template
    python3 brain_helper.py --help             Show this help

Python API:
    from brain_helper import brain, train, query
    brain = get_brain()
    brain.store(...)
    brain.search(...)
    brain.query(...)

Examples:
    python3 brain_helper.py "flask login"
    python3 brain_helper.py --store flask_login "from flask import..." "Flask login"
    python3 brain_helper.py --error ImportError "No module named" "pip install X"
""")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        help()
    elif sys.argv[1] == "--store":
        if len(sys.argv) >= 4:
            train(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "")
        else:
            print("Usage: --store task_type code [description]")
    elif sys.argv[1] == "--error":
        if len(sys.argv) >= 3:
            record_error(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", sys.argv[4] if len(sys.argv) > 4 else "")
        else:
            print("Usage: --error type [message] [solution]")
    elif sys.argv[1] == "--reflect":
        if len(sys.argv) >= 2:
            add_reflection(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "--stats":
        stats()
    elif sys.argv[1] == "--best":
        best(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        query(" ".join(sys.argv[1:]))
