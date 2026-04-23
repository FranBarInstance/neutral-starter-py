#!/usr/bin/env python3
"""Bootstrap core databases for a clean installation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Create or update DB schema required by Neutral Starter Py.",
    )
    parser.add_argument("--db-pwa-url", default=None, help="Override DB_PWA URL")
    parser.add_argument("--db-pwa-type", default=None, help="Override DB_PWA type")
    parser.add_argument("--db-safe-url", default=None, help="Override DB_SAFE URL")
    parser.add_argument("--db-safe-type", default=None, help="Override DB_SAFE type")
    parser.add_argument("--db-image-url", default=None, help="Override DB_IMAGE URL")
    parser.add_argument("--db-image-type", default=None, help="Override DB_IMAGE type")
    parser.add_argument("--quiet", action="store_true", help="Print only errors")
    return parser


def _log(message: str, quiet: bool) -> None:
    if not quiet:
        print(message)


def main() -> int:
    _bootstrap_path()

    from app.bootstrap_db import (  # pylint: disable=import-error,import-outside-toplevel
        bootstrap_databases,
    )
    from app.config import Config  # pylint: disable=import-error,import-outside-toplevel

    parser = _build_parser()
    args = parser.parse_args()

    db_pwa_url = args.db_pwa_url or Config.DB_PWA
    db_pwa_type = (args.db_pwa_type or Config.DB_PWA_TYPE).lower()
    db_safe_url = args.db_safe_url or Config.DB_SAFE
    db_safe_type = (args.db_safe_type or Config.DB_SAFE_TYPE).lower()
    db_image_url = args.db_image_url or Config.DB_IMAGE
    db_image_type = (args.db_image_type or Config.DB_IMAGE_TYPE).lower()

    try:
        _log("[pwa] setup app/user/rbac schema + seed roles", args.quiet)
        _log("[safe] setup session schema", args.quiet)
        _log("[image] setup image schema", args.quiet)
        bootstrap_databases(
            db_pwa_url=db_pwa_url,
            db_pwa_type=db_pwa_type,
            db_safe_url=db_safe_url,
            db_safe_type=db_safe_type,
            db_image_url=db_image_url,
            db_image_type=db_image_type,
        )

        _log("bootstrap_db completed", args.quiet)
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
