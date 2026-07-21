import sqlite3
import json
from typing import Any, Dict, List, Optional, Tuple
from config.settings import settings
from core_logging.logger import logger

class SQLiteMemoryBackend:
    """Manages raw SQLite database interactions for Midnight Core memory."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.storage.db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables for conversation, tasks, executions, vector index, and reports."""
        logger.info(f"Initializing SQLite database at: {self.db_path}")
        with self._get_connection() as conn:
            # Conversations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Executions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    command TEXT NOT NULL,
                    output TEXT,
                    exit_code INTEGER,
                    duration_sec REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tasks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    plan TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Vector metadata / embedding chunks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vector TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reports
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    risk_score TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        logger.info("SQLite database tables initialized successfully.")
        
    # Conversations API
    def save_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO conversation (session_id, role, content, tool_calls) VALUES (?, ?, ?, ?)",
                (session_id, role, content, json.dumps(tool_calls) if tool_calls else None)
            )
            conn.commit()
            
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT role, content, tool_calls, timestamp FROM conversation WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                msg = {
                    "role": row["role"],
                    "content": row["content"]
                }
                if row["tool_calls"]:
                    try:
                        msg["tool_calls"] = json.loads(row["tool_calls"])
                    except Exception:
                        pass
                messages.append(msg)
            return messages

    # Executions API
    def save_execution(self, task_id: str, command: str, output: str, exit_code: int, duration_sec: float) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO execution_history (task_id, command, output, exit_code, duration_sec) VALUES (?, ?, ?, ?, ?)",
                (task_id, command, output, exit_code, duration_sec)
            )
            conn.commit()

    def get_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, task_id, command, output, exit_code, duration_sec, timestamp FROM execution_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # Vector store API
    def save_vector(self, vector: List[float], content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO vector_store (vector, content, metadata) VALUES (?, ?, ?)",
                (json.dumps(vector), content, json.dumps(metadata) if metadata else None)
            )
            conn.commit()

    def get_all_vectors(self) -> List[Tuple[int, List[float], str, Dict[str, Any]]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT id, vector, content, metadata FROM vector_store")
            rows = cursor.fetchall()
            results = []
            for row in rows:
                try:
                    vector = json.loads(row["vector"])
                    meta = json.loads(row["metadata"]) if row["metadata"] else {}
                    results.append((row["id"], vector, row["content"], meta))
                except Exception as e:
                    logger.error(f"Error parsing row {row['id']} from vector_store: {e}")
            return results

    # Reports API
    def save_report(self, title: str, filepath: str, risk_score: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO reports (title, filepath, risk_score) VALUES (?, ?, ?)",
                (title, filepath, risk_score)
            )
            conn.commit()

    def get_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT id, title, filepath, risk_score, created_at FROM reports ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # Tasks API
    def save_task(self, task_id: str, title: str, status: str, plan: Optional[Dict[str, Any]] = None) -> None:
        with self._get_connection() as conn:
            plan_str = json.dumps(plan) if plan else None
            conn.execute(
                "INSERT OR REPLACE INTO tasks (task_id, title, status, plan, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (task_id, title, status, plan_str)
            )
            conn.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT task_id, title, status, plan, created_at, updated_at FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                task = dict(row)
                if task["plan"]:
                    task["plan"] = json.loads(task["plan"])
                return task
            return None

    def get_all_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT task_id, title, status, plan, created_at, updated_at FROM tasks ORDER BY updated_at DESC LIMIT ?", (limit,))
            results = []
            for row in cursor.fetchall():
                task = dict(row)
                if task["plan"]:
                    try:
                        task["plan"] = json.loads(task["plan"])
                    except Exception:
                        pass
                results.append(task)
            return results
