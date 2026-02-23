#!/usr/bin/env sh

set -eu

REPO_URL="https://github.com/FranBarInstance/neutral-starter-py.git"
FALLBACK_DEFAULT_BRANCH="main"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command not found: $1" >&2
    exit 1
  fi
}

prompt_default() {
  prompt_text="$1"
  default_value="$2"
  printf "%s [%s]: " "$prompt_text" "$default_value" >&2
  if [ -r /dev/tty ]; then
    read -r value </dev/tty || true
  else
    read -r value || true
  fi
  if [ -z "${value:-}" ]; then
    printf "%s" "$default_value"
  else
    printf "%s" "$value"
  fi
}

set_env_value() {
  env_file="$1"
  key="$2"
  value="$3"

  tmp_file="$(mktemp)"
  awk -v key="$key" -v value="$value" '
    BEGIN { done = 0 }
    $0 ~ ("^" key "=") {
      print key "=" value
      done = 1
      next
    }
    { print }
    END {
      if (!done) {
        print key "=" value
      }
    }
  ' "$env_file" > "$tmp_file"
  mv "$tmp_file" "$env_file"
}

read_password() {
  prompt_text="$1"
  if [ -r /dev/tty ]; then
    stty -echo </dev/tty
    printf "%s" "$prompt_text" >&2
    read -r value </dev/tty || true
    stty echo </dev/tty
    printf "\n" >&2
  elif [ -t 0 ]; then
    stty -echo
    printf "%s" "$prompt_text" >&2
    read -r value || true
    stty echo
    printf "\n" >&2
  else
    printf "%s" "$prompt_text" >&2
    read -r value || true
  fi
  printf "%s" "${value:-}"
}

need_cmd git
need_cmd python3

DEFAULT_BRANCH="$(git ls-remote --symref "$REPO_URL" HEAD 2>/dev/null | awk '/^ref:/ { sub("refs/heads/", "", $2); print $2; exit }')"
if [ -z "$DEFAULT_BRANCH" ]; then
  DEFAULT_BRANCH="$FALLBACK_DEFAULT_BRANCH"
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHON_MAJOR="$(printf "%s" "$PYTHON_VERSION" | cut -d. -f1)"
PYTHON_MINOR="$(printf "%s" "$PYTHON_VERSION" | cut -d. -f2)"
if [ "$PYTHON_MAJOR" -ne 3 ] || [ "$PYTHON_MINOR" -lt 10 ] || [ "$PYTHON_MINOR" -gt 13 ]; then
  echo "ERROR: Python 3.10 to 3.13 is required (found $PYTHON_VERSION)." >&2
  exit 1
fi

echo "Fetching latest tags from repository..."
TAG_LIST="$(git ls-remote --tags --refs "$REPO_URL" | awk '{print $2}' | sed 's#refs/tags/##' | sort -Vr | head -n 15)"

echo "Available versions:"
echo "  1) development ($DEFAULT_BRANCH latest)"
index=2
if [ -n "$TAG_LIST" ]; then
  printf "%s\n" "$TAG_LIST" | while IFS= read -r tag; do
    printf "  %s) %s\n" "$index" "$tag"
    index=$((index + 1))
  done
else
  echo "  (no tags found)"
fi

TAG_COUNT=0
if [ -n "$TAG_LIST" ]; then
  TAG_COUNT="$(printf "%s\n" "$TAG_LIST" | wc -l | tr -d ' ')"
fi
TOTAL_OPTIONS=$((TAG_COUNT + 1))
SELECTED_INDEX="$(prompt_default "Select version number" "1")"
case "$SELECTED_INDEX" in
  *[!0-9]*|"")
    echo "ERROR: invalid selection" >&2
    exit 1
    ;;
esac
if [ "$SELECTED_INDEX" -lt 1 ] || [ "$SELECTED_INDEX" -gt "$TOTAL_OPTIONS" ]; then
  echo "ERROR: selection out of range (1..$TOTAL_OPTIONS)" >&2
  exit 1
fi

if [ "$SELECTED_INDEX" -eq 1 ]; then
  SELECTED_REF="$DEFAULT_BRANCH"
  SELECTED_LABEL="development ($DEFAULT_BRANCH latest)"
else
  TAG_INDEX=$((SELECTED_INDEX - 1))
  SELECTED_REF="$(printf "%s\n" "$TAG_LIST" | sed -n "${TAG_INDEX}p")"
  SELECTED_LABEL="$SELECTED_REF"
fi

INSTALL_DIR_DEFAULT="$(pwd)"
INSTALL_DIR="$(prompt_default "Installation directory" "$INSTALL_DIR_DEFAULT")"
if [ -e "$INSTALL_DIR" ] && [ "$(ls -A "$INSTALL_DIR" 2>/dev/null || true)" ]; then
  echo "ERROR: installation directory is not empty: $INSTALL_DIR" >&2
  echo "Use an empty directory or create a new one."
  exit 1
fi
mkdir -p "$INSTALL_DIR"

echo "Cloning version '$SELECTED_LABEL' into '$INSTALL_DIR'..."
git clone --depth 1 --branch "$SELECTED_REF" "$REPO_URL" "$INSTALL_DIR"

cd "$INSTALL_DIR"

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Installing dependencies..."
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Configuring environment file..."
cp config/.env.example config/.env
SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
set_env_value "config/.env" "SECRET_KEY" "$SECRET_KEY"

echo "Generating randomized admin routes..."
ROUTE_SUFFIXES="$(python -c 'import secrets; print(secrets.token_hex(6)); print(secrets.token_hex(6))')"
ADMIN_SUFFIX="$(printf "%s\n" "$ROUTE_SUFFIXES" | sed -n '1p')"
DEV_ADMIN_SUFFIX="$(printf "%s\n" "$ROUTE_SUFFIXES" | sed -n '2p')"
ADMIN_ROUTE="/admin-$ADMIN_SUFFIX"
DEV_ADMIN_ROUTE="/dev-admin-$DEV_ADMIN_SUFFIX"

mkdir -p src/component/cmp_7040_admin src/component/cmp_7050_dev_admin
cat > src/component/cmp_7040_admin/custom.json <<EOF
{
  "manifest": {
    "route": "$ADMIN_ROUTE"
  }
}
EOF
cat > src/component/cmp_7050_dev_admin/custom.json <<EOF
{
  "manifest": {
    "route": "$DEV_ADMIN_ROUTE"
  }
}
EOF
echo "Admin route: $ADMIN_ROUTE"
echo "Dev admin route: $DEV_ADMIN_ROUTE"

echo "Bootstrapping databases..."
python bin/bootstrap_db.py

DEV_NAME="$(prompt_default "DEV user alias" "Dev Admin")"
DEV_EMAIL="$(prompt_default "DEV user email" "dev@example.com")"

DEV_PASSWORD=""
while [ "${#DEV_PASSWORD}" -lt 9 ]; do
  DEV_PASSWORD="$(read_password "DEV user password (min 9 chars): ")"
  if [ "${#DEV_PASSWORD}" -lt 9 ]; then
    echo "Password must be at least 9 characters."
  fi
done

DEV_BIRTHDATE="$(prompt_default "DEV user birthdate (YYYY-MM-DD)" "1990-01-01")"
DEV_LOCALE="$(prompt_default "DEV user locale" "es")"

echo "Creating DEV user..."
python bin/create_user.py "$DEV_NAME" "$DEV_EMAIL" "$DEV_PASSWORD" "$DEV_BIRTHDATE" --locale "$DEV_LOCALE" --role dev

set_env_value "config/.env" "DEV_ADMIN_USER" "$DEV_EMAIL"
set_env_value "config/.env" "DEV_ADMIN_PASSWORD" "$DEV_PASSWORD"
set_env_value "config/.env" "DEV_ADMIN_LOCAL_ONLY" "true"
set_env_value "config/.env" "DEV_ADMIN_ALLOWED_IPS" "127.0.0.1,::1"
echo "DEV_ADMIN_* updated in config/.env"

echo "Installation completed."
echo "Important: first sign-in may require the PIN generated for the user."
echo "Keep the PIN shown in the create_user output."
echo "Admin route created: $ADMIN_ROUTE (src/component/cmp_7040_admin/custom.json)"
echo "Dev admin route created: $DEV_ADMIN_ROUTE (src/component/cmp_7050_dev_admin/custom.json)"
echo "Project directory: $INSTALL_DIR"
echo "Run with:"
echo "  cd \"$INSTALL_DIR\" && . .venv/bin/activate && python src/run.py"
