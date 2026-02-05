"""macOS menu bar status indicator for claude-stt.

This module is only imported on macOS when rumps is available.
It provides visual feedback for recording state in the menu bar.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Optional

import rumps

if TYPE_CHECKING:
    from .daemon_service import STTDaemon

logger = logging.getLogger(__name__)


class STTMenuBar(rumps.App):
    """Menu bar app that shows recording state.

    States:
        - Idle (ready): microphone icon
        - Recording: red circle
        - Processing: hourglass (set externally via callback)
    """

    # Icon states
    ICON_IDLE = "\u25CF"  # ● filled circle
    ICON_RECORDING = "\U0001F534"  # 🔴 red circle
    ICON_PROCESSING = "\u25CB"  # ○ empty circle (processing)

    def __init__(
        self,
        daemon: "STTDaemon",
        on_quit: Optional[Callable[[], None]] = None,
    ):
        """Initialize the menu bar app.

        Args:
            daemon: The STTDaemon instance to control.
            on_quit: Optional callback when user quits from menu.
        """
        super().__init__(self.ICON_IDLE, quit_button=None)
        self.daemon = daemon
        self._on_quit = on_quit
        self._recording = False

        # Build menu
        self._status_item = rumps.MenuItem("Status: Ready")
        self._hotkey_item = rumps.MenuItem(f"Hotkey: {daemon.config.hotkey}")
        self._stop_daemon_item = rumps.MenuItem("Stop Daemon", callback=self._stop_daemon)
        self._quit_item = rumps.MenuItem("Quit", callback=self._quit)

        self.menu = [
            self._status_item,
            self._hotkey_item,
            None,  # Separator
            self._stop_daemon_item,
            self._quit_item,
        ]

        # Set up timer for max recording time checks
        # This replaces the main loop's time.sleep(0.1)
        self._timer = rumps.Timer(self._check_max_recording_time, 0.1)

    def start_timer(self) -> None:
        """Start the periodic timer for recording time checks."""
        self._timer.start()

    def on_recording_start(self) -> None:
        """Update UI when recording starts.

        Called from hotkey callback thread - must be non-blocking.
        rumps handles the Cocoa UI update asynchronously.
        """
        try:
            self._recording = True
            self.title = self.ICON_RECORDING
            self._status_item.title = "Status: Recording..."
        except Exception:
            # Don't let UI errors affect recording
            logger.exception("Failed to update menu bar on recording start")

    def on_recording_stop(self) -> None:
        """Update UI when recording stops.

        Called from hotkey callback thread - must be non-blocking.
        """
        try:
            self._recording = False
            self.title = self.ICON_PROCESSING
            self._status_item.title = "Status: Processing..."
        except Exception:
            logger.exception("Failed to update menu bar on recording stop")

    def on_transcription_complete(self) -> None:
        """Update UI when transcription is complete.

        Called from transcription worker thread.
        """
        try:
            self.title = self.ICON_IDLE
            self._status_item.title = "Status: Ready"
        except Exception:
            logger.exception("Failed to update menu bar on transcription complete")

    def _check_max_recording_time(self, _sender: rumps.Timer) -> None:
        """Periodic check for max recording time.

        This delegates to the daemon's check method.
        """
        try:
            self.daemon._check_max_recording_time()
        except Exception:
            logger.exception("Error in max recording time check")

    def _stop_daemon(self, _sender: rumps.MenuItem) -> None:
        """Handle 'Stop Daemon' menu click."""
        try:
            self.daemon.stop()
        except Exception:
            logger.exception("Error stopping daemon from menu")
        finally:
            rumps.quit_application()

    def _quit(self, _sender: rumps.MenuItem) -> None:
        """Handle 'Quit' menu click."""
        try:
            self.daemon.stop()
            if self._on_quit:
                self._on_quit()
        except Exception:
            logger.exception("Error during quit")
        finally:
            rumps.quit_application()
