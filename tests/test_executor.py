import unittest
from unittest.mock import patch, MagicMock
from executor.local import LocalExecutor
from executor.wsl import WSLExecutor
from executor.permissions import permission_controller

class TestExecutor(unittest.TestCase):
    def setUp(self):
        # Configure permission controller to auto-approve during test
        permission_controller.register_approval_callback(lambda x: True)

    def test_local_executor_success(self):
        exec_layer = LocalExecutor()
        # Ping localhost or run whoami (very cross platform or standard)
        res = exec_layer.execute("whoami" if unittest.TestCase == unittest.TestCase else "echo test_run")
        self.assertIn("exit_code", res)
        # Should not crash and return result
        self.assertIsNotNone(res["stdout"])

    def test_local_executor_permission_denied(self):
        from config.settings import settings
        old_level = settings.executor.auto_approve_level
        settings.executor.auto_approve_level = "none"
        try:
            # Set callback to reject everything
            permission_controller.register_approval_callback(lambda x: False)
            exec_layer = LocalExecutor()
            res = exec_layer.execute("whoami")
            self.assertEqual(res["exit_code"], -1)
            self.assertIn("Permission denied", res["stderr"])
        finally:
            settings.executor.auto_approve_level = old_level

    @patch("subprocess.run")
    def test_wsl_distro_detection_parser(self, mock_run):
        mock_output = (
            "  NAME                             STATE                       VERSION\r\n"
            "  kali-linux                 Stopped                   2\r\n"
            "  docker-desktop         Stopped                   2\r\n"
        ).encode("utf-16le")
        
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)
        
        distros = WSLExecutor.detect_distributions()
        self.assertTrue(len(distros) >= 1)
        self.assertEqual(distros[0]["name"], "kali-linux")
        self.assertEqual(distros[0]["version"], 2)

if __name__ == "__main__":
    unittest.main()
