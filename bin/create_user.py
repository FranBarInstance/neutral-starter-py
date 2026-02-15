#!/usr/bin/env python3
"""Cross-platform CLI to create users in the project database."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def _bootstrap_path() -> None:
    """Ensure project src/ is importable when script is run from bin/."""
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a user in Neutral Starter Py."
    )
    parser.add_argument("name", help="User display name (alias).")
    parser.add_argument("email", help="User email.")
    parser.add_argument("password", help="User password.")
    parser.add_argument(
        "birthdate",
        help="Birthdate in ISO format, for example: 1990-05-20 or 1990-05-20T00:00:00",
    )
    parser.add_argument(
        "--locale",
        default="es",
        help="User locale, default: es",
    )
    parser.add_argument(
        "--region",
        default="",
        help="Optional region value.",
    )
    parser.add_argument(
        "--properties",
        default="{}",
        help="Optional JSON text stored in user profile properties.",
    )
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if not args.name.strip():
        raise ValueError("name cannot be empty")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", args.email.strip()):
        raise ValueError("email format is invalid")
    if not args.password.strip():
        raise ValueError("password cannot be empty")

    try:
        datetime.fromisoformat(args.birthdate)
    except ValueError as exc:
        raise ValueError("birthdate must be valid ISO format") from exc

    if args.properties:
        try:
            json.loads(args.properties)
        except json.JSONDecodeError as exc:
            raise ValueError("properties must be valid JSON text") from exc


def main() -> int:
    _bootstrap_path()
    from core.user import User  # pylint: disable=import-error,import-outside-toplevel

    parser = _build_parser()
    args = parser.parse_args()

    try:
        _validate_args(args)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    user_data = {
        "alias": args.name.strip(),
        "email": args.email.strip(),
        "password": args.password,
        "birthdate": args.birthdate,
        "locale": args.locale.strip() or "es",
        "region": args.region.strip(),
        "properties": args.properties.strip() or "{}",
    }

    result = User().create(user_data)
    if not result.get("success"):
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
