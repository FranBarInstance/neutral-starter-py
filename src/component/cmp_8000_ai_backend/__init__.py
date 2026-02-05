"""
AI Models component initialization.
"""
import os
import sys


def init_component(component, _component_schema, _schema):
    """Initialize AI Models component."""
    # Add lib folder to sys.path
    lib_path = os.path.join(component["path"], "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
