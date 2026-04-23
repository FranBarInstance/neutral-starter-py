#!/usr/bin/env python3
"""Component management script for Neutral TS Starter Py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    """Add src directory to Python path."""
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))


def get_component_dir() -> Path:
    """Get the component directory path."""
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "src" / "component"


def get_components(component_dir: Path) -> dict[str, dict]:
    """
    Scan component directory and return component information.

    Returns:
        Dictionary with keys: 'enabled', 'disabled', 'all'
    """
    components = {
        "enabled": [],
        "disabled": [],
        "all": [],
    }

    if not component_dir.exists():
        print(f"Error: Component directory not found: {component_dir}", file=sys.stderr)
        return components

    for item in sorted(component_dir.iterdir()):
        if not item.is_dir():
            continue

        name = item.name

        # Check if it's a component directory (starts with cmp_ or _cmp_)
        if name.startswith("_cmp_"):
            # Disabled component
            manifest_path = item / "manifest.json"
            component_info = {
                "name": name,
                "path": str(item),
                "manifest": None,
                "status": "disabled",
            }
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        component_info["manifest"] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    component_info["error"] = str(e)
            components["disabled"].append(component_info)
            components["all"].append(component_info)

        elif name.startswith("cmp_"):
            # Enabled component
            manifest_path = item / "manifest.json"
            component_info = {
                "name": name,
                "path": str(item),
                "manifest": None,
                "status": "enabled",
            }
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        component_info["manifest"] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    component_info["error"] = str(e)
            components["enabled"].append(component_info)
            components["all"].append(component_info)

    return components


def format_component(component: dict, verbose: bool = False) -> str:
    """Format a component for display."""
    manifest = component.get("manifest") or {}

    if verbose:
        lines = [
            f"  Name: {component['name']}",
            f"  UUID: {manifest.get('uuid', 'N/A')}",
            f"  Display Name: {manifest.get('name', 'N/A')}",
            f"  Description: {manifest.get('description', 'N/A')}",
            f"  Version: {manifest.get('version', 'N/A')}",
            f"  Route: {manifest.get('route', 'N/A')}",
            f"  Status: {component['status']}",
        ]
        if "error" in component:
            lines.append(f"  Error: {component['error']}")
        return "\n".join(lines)

    uuid = manifest.get("uuid", "N/A") if manifest else "N/A"
    display_name = manifest.get("name", "N/A") if manifest else "N/A"
    status_icon = "✓" if component["status"] == "enabled" else "✗"
    return f"  {status_icon} {component['name']:30} {uuid:20} {display_name}"


def cmd_list(args: argparse.Namespace) -> int:
    """List components based on filter."""
    component_dir = get_component_dir()
    components = get_components(component_dir)

    # Determine which components to show
    if args.filter == "enabled":
        to_show = components["enabled"]
        title = "Enabled Components"
    elif args.filter == "disabled":
        to_show = components["disabled"]
        title = "Disabled Components"
    # all
    else:
        to_show = components["all"]
        title = "All Components"

    # Print header
    print(f"\n{title}")
    print("=" * 80)

    if not args.verbose:
        # Print column headers
        print(f"  {'Status':<8} {'Directory':30} {'UUID':20} {'Display Name'}")
        print(f"  {'-'*8} {'-'*30} {'-'*20} {'-'*20}")

    if not to_show:
        print("  No components found.")
        return 0

    for component in to_show:
        print(format_component(component, args.verbose))
        if args.verbose and component != to_show[-1]:
            print()

    # Print summary
    print()
    print(f"Total: {len(to_show)} components")
    if args.filter == "all":
        print(f"  Enabled: {len(components['enabled'])}")
        print(f"  Disabled: {len(components['disabled'])}")

    return 0


def find_components_by_name(component_dir: Path, name: str) -> list[Path]:
    """
    Find component directories by name (with various prefix formats).

    Supports matching:
    - Full name: cmp_7000_hellocomp, _cmp_7000_hellocomp
    - Without cmp prefix: 7000_hellocomp
    - Just the component name: hellocomp

    Args:
        component_dir: Base component directory
        name: Component name (various formats accepted)

    Returns:
        List of matching component paths (may be empty or multiple)
    """
    matches = []

    # Scan all component directories
    if not component_dir.exists():
        return matches

    for item in component_dir.iterdir():
        if not item.is_dir():
            continue

        dir_name = item.name

        # Must be a component directory
        if not (dir_name.startswith("cmp_") or dir_name.startswith("_cmp_")):
            continue

        # Extract parts: prefix + number + name
        # e.g., cmp_7000_hellocomp -> cmp_, 7000, hellocomp
        # e.g., _cmp_7000_hellocomp -> _cmp_, 7000, hellocomp
        if dir_name.startswith("_cmp_"):
            rest = dir_name[5:]
        elif dir_name.startswith("cmp_"):
            rest = dir_name[4:]
        else:
            continue

        # Split number and name (e.g., "7000_hellocomp" -> "7000", "hellocomp")
        parts = rest.split("_", 1)
        if len(parts) == 2:
            _, comp_name = parts
        else:
            comp_name = ""

        # Build all possible identifiers for this component
        identifiers = [
            dir_name,                    # cmp_7000_hellocomp, _cmp_7000_hellocomp
            rest,                        # 7000_hellocomp
            comp_name,                   # hellocomp
            f"cmp_{rest}",               # cmp_7000_hellocomp (normalized)
            f"_cmp_{rest}",              # _cmp_7000_hellocomp (normalized)
        ]

        # Check if the search name matches any identifier
        if name in identifiers:
            matches.append(item)

    return matches


def cmd_enable(args: argparse.Namespace) -> int:  # pylint: disable=too-many-return-statements
    """Enable a disabled component by renaming from _cmp_ to cmp_."""
    component_dir = get_component_dir()

    if not args.component:
        print("Error: Component name is required", file=sys.stderr)
        return 1

    matches = find_components_by_name(component_dir, args.component)

    if not matches:
        print(f"Error: Component '{args.component}' not found", file=sys.stderr)
        return 1

    if len(matches) > 1:
        print(f"Error: Multiple components match '{args.component}':", file=sys.stderr)
        for match in matches:
            print(f"  {match.name}", file=sys.stderr)
        print("Please specify the full component name.", file=sys.stderr)
        return 1

    component_path = matches[0]

    name = component_path.name

    # Check if already enabled
    if name.startswith("cmp_") and not name.startswith("_cmp_"):
        print(f"Component '{name}' is already enabled")
        return 0

    # Must be disabled (_cmp_ prefix)
    if not name.startswith("_cmp_"):
        print(f"Error: '{name}' is not a valid component directory", file=sys.stderr)
        return 1

    # Rename to enable
    new_name = "cmp_" + name[5:]  # Remove _cmp_ and add cmp_
    new_path = component_path.parent / new_name

    try:
        component_path.rename(new_path)
        print(f"Component enabled: {name} -> {new_name}")
        return 0
    except OSError as e:
        print(f"Error renaming component: {e}", file=sys.stderr)
        return 1


def cmd_disable(args: argparse.Namespace) -> int:  # pylint: disable=too-many-return-statements
    """Disable an active component by renaming from cmp_ to _cmp_."""
    component_dir = get_component_dir()

    if not args.component:
        print("Error: Component name is required", file=sys.stderr)
        return 1

    matches = find_components_by_name(component_dir, args.component)

    if not matches:
        print(f"Error: Component '{args.component}' not found", file=sys.stderr)
        return 1

    if len(matches) > 1:
        print(f"Error: Multiple components match '{args.component}':", file=sys.stderr)
        for match in matches:
            print(f"  {match.name}", file=sys.stderr)
        print("Please specify the full component name.", file=sys.stderr)
        return 1

    component_path = matches[0]

    name = component_path.name

    # Check if already disabled
    if name.startswith("_cmp_"):
        print(f"Component '{name}' is already disabled")
        return 0

    # Must be active (cmp_ prefix without _)
    if not name.startswith("cmp_"):
        print(f"Error: '{name}' is not a valid component directory", file=sys.stderr)
        return 1

    # Rename to disable
    new_name = "_cmp_" + name[4:]  # Remove cmp_ and add _cmp_
    new_path = component_path.parent / new_name

    try:
        component_path.rename(new_path)
        print(f"Component disabled: {name} -> {new_name}")
        return 0
    except OSError as e:
        print(f"Error renaming component: {e}", file=sys.stderr)
        return 1


def cmd_reorder(args: argparse.Namespace) -> int:  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
    """Change the load order of a component by renaming its number prefix."""
    component_dir = get_component_dir()

    if not args.component:
        print("Error: Component name is required", file=sys.stderr)
        return 1

    if not args.order:
        print("Error: Order number is required", file=sys.stderr)
        return 1

    # Validate order number
    try:
        order_num = int(args.order)
        if order_num < 0 or order_num > 9999:
            print("Error: Order must be a number between 0000 and 9999", file=sys.stderr)
            return 1
    except ValueError:
        print("Error: Order must be a valid number", file=sys.stderr)
        return 1

    matches = find_components_by_name(component_dir, args.component)

    if not matches:
        print(f"Error: Component '{args.component}' not found", file=sys.stderr)
        return 1

    if len(matches) > 1:
        print(f"Error: Multiple components match '{args.component}':", file=sys.stderr)
        for match in matches:
            print(f"  {match.name}", file=sys.stderr)
        print("Please specify the full component name.", file=sys.stderr)
        return 1

    component_path = matches[0]
    name = component_path.name

    # Determine prefix and rest of name
    if name.startswith("_cmp_"):
        prefix = "_cmp_"
        rest = name[5:]
    elif name.startswith("cmp_"):
        prefix = "cmp_"
        rest = name[4:]
    else:
        print(f"Error: '{name}' is not a valid component directory", file=sys.stderr)
        return 1

    # Split number and name (e.g., "7000_hellocomp" -> "7000", "hellocomp")
    parts = rest.split("_", 1)
    if len(parts) != 2:
        print(f"Error: Cannot parse component name format: {name}", file=sys.stderr)
        return 1

    _, comp_name = parts  # old_number is not needed

    # Build new name
    new_number = f"{order_num:04d}"
    new_name = f"{prefix}{new_number}_{comp_name}"
    new_path = component_path.parent / new_name

    # Check if target already exists
    if new_path.exists():
        print(f"Error: Component '{new_name}' already exists", file=sys.stderr)
        return 1

    try:
        component_path.rename(new_path)
        print(f"Component reordered: {name} -> {new_name}")
        return 0
    except OSError as e:
        print(f"Error renaming component: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cmp",
        description="Component management script for Neutral TS Starter Py.",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Available commands",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List components",
        description="List all, enabled, or disabled components.",
    )
    list_parser.add_argument(
        "filter",
        nargs="?",
        choices=["all", "enabled", "disabled"],
        default="all",
        help="Filter by status: all, enabled, or disabled (default: all)",
    )
    list_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed component information",
    )
    list_parser.set_defaults(func=cmd_list)

    # Enable command
    enable_parser = subparsers.add_parser(
        "enable",
        help="Enable a disabled component",
        description="Enable a disabled component by renaming from _cmp_ to cmp_.",
    )
    enable_parser.add_argument(
        "component",
        help="Component name to enable (e.g., hellocomp, 7000_hellocomp, cmp_7000_hellocomp)",
    )
    enable_parser.set_defaults(func=cmd_enable)

    # Disable command
    disable_parser = subparsers.add_parser(
        "disable",
        help="Disable an enabled component",
        description="Disable an enabled component by renaming from cmp_ to _cmp_.",
    )
    disable_parser.add_argument(
        "component",
        help="Component name to disable (e.g., hellocomp, 7000_hellocomp, cmp_7000_hellocomp)",
    )
    disable_parser.set_defaults(func=cmd_disable)

    # Reorder command
    reorder_parser = subparsers.add_parser(
        "reorder",
        help="Change component load order",
        description="Change the load order of a component by renaming its number prefix.",
    )
    reorder_parser.add_argument(
        "component",
        help="Component name to reorder (e.g., hellocomp, 7000_hellocomp)",
    )
    reorder_parser.add_argument(
        "order",
        help="New order number (0000-9999)",
    )
    reorder_parser.set_defaults(func=cmd_reorder)

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
