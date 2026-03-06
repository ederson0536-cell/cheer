#!/usr/bin/env python3
import subprocess, sys, os
from pathlib import Path

WORKSPACE = Path("/home/david/.openclaw/workspace/skills/knowledge-graph-improved/v3")

print("""
╔══════════════════════════════════════════════════════════════════════╗
║     V3.0 AUTONOMOUS PARALLEL LEARNING SYSTEM          ║
║                                                          ║
║   6 Agents x 3 Iterations                               ║
║   Real Web Research via OpenClaw Browser                 ║
║   Code Template Storage                               ║
╚══════════════════════════════════════════════════════════════════════╝
""")

print("Checking browser...")
try:
    subprocess.run(["openclaw", "browser", "status", "--browser-profile", "openclaw"], capture_output=True, timeout=10)
    print("Browser ready!")
except: pass

print("\nStarting autonomous learning system...")
print("This will run 3 iterations with 6 parallel agents each.")
print("Estimated time: 15-25 minutes\n")

os.chdir(WORKSPACE)
result = subprocess.run([sys.executable, "scripts/autonomous_learning_v3.py"], capture_output=False)

print("\nDone!")
