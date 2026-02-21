# Installation Guide

This document explains how to install **Neutral TS Starter Py** using either the automatic installers or a manual setup.

## 1. Prerequisites

- Python 3.10+
- `git`
- `pip`
- Linux/macOS shell (`sh`) or Windows PowerShell (depending on your platform)

## 2. Automatic Installation (recommended)

Automatic installers are provided for:

- Linux/macOS: `bin/install.sh`
- Windows: `bin/install.ps1`

### 2.1 What the automatic installer does

- Fetches repository tags and lets you choose from the latest 15 versions.
- Asks for installation directory (current directory by default).
- Clones selected version.
- Creates `.venv`.
- Installs `requirements.txt`.
- Copies `config/.env.example` to `config/.env`.
- Generates random `SECRET_KEY`.
- Generates randomized admin routes:
  - `src/component/cmp_7060_admin/custom.json` -> `/admin-[random]`
  - `src/component/cmp_7050_dev_admin/custom.json` -> `/dev-admin-[random]`
- Runs DB bootstrap (`bin/bootstrap_db.py`).
- Creates a `dev` role user with `bin/create_user.py`.
- Writes `DEV_ADMIN_*` values to `config/.env`.

Important:
- First sign-in may require the PIN shown in `create_user.py` output. Save that PIN.
- Randomized admin routes are an additional hardening layer against opportunistic scraping/scanning. They are not a replacement for authentication/authorization/rate limiting.

### 2.2 Linux/macOS

```bash
curl -fsSL https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/master/bin/install.sh | sh
```

### 2.3 Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command "iwr -useb https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/master/bin/install.ps1 | iex"
```

## 3. Manual Installation

### 3.1 Clone repository

```bash
git clone https://github.com/FranBarInstance/neutral-starter-py.git
cd neutral-starter-py
```

### 3.2 Create virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3.3 Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3.4 Configure environment file

```bash
cp config/.env.example config/.env
```

Set `SECRET_KEY` to a strong random value before running in non-local environments.

### 3.5 (Recommended) Generate randomized admin routes

Create:

- `src/component/cmp_7060_admin/custom.json`
- `src/component/cmp_7050_dev_admin/custom.json`

Example:

```json
{
  "manifest": {
    "route": "/admin-r4nd0m12ab34"
  }
}
```

For `cmp_7050_dev_admin` use `/dev-admin-[random]`.

### 3.6 Bootstrap databases

```bash
python bin/bootstrap_db.py
```

### 3.7 Create initial dev/admin user

```bash
python bin/create_user.py "Dev Admin" "dev@example.com" "your-password" "1990-01-01" --locale es --role dev
```

Then update in `config/.env`:

- `DEV_ADMIN_USER=dev@example.com`
- `DEV_ADMIN_PASSWORD=your-password`
- `DEV_ADMIN_LOCAL_ONLY=true`
- `DEV_ADMIN_ALLOWED_IPS=127.0.0.1,::1`

### 3.8 Run application

```bash
python src/run.py
```

Default URL: `http://localhost:5000`

## 4. `config/.env` Variables to Configure

This section focuses on the most relevant variables from `config/.env.example`.

### 4.1 Minimum required

- `SECRET_KEY`: Required. Use a long random value.
- `SITE_DOMAIN`: Domain used by app/security flows.
- `SITE_URL`: Public base URL (include scheme).
- `ALLOWED_HOSTS`: Host allow-list.

### 4.2 Strongly recommended for real deployments

- `TRUSTED_PROXY_CIDRS`: Trusted reverse proxy ranges (if behind proxy/load balancer).
- `CONFIG_DB_PATH`: Optional path for central component overrides.
- `DEV_ADMIN_USER`
- `DEV_ADMIN_PASSWORD`
- `DEV_ADMIN_LOCAL_ONLY`
- `DEV_ADMIN_ALLOWED_IPS`
- `LIMITER_STORAGE_URI`: Use shared backend (for example Redis) in multi-instance deployments.
- `DEFAULT_LIMITS`, `SIGNIN_LIMITS`, `SIGNUP_LIMITS`: Review anti-abuse thresholds.
- `VALIDATE_SIGNUP`: Enable if you require validated signup flow.

### 4.3 Database variables

For each DB group (`PWA`, `SAFE`, `FILES`):

- `DB_*_TYPE` (`sqlite`, `postgresql`, `mysql`, `mariadb`)
- `DB_*_NAME`
- `DB_*_USER`
- `DB_*_PASSWORD`
- `DB_*_HOST`
- `DB_*_PORT`
- `DB_*_PATH` (used for sqlite file location)

If using SQLite, validate filesystem permissions for DB paths.

### 4.4 Mail variables (if email flows are used)

- `MAIL_METHOD` (`smtp`, `sendmail`, or `file`)
- `MAIL_TO_FILE` (when `MAIL_METHOD=file`)
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_SENDER`
- `MAIL_RETURN_PATH`

### 4.5 Security and policy variables

- `REFERRER_POLICY`
- `PERMISSIONS_POLICY`
- `CSP_ALLOWED_SCRIPT`
- `CSP_ALLOWED_STYLE`
- `CSP_ALLOWED_IMG`
- `CSP_ALLOWED_FONT`
- `CSP_ALLOWED_CONNECT`
- `CSP_ALLOWED_FRAME`
- `CSP_ALLOWED_SCRIPT_UNSAFE_INLINE`
- `CSP_ALLOWED_SCRIPT_UNSAFE_EVAL`
- `CSP_ALLOWED_STYLE_UNSAFE_INLINE`

Keep unsafe CSP flags disabled unless strictly necessary.

### 4.6 Debug/development toggles

- `DEBUG_EXPIRE`
- `DEBUG_FILE`
- `WSGI_DEBUG_ALLOWED`
- `AUTO_BOOTSTRAP_DB`
- `NEUTRAL_CACHE_DISABLE`
- `TEMPLATE_HTML_MINIFY`

For production, keep debug-related flags disabled.

## 5. Post-installation Checklist

- Confirm app starts and serves `SITE_URL`.
- Confirm DB files or DB connections are valid.
- Confirm `DEV_ADMIN_*` is set and login works.
- Save/store first-login PIN if signup validation/unconfirmed flow applies.
- Review CSP and host/proxy settings before exposing publicly.
