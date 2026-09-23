"""FreshSend: a local freshness check before sending files."""

from .core import FileSnapshot, FreshnessReport, FreshSendError, inspect_file

__version__ = "0.1.0"

__all__ = [
    "FileSnapshot",
    "FreshnessReport",
    "FreshSendError",
    "__version__",
    "inspect_file",
]
