#!/bin/bash

# Exit codes:
#   0 — no issues found
#   1 — one or more WARNINGs detected (agent must stop and ask the user)

STAGED_FILES=$(git diff --cached --name-only)

if [ -z "$STAGED_FILES" ]; then
    echo "No files staged for commit."
    exit 0
fi

# 1. Patterns for file names
SENSITIVE_FILE_PATTERNS=(".env" "\.pem$" "\.key$" "\.cert$" "\.p12$" "id_rsa" "\.sqlite" "\.db$" "secret" "token" "credential")

# 2. Patterns for absolute paths
ABSOLUTE_PATH_PATTERN="/home/|/Users/|/etc/|/var/|C:\\\\"

# 3. Patterns for secrets WITHIN the code
# Looks for: password=..., API_KEY's, JWT Tokens, AWS Keys
SENSITIVE_CONTENT_PATTERN="password[[:space:]]*=|api[_-]?key[[:space:]]*=|secret[_-]?key[[:space:]]*=|AKIA[0-9A-Z]{16}|Bearer[[:space:]]+eyJ"

echo "Running safety checks on staged files..."
WARNINGS=0

for FILE in $STAGED_FILES; do
    # Validate that the file exists (it might have been deleted in the commit)
    if [ ! -f "$FILE" ]; then
        continue
    fi

    # Check 1: Sensitive file names
    for PATTERN in "${SENSITIVE_FILE_PATTERNS[@]}"; do
        if echo "$FILE" | grep -iqE "$PATTERN"; then
            echo "🔴 WARNING: Sensitive file name detected: $FILE (matched: $PATTERN)"
            WARNINGS=$((WARNINGS + 1))
        fi
    done

    # Check 2: Absolute paths (ignore binaries with -I)
    if grep -IqE "$ABSOLUTE_PATH_PATTERN" "$FILE"; then
        echo "🟡 WARNING: Potential absolute path detected in $FILE"
        grep -InE "$ABSOLUTE_PATH_PATTERN" "$FILE" | head -n 3
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check 3: Secrets in content (ignore binaries with -I)
    if grep -IqE "$SENSITIVE_CONTENT_PATTERN" "$FILE"; then
        echo "🔴 WARNING: Potential hardcoded secret or credential detected in $FILE"
        # Show the line (optionally obfuscate secrets visually if needed)
        grep -InE "$SENSITIVE_CONTENT_PATTERN" "$FILE" | head -n 3
        WARNINGS=$((WARNINGS + 1))
    fi
done

if [ "$WARNINGS" -gt 0 ]; then
    echo "❌ Safety check failed with $WARNINGS warnings. Please review the output above."
    exit 1
fi

echo "✅ Checks completed. No issues found."
exit 0
