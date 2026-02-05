"""Tests for menu_bar config option."""

import sys
import unittest
from unittest import mock


class ConfigMenuBarTests(unittest.TestCase):
    """Tests for menu_bar configuration handling."""

    def test_menu_bar_defaults_to_true(self):
        """menu_bar should default to True."""
        from claude_stt.config import Config

        config = Config()
        self.assertTrue(config.menu_bar)

    def test_menu_bar_can_be_disabled(self):
        """User can explicitly set menu_bar=False."""
        from claude_stt.config import Config

        config = Config(menu_bar=False)
        self.assertFalse(config.menu_bar)

    def test_menu_bar_validated_from_string_true(self):
        """String 'true' should be converted to bool True."""
        from claude_stt.config import Config

        config = Config(menu_bar="true")
        config = config.validate()
        self.assertTrue(config.menu_bar)

    def test_menu_bar_validated_from_string_false(self):
        """String 'false' should be converted to bool False."""
        from claude_stt.config import Config

        config = Config(menu_bar="false")
        config = config.validate()
        self.assertFalse(config.menu_bar)


class EffectiveMenuBarTests(unittest.TestCase):
    """Tests for effective_menu_bar() method."""

    def test_effective_menu_bar_false_when_config_disabled(self):
        """effective_menu_bar() returns False when menu_bar=False."""
        from claude_stt.config import Config

        config = Config(menu_bar=False)
        self.assertFalse(config.effective_menu_bar())

    def test_effective_menu_bar_false_on_linux(self):
        """effective_menu_bar() returns False on Linux even if config=True."""
        with mock.patch.object(sys, "platform", "linux"):
            from claude_stt import platform
            import importlib

            importlib.reload(platform)

            from claude_stt.config import Config

            config = Config(menu_bar=True)
            self.assertFalse(config.effective_menu_bar())

    def test_effective_menu_bar_false_on_windows(self):
        """effective_menu_bar() returns False on Windows even if config=True."""
        with mock.patch.object(sys, "platform", "win32"):
            from claude_stt import platform
            import importlib

            importlib.reload(platform)

            from claude_stt.config import Config

            config = Config(menu_bar=True)
            self.assertFalse(config.effective_menu_bar())

    def test_effective_menu_bar_true_on_macos_with_rumps(self):
        """effective_menu_bar() returns True on macOS with rumps."""
        with mock.patch.object(sys, "platform", "darwin"):
            mock_rumps = mock.MagicMock()
            with mock.patch.dict(sys.modules, {"rumps": mock_rumps}):
                from claude_stt import platform
                import importlib

                importlib.reload(platform)

                from claude_stt.config import Config

                config = Config(menu_bar=True)
                self.assertTrue(config.effective_menu_bar())


if __name__ == "__main__":
    unittest.main()
