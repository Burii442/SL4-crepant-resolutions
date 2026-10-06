"""Executable discovery shared by the exact geometric endpoint checks."""
import os
from pathlib import Path
import shutil


def singular_executable():
    """Select SL4_SINGULAR, then PATH, then Sage's local installation.

    A supplied override must work; silently selecting a different executable
    would make the recorded calculation differ from the user's request.
    This function requires no Sage imports when an override or PATH works.
    """
    override = os.environ.get('SL4_SINGULAR')
    if override is not None:
        found = shutil.which(os.path.expanduser(override)) if override else None
        if not found:
            raise FileNotFoundError('SL4_SINGULAR is missing or not executable: '+repr(override))
        return Path(found).resolve()
    found = shutil.which('Singular')
    if found:
        return Path(found).resolve()
    try:
        from sage.env import SAGE_LOCAL
    except ImportError:
        SAGE_LOCAL = None
    if SAGE_LOCAL:
        candidate = Path(SAGE_LOCAL)/'bin/Singular'
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise FileNotFoundError('Singular executable unavailable; set SL4_SINGULAR or put Singular on PATH')
