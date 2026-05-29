# Python Logger

A production-ready Python logging framework demonstrating enterprise logging patterns,
architectural best practices, and clean code principles.

---

## Overview

This project implements a reusable, configurable logging framework for Python applications.
It is designed to be dropped into any Python project as a standalone module, providing
structured logging with file rotation, multiple output handlers, and external configuration
management — without modifying application code.

---

## Features

- **File-based logging** with size-based rotation (configurable, default 10 MB)
- **Time-based rotation** (configurable, default daily at midnight)
- **Console output** restricted to WARNING and above — keeps terminals clean
- **File output** captures DEBUG and above — full detail for troubleshooting
- **External JSON configuration** — adjust logging behavior without touching code
- **Graceful fallback** to sensible defaults if configuration file is missing or malformed
- **Duplicate handler prevention** — safe to call `get_logger()` multiple times
- **Type hints and docstrings** throughout — PEP-8 compliant

---

## Project Structure

```
python_logger/
├── basic_logger/
│   ├── __init__.py          # Package exports
│   ├── logger.py            # Core logging module
│   ├── config.json          # External configuration
│   ├── example.py           # Usage demonstration
│   └── README.md            # Module-level documentation
├── advanced_logger/         # In development
│   ├── __init__.py
│   ├── logger.py
│   ├── handlers.py
│   ├── formatters.py
│   ├── example.py
│   └── README.md
├── logs/                    # Log output directory (git-ignored)
├── .gitignore
├── LICENSE
└── README.md
```

---

## Quick Start

### Installation

No external dependencies required for `basic_logger`. Clone the repository and import directly.

```bash
git clone https://github.com/georgeduke5/python_logger.git
```

### Basic Usage

```python
from basic_logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("Application started successfully")
logger.warning("Configuration value missing, using default")
logger.error("Failed to connect to database")
logger.critical("System failure — shutting down")
```

### Running the Example

```bash
python -m basic_logger.example
```

---

## Configuration

Logging behavior is controlled via `basic_logger/config.json`. No code changes required.

```json
{
  "log_file_path": "logs/app.log",
  "max_bytes": 10485760,
  "backup_count": 7,
  "file_log_level": "DEBUG",
  "console_log_level": "WARNING",
  "rotation_when": "midnight"
}
```

### Configuration Options

| Key | Default | Description |
|---|---|---|
| `log_file_path` | `logs/app.log` | Path to the log file |
| `max_bytes` | `10485760` (10 MB) | File size before rotation |
| `backup_count` | `7` | Number of backup files to retain |
| `file_log_level` | `DEBUG` | Minimum level written to file |
| `console_log_level` | `WARNING` | Minimum level written to console |
| `rotation_when` | `midnight` | Time-based rotation schedule |

---

## Log Rotation Strategy

This framework implements a dual-rotation strategy:

- **Size-based rotation** — rotates when the log file exceeds `max_bytes`
- **Time-based rotation** — rotates daily at `midnight`

Whichever threshold is reached first triggers rotation. Up to `backup_count` files are
retained before the oldest is deleted. This prevents unbounded disk usage in production
environments.

---

## Architectural Decisions

### Why external JSON configuration?

Configuration is separated from code so that log levels, file paths, and rotation thresholds
can be adjusted per environment (development, staging, production) without modifying source
code or triggering a deployment.

### Why two rotation handlers?

Size-based rotation handles sudden log spikes (e.g., a burst of errors). Time-based rotation
handles gradual accumulation. Using both ensures predictable disk usage under all conditions.

### Why restrict console to WARNING and above?

In production, console output is typically captured by process supervisors or container
runtimes. Flooding stdout with DEBUG and INFO messages creates noise that obscures actionable
alerts. File logging retains full detail for post-incident analysis.

### Why prevent duplicate handlers?

Python's logging module caches loggers by name. Calling `get_logger(__name__)` from the same
module multiple times — a common pattern in long-running applications — would otherwise attach
duplicate handlers, causing each message to be written multiple times. The handler check
prevents this.

---

## Log Format

```
2026-05-21 14:30:45 - my_module - INFO - process_data:42 - Processing 1000 records
```

| Field | Description |
|---|---|
| Timestamp | ISO 8601 format (`YYYY-MM-DD HH:MM:SS`) |
| Logger name | Module `__name__` passed to `get_logger()` |
| Level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| Location | `function_name:line_number` |
| Message | Log message content |

---

## Logging Levels Reference

| Level | Use Case |
|---|---|
| `DEBUG` | Detailed diagnostic information for development |
| `INFO` | Confirmation that things are working as expected |
| `WARNING` | Something unexpected happened but the application continues |
| `ERROR` | A serious problem — a function could not complete |
| `CRITICAL` | A severe error — the application may not be able to continue |

---

## Roadmap

- [x] Basic logger with dual rotation
- [x] External JSON configuration
- [x] Console and file handler separation
- [ ] Advanced logger with structured JSON output
- [ ] Custom sanitization filter for sensitive data redaction
- [ ] Audit logging handler
- [ ] Integration example with pytest test suite
- [ ] Docker deployment example

---

## Development Approach

This project was developed using **agentic AI development** with Claude Code (Anthropic).
Architecture decisions, trade-offs, and code reviews were conducted collaboratively with AI
assistance, with all final design decisions and code approvals made by the author.

This approach demonstrates proficiency in leveraging AI as a productivity multiplier while
maintaining engineering judgment and code quality standards.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**George Duke**  
Software Architect  
[GitHub](https://github.com/georgeduke5)