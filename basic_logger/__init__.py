"""
basic_logger/__init__.py

Public surface of the basic_logger package.

Importing :func:`get_logger` from here (rather than from the internal
``logger`` module) keeps downstream code decoupled from the package layout
and allows internal refactors without breaking existing import paths::

    from basic_logger import get_logger

    log = get_logger(__name__)
"""

from basic_logger.logger import get_logger

__all__ = ["get_logger"]
