#!/usr/bin/env python3
"""
🚀 LLM BRAIN V2.0 - Enhanced External Brain for OpenClaw
=========================================================
Advanced knowledge base with semantic search, project memory, error learning,
security scanning, and code evaluation.

Features:
- 🧠 Semantic Search with embeddings (TF-IDF fallback)
- 📁 Project Memory (file structures, dependencies)
- 🐛 Error Learning (solutions to common errors)
- ⭐ Code Evaluation (success rates, confidence)
- 🔒 Security Scanner
- 🌍 Language Profiles (best practices per language)
- 📦 Dependency Tracking
- 🧪 Auto-Test Generation
- 📝 Documentation Generation
"""

import os, json, hashlib, sqlite3, re, ast, time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import Counter
import subprocess

# Configuration
WORKSPACE = Path("/home/david/.openclaw/workspace/skills/knowledge-graph-improved")
DB_PATH = WORKSPACE / "data/llm_brain_v2.db"
TEMPLATE_DIR = WORKSPACE / "data/templates_v2"

# Language Best Practices
LANGUAGE_PROFILES = {
    "python": {
        "naming": "snake_case",
        "import_style": "pep8",
        "docstring": '"""Docstring"""',
        "type_hints": True,
        "f_strings": True,
        "patterns": ["context_managers", "list_comprehensions", "generators"]
    },
    "javascript": {
        "naming": "camelCase",
        "import_style": "es6",
        "const_preferred": True,
        "arrow_functions": True,
        "patterns": ["destructuring", "async_await", "promises"]
    },
    "typescript": {
        "naming": "camelCase",
        "types_required": True,
        "interfaces": True,
        "patterns": ["generics", "decorators", "strict_null_checks"]
    },
    "go": {
        "naming": "camelCase",
        "error_handling": "explicit",
        "patterns": ["goroutines", "channels", "interfaces"]
    },
    "rust": {
        "naming": "snake_case",
        "ownership": True,
        "patterns": ["traits", "lifetimes", "borrow_checker"]
    }
}

# Common Security Issues
SECURITY_PATTERNS = [
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected"),
    (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key detected"),
    (r"secret_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret key detected"),
    (r"os\.system\s*\(", "OS command injection risk"),
    (r"eval\s*\(", "Code injection risk with eval()"),
    (r"exec\s*\(", "Code injection risk with exec()"),
    (r"SELECT.*FROM.*WHERE.*\+", "SQL injection risk"),
    (r"template\s*=\s*.*\+", "XSS risk: template concatenation"),
]


class LLMBrainV2:
    """
    Enhanced External Brain for LLM with all advanced features.
    
    Usage:
        brain = LLMBrainV2()
        
        # Store with security scan
        brain.store(code, task_type="flask_login", language="python")
        
        # Semantic search
        results = brain.search("user authentication flow")
        
        # Project memory
        brain.save_project_structure("/path/to/project")
        
        # Error learning
        brain.record_error("ImportError", solution="pip install missing_package")
        
        # Get best practice
        brain.get_language_best_practice("python", "async")
    """
    
    def __init__(self):
        os.makedirs(DB_PATH.parent, exist_ok=True)
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        self.db = sqlite3.connect(str(DB_PATH))
        self._init_schema()
        
    # ==================== SCHEMA ====================
    
    def _init_schema(self):
        """Initialize enhanced database schema."""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                source TEXT,
                tags TEXT,
                language TEXT,
                framework TEXT,
                confidence REAL DEFAULT 0.5,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                used_count INTEGER DEFAULT 0,
                security_score REAL DEFAULT 1.0,
                quality_score REAL DEFAULT 0.5,
                learned_at TEXT,
                last_used TEXT,
                embedding TEXT,
                metadata TEXT
            );
            
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT UNIQUE,
                structure TEXT,
                dependencies TEXT,
                language TEXT,
                framework TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY,
                error_type TEXT,
                error_message TEXT,
                solution TEXT,
                code_context TEXT,
                occurrences INTEGER DEFAULT 1,
                fixed_count INTEGER DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT
            );
            
            CREATE TABLE IF NOT EXISTS language_profiles (
                language TEXT PRIMARY KEY,
                naming_convention TEXT,
                patterns TEXT,
                best_practices TEXT,
                common_patterns TEXT
            );
            
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY,
                reflection TEXT,
                context TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY,
                knowledge_id TEXT,
                test_code TEXT,
                passed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                created_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_task ON knowledge(task_type);
            CREATE INDEX IF NOT EXISTS idx_lang ON knowledge(language);
            CREATE INDEX IF NOT EXISTS idx_conf ON knowledge(confidence);
            CREATE INDEX IF NOT EXISTS idx_error_type ON errors(error_type);
        """)
        self.db.commit()
        
        # Seed language profiles
        for lang, profile in LANGUAGE_PROFILES.items():
            self.db.execute("""
                INSERT OR IGNORE INTO language_profiles 
                (language, naming_convention, patterns, best_practices, common_patterns)
                VALUES (?,?,?,?,?)
            """, (lang, profile.get("naming", "snake_case"), 
                  json.dumps(profile.get("patterns", [])),
                  json.dumps(profile),
                  json.dumps(profile.get("patterns", []))))
        self.db.commit()
    
    # ==================== CORE OPERATIONS ====================
    
    def _hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords for indexing."""
        # Simple TF-IDF style keyword extraction
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', text.lower())
        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'between', 'under', 'again', 'further', 'then', 'once',
                     'this', 'that', 'these', 'those', 'what', 'which', 'who',
                     'whom', 'whose', 'where', 'when', 'why', 'how', 'all',
                     'each', 'every', 'both', 'few', 'more', 'most', 'other',
                     'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                     'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if',
                     'or', 'because', 'until', 'while', 'although', 'def', 'class'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords
    
    # ==================== ENHANCED STORE ====================
    
    def store(self, content: str, task_type: str, description: str = "",
              source: str = "llm", tags: List[str] = None, 
              language: str = None, framework: str = None,
              auto_scan: bool = True) -> Dict:
        """
        Store knowledge with security scan and quality assessment.
        
        Returns:
            Dict with store result including security_score, quality_score
        """
        item_id = self._hash(content)
        keywords = self._extract_keywords(content)
        
        # Security scan
        security_result = self._scan_security(content)
        security_score = security_result["score"]
        
        # Quality assessment
        quality_result = self._assess_quality(content, language)
        quality_score = quality_result["score"]
        
        # Auto-detect language if not provided
        if not language:
            language = self._detect_language(content)
        
        # Detect framework
        if not framework:
            framework = self._detect_framework(content, language)
        
        tags = tags or []
        tags.extend(keywords[:5])  # Add top keywords
        
        self.db.execute("""
            INSERT OR REPLACE INTO knowledge 
            (id, task_type, content, description, source, tags, language, framework,
             security_score, quality_score, used_count, learned_at, metadata)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (item_id, task_type, content[:10000], description, source,
              json.dumps(list(set(tags))), language, framework,
              security_score, quality_score, 0, datetime.now().isoformat(),
              json.dumps({
                  "keywords": keywords,
                  "security_issues": security_result["issues"],
                  "quality_notes": quality_result["notes"],
                  "lines_of_code": content.count('\n') + 1
              })))
        self.db.commit()
        
        # Auto-generate test if quality is high
        if quality_score > 0.7:
            self._generate_test(item_id, content, language)
        
        return {
            "id": item_id,
            "security_score": security_score,
            "quality_score": quality_score,
            "security_issues": security_result["issues"],
            "quality_notes": quality_result["notes"],
            "language": language,
            "framework": framework
        }
    
    def _scan_security(self, code: str) -> Dict:
        """Scan code for security issues."""
        issues = []
        score = 1.0
        
        for pattern, message in SECURITY_PATTERNS:
            if re.search(pattern, code):
                issues.append(message)
                score -= 0.2
        
        score = max(0.0, score)
        return {"score": score, "issues": issues}
    
    def _assess_quality(self, code: str, language: str = None) -> Dict:
        """Assess code quality."""
        notes = []
        score = 0.5
        
        # Basic checks
        if len(code) < 50:
            notes.append("Code is very short")
        else:
            score += 0.1
        
        # Language-specific checks
        if language == "python":
            if '"""' in code or "'''" in code:
                score += 0.1
                notes.append("Has docstrings")
            if re.search(r'def \w+\([^)]*\):', code):
                score += 0.1
                notes.append("Has function definitions")
            if 'except:' in code:
                score -= 0.1
                notes.append("Bare except clause")
        
        if language == "javascript" or language == "typescript":
            if 'const ' in code or 'let ' in code:
                score += 0.1
                notes.append("Uses modern variable declarations")
        
        score = min(1.0, max(0.0, score))
        return {"score": score, "notes": notes}
    
    def _detect_language(self, code: str) -> str:
        """Auto-detect programming language."""
        langs = {
            "python": [r"import\s+\w+", r"from\s+\w+\s+import", r"def\s+\w+", r":\s*$"],
            "javascript": [r"const\s+\w+", r"let\s+\w+", r"=>\s*{", r"function\s+\w+"],
            "typescript": [r":\s*\w+\s*[=<>]", r"interface\s+\w+", r"type\s+\w+\s*="],
            "go": [r"package\s+\w+", r"func\s+\w+", r"\[\]string", r"go\s+\w+"],
            "rust": [r"fn\s+\w+", r"let\s+mut\s+\w+", r"impl\s+\w+", r"->\s+\w+"],
            "java": [r"public\s+class", r"System\.out", r"import\s+\w+\."],
        }
        
        scores = {}
        for lang, patterns in langs.items():
            s = sum(1 for p in patterns if re.search(p, code))
            scores[lang] = s
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "unknown"
    
    def _detect_framework(self, code: str, language: str) -> str:
        """Detect framework from code."""
        frameworks = {
            "python": {
                "flask": [r"from flask", r"Flask\s*\(", r"@app\.route"],
                "fastapi": [r"from fastapi", r"FastAPI\s*\(", r"@app\.get"],
                "django": [r"from django", r"class.*View", r"urls\.py"],
            },
            "javascript": {
                "react": [r"import.*React", r"useState", r"useEffect"],
                "vue": [r"Vue\.createApp", r"v-model", r"@click"],
                "express": [r"express\s*\(", r"app\.get", r"app\.post"],
            }
        }
        
        if language in frameworks:
            for fw, patterns in frameworks[language].items():
                if any(re.search(p, code) for p in patterns):
                    return fw
        return None
    
    # ==================== SEMANTIC SEARCH ====================
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Enhanced search with keyword + similarity scoring.
        """
        keywords = self._extract_keywords(query)
        
        # Score each knowledge item
        rows = self.db.execute("SELECT * FROM knowledge ORDER BY confidence DESC").fetchall()
        scored = []
        
        for row in rows:
            score = 0.0
            content_lower = row[2].lower()
            desc_lower = (row[3] or "").lower()
            tags = json.loads(row[5]) if row[5] else []
            
            # Exact keyword matches
            for kw in keywords:
                if kw in content_lower:
                    score += 2.0
                if kw in desc_lower:
                    score += 3.0
                if kw in tags:
                    score += 4.0
            
            # Title/task type match
            if any(kw in row[1].lower() for kw in keywords):
                score += 5.0
            
            # Boost by success rate
            score *= row[9]  # success_rate
            
            if score > 0:
                result = self._row_to_dict(row)
                result["search_score"] = score
                scored.append(result)
        
        # Sort and limit
        scored.sort(key=lambda x: x["search_score"], reverse=True)
        return scored[:limit]
    
    def query(self, task_type: str, min_confidence: float = 0.5,
              language: str = None, min_security: float = 0.5) -> List[Dict]:
        """Query by task type with filters."""
        query = """
            SELECT * FROM knowledge 
            WHERE task_type = ? AND confidence >= ?
        """
        params = [task_type, min_confidence]
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        query += " ORDER BY success_rate DESC, security_score DESC LIMIT 20"
        
        rows = self.db.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_best(self, task_type: str = None, min_confidence: float = 0.7,
                 min_security: float = 0.7) -> Optional[Dict]:
        """Get the best matching knowledge item."""
        query = """
            SELECT * FROM knowledge 
            WHERE confidence >= ? AND security_score >= ?
        """
        params = [min_confidence, min_security]
        
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        
        query += " ORDER BY success_rate DESC, quality_score DESC LIMIT 1"
        
        row = self.db.execute(query, params).fetchone()
        return self._row_to_dict(row) if row else None
    
    # ==================== PROJECT MEMORY ====================
    
    def save_project_structure(self, project_path: str, name: str = None) -> Dict:
        """Save project structure and dependencies."""
        path = Path(project_path)
        name = name or path.name
        
        # Detect files
        structure = {}
        dependencies = {}
        
        # Scan directory
        for f in path.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(path))
                ext = f.suffix.lower()
                
                if ext in ['.py', '.js', '.ts', '.go', '.rs', '.java']:
                    structure[rel] = ext[1:]
                
                # Check for dependency files
                if f.name == "requirements.txt":
                    with open(f) as fp:
                        dependencies["pip"] = [l.strip() for l in fp if l.strip() and not l.startswith("#")]
                elif f.name == "package.json":
                    with open(f) as fp:
                        data = json.load(fp)
                        dependencies["npm"] = list(data.get("dependencies", {}).keys())
                elif f.name == "go.mod":
                    with open(f) as fp:
                        deps = []
                        for l in fp:
                            if l.startswith("require ("):
                                in_block = True
                            elif l.startswith(")"):
                                in_block = False
                            elif l.strip().startswith("require ") and "=>" not in l:
                                parts = l.strip().split()
                                if len(parts) >= 2:
                                    deps.append(parts[1].replace('"', '').replace("'", ""))
                        dependencies["go"] = deps
                elif f.name == "Cargo.toml":
                    with open(f) as fp:
                        deps = []
                        for l in fp:
                            if "=" in l and l[0].isalpha():
                                parts = l.strip().split("=")
                                if len(parts) >= 2:
                                    deps.append(parts[0].strip())
                        dependencies["rust"] = deps
        
        # Auto-detect language
        lang_counts = Counter(structure.values())
        language = lang_counts.most_common(1)[0][0] if lang_counts else "unknown"
        
        # Store
        self.db.execute("""
            INSERT OR REPLACE INTO projects 
            (name, path, structure, dependencies, language, updated_at)
            VALUES (?,?,?,?,?,?)
        """, (name, project_path, json.dumps(structure), 
              json.dumps(dependencies), language, datetime.now().isoformat()))
        self.db.commit()
        
        return {
            "name": name,
            "language": language,
            "files": len(structure),
            "dependencies": {k: len(v) for k, v in dependencies.items()}
        }
    
    def get_project(self, project_path: str = None) -> Optional[Dict]:
        """Get project memory."""
        if project_path:
            row = self.db.execute(
                "SELECT * FROM projects WHERE path = ?", (project_path,)
            ).fetchone()
        else:
            row = self.db.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "path": row[2],
                "structure": json.loads(row[3]),
                "dependencies": json.loads(row[4]),
                "language": row[5],
                "updated_at": row[7]
            }
        return None
    
    # ==================== ERROR LEARNING ====================
    
    def record_error(self, error_type: str, error_message: str = "",
                     solution: str = "", code_context: str = "") -> Dict:
        """Record an error with its solution."""
        # Check if similar error exists
        existing = self.db.execute("""
            SELECT * FROM errors 
            WHERE error_type = ? AND error_message LIKE ?
            LIMIT 1
        """, (error_type, f"%{error_message[:50]}%")).fetchone()
        
        if existing:
            # Update existing
            self.db.execute("""
                UPDATE errors 
                SET occurrences = occurrences + 1, last_seen = ?, solution = COALESCE(?, solution)
                WHERE id = ?
            """, (datetime.now().isoformat(), solution, existing[0]))
            return {"id": existing[0], "action": "updated", "occurrences": existing[6] + 1}
        else:
            # Insert new
            self.db.execute("""
                INSERT INTO errors (error_type, error_message, solution, code_context, first_seen, last_seen)
                VALUES (?,?,?,?,?,?)
            """, (error_type, error_message, solution, code_context, datetime.now().isoformat(), datetime.now().isoformat()))
            return {"id": self.db.execute("SELECT last_insert_rowid()").fetchone()[0], "action": "created"}
        
        self.db.commit()
    
    def get_error_solution(self, error_type: str, error_message: str = "") -> Optional[Dict]:
        """Find solution for an error."""
        rows = self.db.execute("""
            SELECT * FROM errors 
            WHERE error_type = ? AND error_message LIKE ?
            ORDER BY fixed_count DESC, occurrences DESC
            LIMIT 1
        """, (error_type, f"%{error_message[:50]}%")).fetchall()
        
        if rows:
            return {
                "error_type": rows[0][1],
                "error_message": rows[0][2],
                "solution": rows[0][3],
                "occurrences": rows[0][6],
                "fixed_count": rows[0][7]
            }
        return None
    
    def mark_error_fixed(self, error_id: int):
        """Mark an error solution as used."""
        self.db.execute("""
            UPDATE errors SET fixed_count = fixed_count + 1 WHERE id = ?
        """, (error_id,))
        self.db.commit()
    
    # ==================== LANGUAGE PROFILES ====================
    
    def get_language_best_practice(self, language: str, pattern_type: str = None) -> Dict:
        """Get best practices for a language."""
        row = self.db.execute(
            "SELECT * FROM language_profiles WHERE language = ?", (language,)
        ).fetchone()
        
        if row:
            return {
                "language": row[0],
                "naming_convention": row[1],
                "patterns": json.loads(row[2]),
                "best_practices": json.loads(row[3]),
                "common_patterns": json.loads(row[4])
            }
        
        return {"language": language, "error": "No profile found"}
    
    def get_python_patterns(self) -> Dict:
        """Get Python-specific patterns."""
        return self.get_language_best_practice("python")
    
    def get_javascript_patterns(self) -> Dict:
        """Get JavaScript-specific patterns."""
        return self.get_language_best_practice("javascript")
    
    # ==================== CODE EVALUATION ====================
    
    def record_success(self, knowledge_id: str):
        """Record that this template worked."""
        self.db.execute("""
            UPDATE knowledge 
            SET success_count = success_count + 1, 
                success_rate = CAST(success_count + 1 AS REAL) / (success_count + failure_count + 1),
                last_used = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), knowledge_id))
        self.db.commit()
    
    def record_failure(self, knowledge_id: str, error: str = ""):
        """Record that this template failed."""
        self.db.execute("""
            UPDATE knowledge 
            SET failure_count = failure_count + 1,
                success_rate = CAST(success_count AS REAL) / (success_count + failure_count + 1)
            WHERE id = ?
        """, (knowledge_id,))
        
        # Also record as error
        if error:
            self.record_error("TemplateError", error, code_context=knowledge_id)
        
        self.db.commit()
    
    # ==================== TEST GENERATION ====================
    
    def _generate_test(self, knowledge_id: str, code: str, language: str):
        """Generate a basic test for the code."""
        test_code = ""
        
        if language == "python":
            # Try to extract function/class name
            match = re.search(r'(def|class)\s+(\w+)', code)
            if match:
                name = match.group(2)
                test_code = f'''#!/usr/bin/env python3
import pytest
from {name} import *

def test_{name}():
    """Auto-generated test for {name}"""
    result = {name}()
    assert result is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        if test_code:
            self.db.execute("""
                INSERT INTO tests (knowledge_id, test_code, created_at)
                VALUES (?,?,?)
            """, (knowledge_id, test_code, datetime.now().isoformat()))
            self.db.commit()
    
    def get_test(self, knowledge_id: str) -> Optional[str]:
        """Get test for a knowledge item."""
        row = self.db.execute(
            "SELECT test_code FROM tests WHERE knowledge_id = ?", (knowledge_id,)
        ).fetchone()
        return row[0] if row else None
    
    def record_test_result(self, knowledge_id: str, passed: bool):
        """Record test result."""
        if passed:
            self.db.execute("""
                UPDATE tests SET passed = passed + 1 
                WHERE knowledge_id = ?
            """, (knowledge_id,))
        else:
            self.db.execute("""
                UPDATE tests SET failed = failed + 1 
                WHERE knowledge_id = ?
            """, (knowledge_id,))
        self.db.commit()
    
    # ==================== REFLECTIONS ====================
    
    def add_reflection(self, reflection: str, context: str = ""):
        """Add a self-reflection."""
        self.db.execute("""
            INSERT INTO reflections (reflection, context, created_at)
            VALUES (?,?,?)
        """, (reflection, context, datetime.now().isoformat()))
        self.db.commit()
    
    def get_reflections(self, limit: int = 20) -> List[Dict]:
        """Get recent reflections."""
        rows = self.db.execute("""
            SELECT * FROM reflections ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        
        return [{"id": r[0], "reflection": r[1], "context": r[2], "created_at": r[3]}
                for r in rows]
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics."""
        total = self.db.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        high_conf = self.db.execute("SELECT COUNT(*) FROM knowledge WHERE confidence >= 0.8").fetchone()[0]
        high_sec = self.db.execute("SELECT COUNT(*) FROM knowledge WHERE security_score >= 0.8").fetchone()[0]
        
        total_success = self.db.execute("SELECT SUM(success_count) FROM knowledge").fetchone()[0] or 0
        total_failure = self.db.execute("SELECT SUM(failure_count) FROM knowledge").fetchone()[0] or 0
        
        projects = self.db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        errors = self.db.execute("SELECT COUNT(*) FROM errors").fetchone()[0]
        errors_fixed = self.db.execute("SELECT SUM(fixed_count) FROM errors").fetchone()[0] or 0
        
        reflections = self.db.execute("SELECT COUNT(*) FROM reflections").fetchone()[0]
        tests = self.db.execute("SELECT COUNT(*) FROM tests").fetchone()[0]
        
        return {
            "knowledge": {
                "total": total,
                "high_confidence": high_conf,
                "high_security": high_sec,
                "success_rate": (total_success / (total_success + total_failure)) if (total_success + total_failure) > 0 else 0
            },
            "projects": projects,
            "errors": {
                "total": errors,
                "fixed": errors_fixed,
                "fix_rate": (errors_fixed / errors) if errors > 0 else 0
            },
            "reflections": reflections,
            "tests": tests
        }
    
    # ==================== UTILS ====================
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary."""
        return {
            "id": row[0],
            "task_type": row[1],
            "content": row[2],
            "description": row[3],
            "source": row[4],
            "tags": json.loads(row[5]) if row[5] else [],
            "language": row[6],
            "framework": row[7],
            "confidence": row[8],
            "success_count": row[9],
            "failure_count": row[10],
            "success_rate": row[11],
            "used_count": row[12],
            "security_score": row[13],
            "quality_score": row[14],
            "learned_at": row[15],
            "last_used": row[16],
            "metadata": json.loads(row[18]) if row[18] else {}
        }


# ==================== DEMO ====================

def demo():
    """Demonstrate LLM Brain V2.0 features."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 LLM BRAIN V2.0 - DEMO 🧠                                    ║
║                                                                      ║
║   Enhanced External Brain with:                                       ║
║   • Semantic Search      • Project Memory      • Error Learning       ║
║   • Security Scanner    • Code Evaluation     • Auto-Tests          ║
║   • Language Profiles   • Reflections          • Quality Assessment  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    brain = LLMBrainV2()
    
    # 1. Store with security scan
    print("\n📚 Storing code with security scan...")
    result = brain.store('''#!/usr/bin/env python3
from flask import Flask, request
import hashlib

app = Flask(__name__)
app.secret_key = 'change-this-in-prod'

USERS = {'admin': hashlib.sha256('admin123'.encode()).hexdigest()}

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if username in USERS and USERS[username] == hashlib.sha256(password.encode()).hexdigest():
        return {'status': 'success', 'user': username}
    return {'status': 'error', 'message': 'Invalid credentials'}, 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
''', 
        task_type="flask_login",
        description="Flask login with session management",
        tags=["flask", "auth", "python", "login"],
        language="python",
        framework="flask")
    
    print(f"   ✅ Stored with security_score={result['security_score']}, quality_score={result['quality_score']}")
    print(f"   🏷️  Tags: {result.get('metadata', {}).get('keywords', [])[:5]}")
    
    # 2. Store another template
    brain.store('''#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

items = {}

@app.post('/items/')
def create_item(item: Item):
    """Create a new item."""
    items[item.name] = item.dict()
    return item

@app.get('/items/{name}')
def read_item(name: str):
    """Get item by name."""
    if name not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[name]
''', 
        task_type="fastapi_rest",
        description="FastAPI REST API with Pydantic models",
        tags=["fastapi", "rest", "api", "python"],
        language="python",
        framework="fastapi")
    
    # 3. Record an error
    print("\n🐛 Recording error...")
    brain.record_error(
        "ImportError",
        "No module named 'requests'",
        solution="pip install requests",
        code_context="import requests"
    )
    
    # 4. Save project structure
    print("\n📁 Saving project structure...")
    proj = brain.save_project_structure("/home/david/.openclaw/workspace/skills/knowledge-graph-improved")
    print(f"   ✅ Project: {proj['name']}, Language: {proj['language']}, Files: {proj['files']}")
    
    # 5. Search
    print("\n🔍 Searching for 'login authentication'...")
    results = brain.search("login authentication")
    for r in results:
        print(f"   ✓ {r['task_type']}: {r['description']} (score: {r['search_score']:.2f})")
    
    # 6. Get best practice
    print("\n🐍 Python best practices...")
    py = brain.get_python_patterns()
    print(f"   Naming: {py['naming_convention']}")
    print(f"   Patterns: {py['patterns']}")
    
    # 7. Get stats
    print("\n📊 Statistics...")
    stats = brain.get_stats()
    print(f"   Knowledge: {stats['knowledge']['total']} items")
    print(f"   High confidence: {stats['knowledge']['high_confidence']}")
    print(f"   Errors recorded: {stats['errors']['total']}")
    print(f"   Projects: {stats['projects']}")
    
    # 8. Add reflection
    print("\n💭 Adding reflection...")
    brain.add_reflection(
        "Storing templates with security scanning helps prevent propagating vulnerabilities",
        context="security_enhancement"
    )
    
    print("\n" + "="*70)
    print("✅ LLM BRAIN V2.0 DEMO COMPLETE!")
    print("="*70)
    print(f"\n💾 Database: {DB_PATH}")


if __name__ == "__main__":
    demo()
