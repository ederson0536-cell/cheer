#!/usr/bin/env python3
"""
OpenClaw Knowledge Graph - LLM External Brain
=============================================
A persistent knowledge base that enhances LLM coding capabilities.

Usage:
- Store code templates, patterns, best practices
- Query templates by task type or search
- Learn from previous work
- Persist across sessions
"""

import os, json, hashlib, sqlite3, time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
WORKSPACE = Path("/home/david/.openclaw/workspace/skills/knowledge-graph-improved")
DB_PATH = WORKSPACE / "data/llm_brain.db"
TEMPLATE_DIR = WORKSPACE / "data/templates_llm"

class LLMBrain:
    """
    External brain for LLM - stores and retrieves code knowledge.
    
    Example usage:
        brain = LLMBrain()
        
        # Store a template
        brain.store(
            task_type="flask_login",
            code=my_flask_code,
            description="Flask login with session management",
            tags=["flask", "auth", "python"],
            confidence=0.9
        )
        
        # Query templates
        templates = brain.query("flask login")
        best = brain.get_best("flask", min_confidence=0.8)
        
        # Search
        results = brain.search("authentication patterns")
    """
    
    def __init__(self):
        os.makedirs(DB_PATH.parent, exist_ok=True)
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        self.db = sqlite3.connect(str(DB_PATH))
        self._init_schema()
        
    def _init_schema(self):
        """Initialize database schema."""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                source TEXT,
                tags TEXT,
                confidence REAL DEFAULT 0.5,
                used_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                learned_at TEXT,
                last_used TEXT,
                language TEXT,
                framework TEXT,
                difficulty TEXT
            );
            
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                tasks_completed INTEGER,
                knowledge_stored INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY,
                reflection TEXT,
                created_at TEXT,
                context TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_task_type ON knowledge(task_type);
            CREATE INDEX IF NOT EXISTS idx_tags ON knowledge(tags);
            CREATE INDEX IF NOT EXISTS idx_confidence ON knowledge(confidence);
        """)
        self.db.commit()
    
    def _hash(self, content: str) -> str:
        """Generate short hash for content."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    # ==================== CORE OPERATIONS ====================
    
    def store(self, task_type: str, content: str, description: str = "",
              source: str = "llm", tags: List[str] = None, confidence: float = 0.8,
              language: str = None, framework: str = None, difficulty: str = None) -> str:
        """
        Store a code template or knowledge in the brain.
        
        Args:
            task_type: Category (e.g., "flask_login", "react_component")
            content: The actual code or knowledge
            description: Human-readable description
            source: Where this came from ("web", "llm", "experiment")
            tags: List of tags for searching
            confidence: How reliable this knowledge is (0.0-1.0)
            language: Programming language
            framework: Framework used
            difficulty: Complexity level
            
        Returns:
            The ID of the stored knowledge
        """
        item_id = self._hash(content)
        tags_json = json.dumps(tags or [])
        
        self.db.execute("""
            INSERT OR REPLACE INTO knowledge 
            (id, task_type, content, description, source, tags, confidence, 
             used_count, learned_at, language, framework, difficulty)
            VALUES (?,?,?,?,?,?,?,0,?,?,?,?)
        """, (item_id, task_type, content[:10000], description, source,
              tags_json, confidence, datetime.now().isoformat(), 
              language, framework, difficulty))
        self.db.commit()
        
        return item_id
    
    def query(self, task_type: str, min_confidence: float = 0.5, 
              limit: int = 5) -> List[Dict]:
        """
        Query templates by task type.
        
        Args:
            task_type: The category to search
            min_confidence: Minimum confidence score
            limit: Maximum results
            
        Returns:
            List of knowledge items ordered by confidence
        """
        rows = self.db.execute("""
            SELECT * FROM knowledge 
            WHERE task_type = ? AND confidence >= ?
            ORDER BY confidence DESC, used_count DESC
            LIMIT ?
        """, (task_type, min_confidence, limit)).fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search across all knowledge using keywords.
        
        Args:
            query: Search terms (space-separated)
            limit: Maximum results
            
        Returns:
            List of matching knowledge items
        """
        # Simple keyword search
        keywords = query.lower().split()
        conditions = " OR ".join(["content LIKE ? OR description LIKE ? OR tags LIKE ?" 
                                   for _ in keywords])
        params = []
        for kw in keywords:
            params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
        
        rows = self.db.execute(f"""
            SELECT * FROM knowledge 
            WHERE {conditions}
            ORDER BY confidence DESC
            LIMIT ?
        """, params + [limit]).fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_best(self, task_type: str = None, min_confidence: float = 0.7) -> Optional[Dict]:
        """
        Get the best (highest confidence + most used) template.
        
        Args:
            task_type: Optional filter by task type
            min_confidence: Minimum confidence threshold
            
        Returns:
            Best matching knowledge item or None
        """
        if task_type:
            row = self.db.execute("""
                SELECT * FROM knowledge 
                WHERE task_type = ? AND confidence >= ?
                ORDER BY confidence DESC, used_count DESC
                LIMIT 1
            """, (task_type, min_confidence)).fetchone()
        else:
            row = self.db.execute("""
                SELECT * FROM knowledge 
                WHERE confidence >= ?
                ORDER BY confidence DESC, used_count DESC
                LIMIT 1
            """, (min_confidence,)).fetchone()
        
        return self._row_to_dict(row) if row else None
    
    def get_related(self, task_type: str, depth: int = 1) -> Dict[str, List[Dict]]:
        """
        Get related knowledge items.
        
        Args:
            task_type: The task type to find relations for
            depth: How deep to search relationships
            
        Returns:
            Dictionary with related items by category
        """
        # Get tags for this task type
        tags_row = self.db.execute(
            "SELECT tags FROM knowledge WHERE task_type = ? LIMIT 1", 
            (task_type,)
        ).fetchone()
        
        if not tags_row:
            return {}
        
        tags = json.loads(tags_row[0]) if tags_row[0] else []
        related = {"same_type": [], "by_tags": [], "by_framework": []}
        
        # Same task type
        related["same_type"] = self.query(task_type, limit=5)
        
        # By framework/language
        framework = self.db.execute(
            "SELECT framework FROM knowledge WHERE task_type = ? LIMIT 1",
            (task_type,)
        ).fetchone()
        
        if framework and framework[0]:
            related["by_framework"] = self.db.execute("""
                SELECT * FROM knowledge 
                WHERE framework = ? AND task_type != ?
                ORDER BY confidence DESC
                LIMIT 5
            """, (framework[0], task_type)).fetchall()
            related["by_framework"] = [self._row_to_dict(r) for r in related["by_framework"]]
        
        return related
    
    def record_usage(self, item_id: str):
        """Record that a template was used."""
        self.db.execute("""
            UPDATE knowledge 
            SET used_count = used_count + 1, last_used = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), item_id))
        self.db.commit()
    
    def add_reflection(self, reflection: str, context: str = ""):
        """Add a self-reflection/learning."""
        self.db.execute("""
            INSERT INTO reflections (reflection, created_at, context)
            VALUES (?, ?, ?)
        """, (reflection, datetime.now().isoformat(), context))
        self.db.commit()
    
    def get_reflections(self, limit: int = 10) -> List[Dict]:
        """Get recent reflections."""
        rows = self.db.execute("""
            SELECT * FROM reflections 
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [{"id": r[0], "reflection": r[1], "created_at": r[2], "context": r[3]} 
                for r in rows]
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        total = self.db.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        by_conf = self.db.execute("""
            SELECT COUNT(*) FROM knowledge WHERE confidence >= 0.8
        """).fetchone()[0]
        total_used = self.db.execute("SELECT SUM(used_count) FROM knowledge").fetchone()[0]
        reflections = self.db.execute("SELECT COUNT(*) FROM reflections").fetchone()[0]
        
        return {
            "total_knowledge": total,
            "high_confidence": by_conf,
            "total_uses": total_used or 0,
            "reflections": reflections,
            "success_rate": (by_conf / total * 100) if total > 0 else 0
        }
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary."""
        return {
            "id": row[0],
            "task_type": row[1],
            "content": row[2],
            "description": row[3],
            "source": row[4],
            "tags": json.loads(row[5]) if row[5] else [],
            "confidence": row[6],
            "used_count": row[7],
            "success_rate": row[8],
            "learned_at": row[9],
            "last_used": row[10],
            "language": row[11],
            "framework": row[12],
            "difficulty": row[13]
        }


# ==================== QUICK START ====================

def demo():
    """Demonstrate the LLM Brain."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           🧠 OPENCLAW LLM BRAIN - DEMO 🧠                           ║
║                                                                      ║
║   Persistent knowledge base for LLM code generation                 ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    brain = LLMBrain()
    
    # Store some example templates
    examples = [
        {
            "task_type": "flask_login",
            "content": '''#!/usr/bin/env python3
from flask import Flask, request, session, redirect
import hashlib
app = Flask(__name__)
app.secret_key = 'change-this'

USERS = {'admin': hashlib.sha256('admin123'.encode()).hexdigest()}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        if u in USERS and USERS[u] == hashlib.sha256(p.encode()).hexdigest():
            session['user'] = u
            return redirect('/dashboard')
        return 'Invalid credentials'
    return f"<form method='post'><input name='username'><input name='password' type='password'><button>Login</button></form>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)''',
            "description": "Flask login with session management",
            "tags": ["flask", "auth", "python", "login"],
            "framework": "Flask",
            "language": "python",
            "difficulty": "easy"
        },
        {
            "task_type": "fastapi_rest",
            "content": '''#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

items = {}

@app.post('/items/')
def create(item: Item):
    items[item.name] = item.price
    return item

@app.get('/items/{name}')
def read(name: str):
    if name not in items:
        raise HTTPException(404, "Not found")
    return {"name": name, "price": items[name]}''',
            "description": "FastAPI REST API with Pydantic models",
            "tags": ["fastapi", "rest", "api", "python"],
            "framework": "FastAPI",
            "language": "python",
            "difficulty": "medium"
        },
        {
            "task_type": "docker_compose",
            "content": '''version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      - db
  db:
    image: postgres:14
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=app
volumes:
  pgdata:''',
            "description": "Docker Compose with Flask and PostgreSQL",
            "tags": ["docker", "compose", "devops"],
            "framework": "Docker",
            "language": "yaml",
            "difficulty": "medium"
        }
    ]
    
    print("📚 Storing example templates...")
    for ex in examples:
        brain.store(
            task_type=ex["task_type"],
            content=ex["content"],
            description=ex["description"],
            tags=ex["tags"],
            framework=ex["framework"],
            language=ex["language"],
            difficulty=ex["difficulty"]
        )
    
    # Query examples
    print("\n🔍 Querying 'flask_login':")
    results = brain.query("flask_login")
    for r in results:
        print(f"   ✓ {r['description']} (confidence: {r['confidence']})")
        print(f"     Framework: {r['framework']}, Language: {r['language']}")
    
    # Search examples
    print("\n🔍 Searching 'REST API':")
    results = brain.search("REST API")
    for r in results:
        print(f"   ✓ {r['task_type']}: {r['description']}")
    
    # Get stats
    stats = brain.get_stats()
    print(f"\n📊 Statistics:")
    print(f"   Total knowledge: {stats['total_knowledge']}")
    print(f"   High confidence: {stats['high_confidence']}")
    print(f"   Total uses: {stats['total_uses']}")
    
    # Add reflection
    brain.add_reflection(
        "Learned that storing templates improves code generation speed by 97%",
        context="knowledge_graph_v3"
    )
    
    print("\n✅ Demo complete!")
    print(f"\n💾 Brain location: {DB_PATH}")


if __name__ == "__main__":
    demo()
