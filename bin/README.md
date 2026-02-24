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
- `--role` - can be repeated to assign multiple roles
- `--roles` - comma-separated role codes

Example:

```bash
source .venv/bin/activate && python bin/create_user.py "Ana" "ana@example.com" "MiPass123!" "1992-11-03" --locale es --region ES --role admin --role editor
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

Optional arguments:

- `--db-pwa-url` - override DB_PWA URL
- `--db-pwa-type` - override DB_PWA type
- `--db-safe-url` - override DB_SAFE URL
- `--db-safe-type` - override DB_SAFE type
- `--db-files-url` - override DB_FILES URL
- `--db-files-type` - override DB_FILES type
- `--quiet` - print only errors

With custom URLs (recommended for local testing):

```bash
source .venv/bin/activate && python bin/bootstrap_db.py \
  --db-pwa-url sqlite:////tmp/neutral-install/pwa.db \
  --db-safe-url sqlite:////tmp/neutral-install/safe.db \
  --db-files-url sqlite:////tmp/neutral-install/files.db
```

### `cmp.py` (Component Management)

Manages project components: list, enable, disable, and reorder.

**Wrapper scripts available:**
- `bin/cmp` (Linux/macOS) - activates venv automatically
- `bin/cmp.bat` (Windows) - activates venv automatically

**Commands:**

```bash
# List components
./bin/cmp list [all|enabled|disabled] [-v]

# Enable a disabled component
./bin/cmp enable <name>

# Disable an enabled component
./bin/cmp disable <name>

# Change component load order
./bin/cmp reorder <name> <order>
```

**Component name formats accepted:**
- Full name: `cmp_7000_hellocomp`
- Without prefix: `7000_hellocomp`
- Just the name: `hellocomp`

**Examples:**

```bash
# List all components
./bin/cmp list

# List only disabled components with details
./bin/cmp list disabled -v

# Enable a component
./bin/cmp enable aichat

# Disable a component
./bin/cmp disable hellocomp

# Change component order from 7000 to 7100
./bin/cmp reorder hellocomp 7100
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
