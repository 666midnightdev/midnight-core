import unittest
import os
from memory.db import SQLiteMemoryBackend
from memory.vector import VectorDatabase
from providers.ollama import OllamaProvider

class TestMemory(unittest.TestCase):
    def setUp(self):
        # Use a temporary file path for tests
        self.db_path = "test_midnight.db"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass
        self.db = SQLiteMemoryBackend(self.db_path)

    def tearDown(self):
        # Clean up temporary database
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_conversation_saving_and_loading(self):
        session_id = "test_sess"
        self.db.save_message(session_id, "user", "Testing memory prompt")
        self.db.save_message(session_id, "assistant", "Testing response")
        
        msgs = self.db.get_messages(session_id)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["content"], "Testing memory prompt")
        self.assertEqual(msgs[1]["role"], "assistant")

    def test_execution_history_logging(self):
        self.db.save_execution("task_123", "nmap -sV target", "Host is up", 0, 1.25)
        executions = self.db.get_executions(limit=10)
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["command"], "nmap -sV target")
        self.assertEqual(executions[0]["exit_code"], 0)

    def test_cosine_similarity(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        sim_identical = VectorDatabase._cosine_similarity(v1, v2)
        self.assertAlmostEqual(sim_identical, 1.0)
        
        v3 = [0.0, 1.0, 0.0]
        sim_orthogonal = VectorDatabase._cosine_similarity(v1, v3)
        self.assertAlmostEqual(sim_orthogonal, 0.0)

if __name__ == "__main__":
    unittest.main()
