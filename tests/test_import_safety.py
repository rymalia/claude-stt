"""Tests for import safety - ensuring no top-level rumps imports break Linux/Windows."""

import ast
import unittest
from pathlib import Path


class ImportSafetyTests(unittest.TestCase):
    """Tests to ensure optional dependencies don't have top-level imports.

    These tests verify that rumps is only imported conditionally,
    ensuring the daemon works on Linux/Windows where rumps isn't available.
    """

    def _get_top_level_imports(self, filepath: Path) -> list[str]:
        """Extract all top-level import names from a Python file."""
        with open(filepath) as f:
            tree = ast.parse(f.read())

        imports = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                # Also check the names being imported
                for alias in node.names:
                    imports.append(alias.name)
        return imports

    def test_daemon_module_no_rumps_import(self):
        """daemon.py should not have top-level rumps import."""
        daemon_path = Path(__file__).parent.parent / "src" / "claude_stt" / "daemon.py"
        imports = self._get_top_level_imports(daemon_path)

        self.assertNotIn("rumps", imports)
        self.assertNotIn(".menubar", imports)
        self.assertNotIn("menubar", imports)

    def test_daemon_service_no_rumps_import(self):
        """daemon_service.py should not have top-level rumps import."""
        daemon_service_path = (
            Path(__file__).parent.parent / "src" / "claude_stt" / "daemon_service.py"
        )
        imports = self._get_top_level_imports(daemon_service_path)

        self.assertNotIn("rumps", imports)
        self.assertNotIn(".menubar", imports)
        self.assertNotIn("menubar", imports)

    def test_config_no_rumps_import(self):
        """config.py should not have top-level rumps import."""
        config_path = Path(__file__).parent.parent / "src" / "claude_stt" / "config.py"
        imports = self._get_top_level_imports(config_path)

        self.assertNotIn("rumps", imports)

    def test_platform_no_rumps_import(self):
        """platform.py should not have top-level rumps import."""
        platform_path = (
            Path(__file__).parent.parent / "src" / "claude_stt" / "platform.py"
        )
        imports = self._get_top_level_imports(platform_path)

        # platform.py imports rumps inside menubar_available(), not at top level
        self.assertNotIn("rumps", imports)


class ModuleImportTests(unittest.TestCase):
    """Tests that modules can be imported (they don't fail on import)."""

    def test_daemon_imports_successfully(self):
        """daemon.py should import without errors."""
        from claude_stt import daemon  # noqa: F401

    def test_daemon_service_imports_successfully(self):
        """daemon_service.py should import without errors."""
        from claude_stt import daemon_service  # noqa: F401

    def test_config_imports_successfully(self):
        """config.py should import without errors."""
        from claude_stt import config  # noqa: F401

    def test_platform_imports_successfully(self):
        """platform.py should import without errors."""
        from claude_stt import platform  # noqa: F401


if __name__ == "__main__":
    unittest.main()
