"""WSGI application entry point """
# pylint: disable=C0103

import glob
import os
import sys


# Set environment flag for WSGI
os.environ["RUNNING_UNDER_WSGI"] = "True"

# Get project root directory (resolving any symlinks)
src_dir = os.path.dirname(os.path.realpath(__file__))
venv_dir = os.path.join(src_dir, '..', '.venv')  # Adjust if your venv is elsewhere

if not os.path.exists(venv_dir):
    raise RuntimeError(f"Virtual environment directory not found: {venv_dir}")

# Use a set to avoid duplicate paths
site_packages_dirs = set()

# Platform-specific subdirectory
lib_subdir = 'Lib' if os.name == 'nt' else 'lib'

# Pattern to match pythonX.X/site-packages in virtualenv
pattern = os.path.join(venv_dir, lib_subdir, 'python*', 'site-packages')
for site_pkg in glob.glob(pattern):
    real_path = os.path.realpath(site_pkg)
    if os.path.isdir(real_path):
        site_packages_dirs.add(real_path)

# Fallback method if no site-packages found
if not site_packages_dirs:
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    fallback_path = os.path.join(venv_dir, lib_subdir, python_version, 'site-packages')
    real_fallback_path = os.path.realpath(fallback_path)
    if os.path.isdir(real_fallback_path):
        site_packages_dirs.add(real_fallback_path)

# Validate we found at least one site-packages
if not site_packages_dirs:
    raise RuntimeError(
        "No valid site-packages directories found in virtual environment. "
        f"Tried paths matching: {pattern}"
    )

# Add all found paths to Python path (newest versions first), avoiding duplicates
for pkg_dir in sorted(site_packages_dirs, reverse=True):
    normalized_path = os.path.normpath(os.path.realpath(pkg_dir))
    if normalized_path not in sys.path:
        sys.path.insert(0, normalized_path)
        print(f"Added to Python path: {normalized_path}")

# Add main project directory to path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import the Flask application only after all paths have been configured
from app import create_app  # pylint: disable=C0413
application = create_app(debug=False)
