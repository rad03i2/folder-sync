"""Folder Sync — safe, preview-first one-way folder synchronization."""

from .core import Action, apply, plan, sha256, validate_roots

__all__ = ["Action", "apply", "plan", "sha256", "validate_roots"]
__version__ = "1.0.0"
