"""Platform detection utilities for claude-stt."""

import sys


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform == "linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def menubar_available() -> bool:
    """Check if menu bar support is available (macOS + rumps installed).

    Returns True only if:
    - Running on macOS
    - rumps is installed and importable
    """
    if not is_macos():
        return False
    try:
        import rumps  # noqa: F401

        return True
    except ImportError:
        return False
