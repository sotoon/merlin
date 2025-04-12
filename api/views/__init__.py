"""
Aggregator module for view classes and functions.
It collects public names from submodules.
"""

from . import note, auth, form, profile

# Import everything from each submodule into this package's namespace.
from .note import *
from .auth import *
from .form import *
from .profile import *


__all__ = note.__all__ + auth.__all__ + form.__all__ + profile.__all__
