"""Compatibility shim for tools that import `blogicum.settings` from repo root.

This re-exports the actual Django settings module located at
`blogicum/blogicum/settings.py`.
"""

from blogicum.blogicum.settings import *  # noqa: F401,F403

