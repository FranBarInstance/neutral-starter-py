# Bin Scripts

This directory contains operational project scripts (support tasks, maintenance, and development utilities).

## General Rule

- Always use the local `.venv` virtual environment for any Python script.
- Recommended base command:

```bash
source .venv/bin/activate && python bin/<script>.py
```

On Windows:

```bat
.venv\Scripts\python.exe bin\<script>.py
```

## Available Scripts

### `create_user.py`

Creates a user in the database using the project's internal logic (`core.user.User.create`).

Usage:

```bash
source .venv/bin/activate && python bin/create_user.py "Nombre" "email@dominio.com" "password" "1990-05-20"
```

Optional arguments:

- `--locale` (default: `es`)
- `--region`
- `--properties` (JSON)

Example:

```bash
source .venv/bin/activate && python bin/create_user.py "Ana" "ana@example.com" "MiPass123!" "1992-11-03" --locale es --region ES --properties "{\"role\":\"admin\"}"
```

### `bootstrap_db.py`

Initializes the base database schema for a clean installation.

Includes:
- `pwa`: `uid`, `user*`, `pin`, `role`, `user_role` tables + base roles.
- `safe`: `session` table.
- `files`: database connection/creation check.

Basic usage:

```bash
source .venv/bin/activate && python bin/bootstrap_db.py
```

With custom URLs (recommended for local testing):

```bash
source .venv/bin/activate && python bin/bootstrap_db.py \
  --db-pwa-url sqlite:////tmp/neutral-install/pwa.db \
  --db-safe-url sqlite:////tmp/neutral-install/safe.db \
  --db-files-url sqlite:////tmp/neutral-install/files.db
```

### `install.sh` (Linux/macOS)

Interactive installer for a clean installation from a repository version.

Includes:
- option to install the current development version (repository default branch, auto-detected; fallback `main`)
- list of up to 15 tags and version selection
- destination directory selection
- `.venv` creation + `requirements.txt` installation
- copy from `config/.env.example` to `config/.env` + `SECRET_KEY` generation
- automatic generation of randomized routes in:
  - `src/component/cmp_7040_admin/custom.json` -> `/admin-[random]`
  - `src/component/cmp_7050_dev_admin/custom.json` -> `/dev-admin-[random]`
- `bootstrap_db.py`
- required creation of `dev` user (prompts for data) and update of `DEV_ADMIN_*` in `.env`

Remote usage:

```bash
curl -fsSL https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/main/bin/install.sh | sh
```

### `install.ps1` (Windows PowerShell)

Equivalent interactive installer for Windows.

Remote usage:

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command "iwr -useb https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/main/bin/install.ps1 | iex"
```

## Convention for Future Scripts

- Name: `snake_case.py` (example: `sync_data.py`).
- Single Python entry point (without `.sh`/`.bat` wrappers, unless truly needed).
- Arguments with `argparse` and `--help`.
- Validate inputs and return clear exit codes:
  - `0`: OK
  - `1`: execution error
  - `2`: argument error
- Keep scripts idempotent whenever possible.
