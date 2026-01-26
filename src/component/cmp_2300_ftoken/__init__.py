"""Component FToken - Init"""

import os
import sys


def init_component(_component, _component_schema, _schema):
    """Initialize FToken component."""
    expose_ftoken_lib()


def expose_ftoken_lib():
    """Expose FToken library to sys.path."""

    # Add component path to sys.path for the usage of ftoken_0yt2sa
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(base_dir, 'lib')
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
