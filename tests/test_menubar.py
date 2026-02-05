"""Tests for the menu bar UI module."""

import sys
import unittest
from unittest import mock

# Skip all tests if not on macOS or rumps unavailable
try:
    import rumps  # noqa: F401

    RUMPS_AVAILABLE = True
except ImportError:
    RUMPS_AVAILABLE = False


@unittest.skipUnless(
    sys.platform == "darwin" and RUMPS_AVAILABLE, "Requires macOS and rumps"
)
class STTMenuBarTests(unittest.TestCase):
    """Tests for STTMenuBar class."""

    def setUp(self):
        """Set up test fixtures."""
        from claude_stt.config import Config
        from claude_stt.menubar import STTMenuBar

        self.mock_daemon = mock.MagicMock()
        self.mock_daemon.config = Config()
        self.app = STTMenuBar(self.mock_daemon)

    def test_icon_constants_defined(self):
        """Icon constants should be defined."""
        self.assertEqual(self.app.ICON_IDLE, "\u25CF")  # ● filled circle
        self.assertEqual(self.app.ICON_RECORDING, "\U0001F534")  # 🔴
        self.assertEqual(self.app.ICON_PROCESSING, "\u25CB")  # ○ empty circle

    def test_recording_start_sets_recording_flag(self):
        """on_recording_start should set _recording flag."""
        self.assertFalse(self.app._recording)
        self.app.on_recording_start()
        self.assertTrue(self.app._recording)

    def test_recording_stop_clears_recording_flag(self):
        """on_recording_stop should clear _recording flag."""
        self.app.on_recording_start()
        self.assertTrue(self.app._recording)
        self.app.on_recording_stop()
        self.assertFalse(self.app._recording)

    def test_status_menu_item_updates(self):
        """Status menu item should reflect current state."""
        self.assertEqual(self.app._status_item.title, "Status: Ready")

        self.app.on_recording_start()
        self.assertEqual(self.app._status_item.title, "Status: Recording...")

        self.app.on_recording_stop()
        self.assertEqual(self.app._status_item.title, "Status: Processing...")

        self.app.on_transcription_complete()
        self.assertEqual(self.app._status_item.title, "Status: Ready")

    def test_stop_daemon_calls_daemon_stop(self):
        """'Stop Daemon' menu click should call daemon.stop()."""
        with mock.patch("rumps.quit_application"):
            self.app._stop_daemon(None)
            self.mock_daemon.stop.assert_called_once()

    def test_quit_calls_daemon_stop(self):
        """'Quit' menu click should call daemon.stop()."""
        with mock.patch("rumps.quit_application"):
            self.app._quit(None)
            self.mock_daemon.stop.assert_called_once()

    def test_quit_calls_on_quit_callback(self):
        """'Quit' should call the optional on_quit callback."""
        on_quit = mock.MagicMock()
        from claude_stt.menubar import STTMenuBar

        app = STTMenuBar(self.mock_daemon, on_quit=on_quit)
        with mock.patch("rumps.quit_application"):
            app._quit(None)
            on_quit.assert_called_once()


@unittest.skipUnless(
    sys.platform == "darwin" and RUMPS_AVAILABLE, "Requires macOS and rumps"
)
class MenuBarCallbackTimingTests(unittest.TestCase):
    """Tests for callback performance requirements."""

    def test_callbacks_are_nonblocking(self):
        """Callbacks should complete quickly (<10ms)."""
        import time

        from claude_stt.config import Config
        from claude_stt.menubar import STTMenuBar

        mock_daemon = mock.MagicMock()
        mock_daemon.config = Config()
        app = STTMenuBar(mock_daemon)

        # Test start callback
        start = time.perf_counter()
        app.on_recording_start()
        elapsed_start = time.perf_counter() - start
        self.assertLess(elapsed_start, 0.010, "on_recording_start took too long")

        # Test stop callback
        start = time.perf_counter()
        app.on_recording_stop()
        elapsed_stop = time.perf_counter() - start
        self.assertLess(elapsed_stop, 0.010, "on_recording_stop took too long")

        # Test complete callback
        start = time.perf_counter()
        app.on_transcription_complete()
        elapsed_complete = time.perf_counter() - start
        self.assertLess(
            elapsed_complete, 0.010, "on_transcription_complete took too long"
        )


@unittest.skipUnless(
    sys.platform == "darwin" and RUMPS_AVAILABLE, "Requires macOS and rumps"
)
class MenuBarErrorHandlingTests(unittest.TestCase):
    """Tests for error handling in menubar callbacks."""

    def test_callback_error_does_not_propagate(self):
        """Errors in callbacks should be caught, not propagated."""
        from claude_stt.config import Config
        from claude_stt.menubar import STTMenuBar

        mock_daemon = mock.MagicMock()
        mock_daemon.config = Config()
        app = STTMenuBar(mock_daemon)

        # Make title setter raise
        with mock.patch.object(
            type(app), "title", new_callable=mock.PropertyMock
        ) as mock_title:
            mock_title.side_effect = Exception("Cocoa error")

            # Should not raise - errors are caught and logged
            app.on_recording_start()  # No exception

    def test_stop_daemon_handles_daemon_error(self):
        """_stop_daemon should handle errors from daemon.stop()."""
        from claude_stt.config import Config
        from claude_stt.menubar import STTMenuBar

        mock_daemon = mock.MagicMock()
        mock_daemon.config = Config()
        mock_daemon.stop.side_effect = Exception("Stop failed")

        app = STTMenuBar(mock_daemon)
        with mock.patch("rumps.quit_application"):
            # Should not raise
            app._stop_daemon(None)


if __name__ == "__main__":
    unittest.main()
