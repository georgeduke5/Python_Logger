"""
basic_logger/logger.py

Production-ready logger factory for the basic_logger package.

Reads configuration from config.json (co-located with this module) and
returns fully configured :class:`logging.Logger` instances with three
handlers attached:

* **RotatingFileHandler** — size-based rotation (default 10 MB, 7 backups).
* **TimedRotatingFileHandler** — daily rotation at midnight.
* **StreamHandler** — console output (WARNING and above only).

Typical usage::

    from basic_logger import get_logger

    log = get_logger(__name__)
    log.info("Service started")
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import json
import logging
import logging.handlers
import os
import pathlib
import sys
import warnings
from typing import Any

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Absolute path to the config file that lives next to this module.
_CONFIG_PATH: pathlib.Path = pathlib.Path(__file__).parent / "config.json"

#: Fallback configuration used when config.json cannot be read or is invalid.
_DEFAULT_CONFIG: dict[str, Any] = {
    "log_file_path": "logs/app.log",
    "max_bytes": 10_485_760,
    "backup_count": 7,
    "log_format": (
        "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
    ),
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "console_log_level": "WARNING",
    "file_log_level": "DEBUG",
    "rotation_when": "midnight",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_config() -> dict[str, Any]:
    """Load logger configuration from *config.json*.

    Falls back to :data:`_DEFAULT_CONFIG` and emits a :func:`warnings.warn`
    if the file is missing, unreadable, or contains invalid JSON so that the
    calling application always receives a usable configuration.

    Returns
    -------
    dict[str, Any]
        Merged configuration dictionary (file values override defaults for
        keys that are present; missing keys are filled from defaults).
    """
    config = dict(_DEFAULT_CONFIG)
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        standard_fmt   = raw.get("formatters", {}).get("standard", {})
        console_h      = raw.get("handlers",   {}).get("console",    {})
        file_h         = raw.get("handlers",   {}).get("file",       {})
        timed_h        = raw.get("handlers",   {}).get("timed_file", {})

        for key in ("log_format", "datefmt"):
            if key in standard_fmt:
                config[key] = standard_fmt[key]
        for key in ("console_log_level",):
            if key in console_h:
                config[key] = console_h[key]
        for key in ("log_file_path", "max_bytes", "backup_count", "file_log_level"):
            if key in file_h:
                config[key] = file_h[key]
        for key in ("rotation_when",):
            if key in timed_h:
                config[key] = timed_h[key]
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        warnings.warn(
            f"Could not load {_CONFIG_PATH}: {exc}. Using default config.",
            stacklevel=2,
        )
    return config


def _resolve_log_path(raw_path: str) -> pathlib.Path:
    """Resolve *raw_path* to an absolute :class:`pathlib.Path`.

    Relative paths are interpreted relative to the current working directory
    at import time.  Parent directories are created automatically
    (``mkdir -p`` semantics) so that handlers can open the file immediately.

    Parameters
    ----------
    raw_path:
        The ``log_file_path`` string from configuration, e.g. ``"logs/app.log"``.

    Returns
    -------
    pathlib.Path
        Absolute, fully-resolved path with all parent directories guaranteed
        to exist.
    """
    path = pathlib.Path(raw_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _make_formatter(fmt: str, datefmt: str) -> logging.Formatter:
    """Create a :class:`logging.Formatter` with the given timestamp format.

    Parameters
    ----------
    fmt:
        Format string passed directly to :class:`logging.Formatter`.
    datefmt:
        Date/time format string, e.g. ``"%Y-%m-%d %H:%M:%S"``.

    Returns
    -------
    logging.Formatter
    """
    return logging.Formatter(fmt, datefmt=datefmt)


def _make_rotating_file_handler(
    log_path: pathlib.Path,
    level: int,
    formatter: logging.Formatter,
    max_bytes: int,
    backup_count: int,
) -> logging.handlers.RotatingFileHandler:
    """Build a size-based :class:`~logging.handlers.RotatingFileHandler`.

    The file is opened in append mode so that restarts do not clobber
    previous log data.  ``encoding="utf-8"`` is set explicitly for
    cross-platform safety.

    Parameters
    ----------
    log_path:
        Absolute path to the log file.
    level:
        Numeric logging level (e.g. ``logging.DEBUG``).
    formatter:
        Pre-built :class:`logging.Formatter` to attach to this handler.
    max_bytes:
        Maximum file size in bytes before rotation (0 = never rotate by size).
    backup_count:
        Number of rotated backup files to retain.

    Returns
    -------
    logging.handlers.RotatingFileHandler
    """
    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
        mode="a",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def _make_timed_rotating_handler(
    log_path: pathlib.Path,
    level: int,
    formatter: logging.Formatter,
    when: str,
    backup_count: int,
) -> logging.handlers.TimedRotatingFileHandler:
    """Build a time-based :class:`~logging.handlers.TimedRotatingFileHandler`.

    Parameters
    ----------
    log_path:
        Absolute path to the log file.  Both handlers may target the same
        file; Python's logging infrastructure serialises writes.
    level:
        Numeric logging level.
    formatter:
        Pre-built :class:`logging.Formatter` to attach to this handler.
    when:
        Rotation schedule string accepted by
        :class:`~logging.handlers.TimedRotatingFileHandler`
        (``"midnight"``, ``"h"``, ``"d"``, …).
    backup_count:
        Number of rotated backup files to retain.

    Returns
    -------
    logging.handlers.TimedRotatingFileHandler
    """
    handler = logging.handlers.TimedRotatingFileHandler(
        log_path,
        when=when,
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def _make_console_handler(
    level: int,
    formatter: logging.Formatter,
) -> logging.StreamHandler:
    """Build a :class:`logging.StreamHandler` that writes to *stderr*.

    Console output is intentionally restricted to WARNING and above so that
    routine INFO/DEBUG noise stays out of operator terminals while still
    surfacing actionable alerts.

    Parameters
    ----------
    level:
        Numeric logging level.  Typically ``logging.WARNING``.
    formatter:
        Pre-built :class:`logging.Formatter` to attach to this handler.

    Returns
    -------
    logging.StreamHandler
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """Return a fully configured :class:`logging.Logger` for *name*.

    Handlers are attached only on the first call for a given *name*;
    subsequent calls return the cached logger without adding duplicate
    handlers.  This makes ``get_logger`` safe to call at module import time
    or inside frequently-invoked functions.

    Configuration is loaded once per process from *config.json*.  If the
    file is absent or malformed the module falls back to
    :data:`_DEFAULT_CONFIG` so that callers always receive a working logger.

    Parameters
    ----------
    name:
        Logger name, typically ``__name__`` of the calling module.  Follows
        the standard dotted-hierarchy convention so that child loggers
        inherit settings from parent loggers automatically.

    Returns
    -------
    logging.Logger
        Logger with :class:`~logging.handlers.RotatingFileHandler`,
        :class:`~logging.handlers.TimedRotatingFileHandler`, and
        :class:`logging.StreamHandler` attached.

    Raises
    ------
    OSError
        Re-raised (after logging a critical message to the root logger) if
        the log directory cannot be created due to a permissions error or
        invalid path, so the caller can decide whether to abort or continue
        without file logging.

    Examples
    --------
    >>> from basic_logger import get_logger
    >>> log = get_logger(__name__)
    >>> log.info("Hello, world!")
    """
    config = _load_config()
    log_path = _resolve_log_path(config["log_file_path"])
    formatter = _make_formatter(config["log_format"], config["datefmt"])

    file_level = getattr(logging, config["file_log_level"].upper(), logging.DEBUG)
    console_level = getattr(logging, config["console_log_level"].upper(), logging.WARNING)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_make_rotating_file_handler(
            log_path, file_level, formatter, config["max_bytes"], config["backup_count"]
        ))
        logger.addHandler(_make_timed_rotating_handler(
            log_path, file_level, formatter, config["rotation_when"], config["backup_count"]
        ))
        logger.addHandler(_make_console_handler(console_level, formatter))

    return logger
