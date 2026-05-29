"""
basic_logger/example.py

Demonstration script for the basic_logger package.

Run from the project root::

    python -m basic_logger.example

Expected behaviour
------------------
* Console output: WARNING, ERROR, and CRITICAL messages only.
* File output (logs/app.log): all five levels — DEBUG through CRITICAL.

The script exercises each log level, demonstrates logger name hierarchy
(root module vs. sub-component), and shows that the file handler captures
everything while the console handler remains quiet for routine messages.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import logging

# ---------------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------------
from basic_logger import get_logger


# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------

#: Logger for this example module.
log: logging.Logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Demo functions
# ---------------------------------------------------------------------------

def demo_log_levels() -> None:
    """Emit one message at each of the five standard logging levels.

    Console will display only the WARNING, ERROR, and CRITICAL lines.
    The log file will contain all five lines, including DEBUG and INFO.
    """
    log.debug("debug: fine-grained diagnostic detail")
    log.info("info: normal operational milestone")
    log.warning("warning: something unexpected but recoverable")
    log.error("error: operation failed, investigation needed")
    log.critical("critical: system cannot continue normally")


def demo_logger_hierarchy() -> None:
    """Show that child loggers inherit configuration from parent loggers.

    Creates a child logger (``basic_logger.example.child``) and confirms
    that it writes to the same handlers as the parent without requiring
    separate configuration.
    """
    child = get_logger(f"{__name__}.child")
    child.info("child logger inherits handlers from parent — no extra setup needed")


def demo_exception_logging() -> None:
    """Log an exception with full traceback using :meth:`logging.Logger.exception`.

    Demonstrates the preferred pattern for logging caught exceptions so that
    the stack trace is preserved in the log file for post-mortem analysis.
    """
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("caught an exception — full traceback captured in log file")


def demo_structured_context() -> None:
    """Pass extra context fields to the logger using the ``extra`` parameter.

    Shows how to attach request IDs, user IDs, or other structured fields
    to individual log records without modifying the global format string.
    """
    log.info(
        "processed request",
        extra={"request_id": "req-42", "user_id": "u-7"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run all demonstration functions in sequence.

    Prints a brief header to stdout so the user can visually distinguish
    console log output (which goes to stderr) from script output.
    """
    print("=== basic_logger demo ===")
    print("Console shows WARNING and above; all levels go to the log file.\n")

    demo_log_levels()
    demo_logger_hierarchy()
    demo_exception_logging()
    demo_structured_context()

    print("\nDone. Check the logs folder for the full log file (logs/app.log).")


if __name__ == "__main__":
    main()
