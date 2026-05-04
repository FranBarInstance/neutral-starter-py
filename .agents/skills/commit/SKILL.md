---
name: commit
description: Group changes into semantic commits following repository standards.
---

# Semantic Commit Only

This skill guides you through the process of grouping current changes into meaningful semantic commits.

## Rules and Constraints

- **Explicit Request**: Only perform commits when the user explicitly indicates it.
- **Full Repository Inspection**: Before proposing any commit, inspect the current state:
  - `git status --short`
  - `git diff --stat`
  - `git diff`
  - `git log --oneline -10`
- **Semantic Grouping**: Identify related file groups by intent:
  - `feat`: New features
  - `fix`: Bug fixes
  - `refactor`: Code changes that neither fix a bug nor add a feature
  - `docs`: Documentation only changes
  - `test`: Adding missing tests or correcting existing tests
  - `chore`: Changes to the build process or auxiliary tools and libraries
  - `perf`: Code changes that improve performance
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
  - `ci`: Changes to CI configuration files and scripts
- **Independence**: Create multiple commits when there are independent changes. Do not mix unrelated changes in the same commit.
- **Contextual Messages**: Use the user's prompt and conversation context to adjust commit messages, but ensure they accurately describe the changes.
- **Excluded Directories**: Ensure no files from `tmp/`, `.venv/`, or `__pycache__/` are ever staged or committed.
- **Security Check**: Before committing, check for sensitive or suspicious files (`.env`, tokens, credentials, keys, secrets). **Stop and ask if any are found.**
- **Absolute Path Check**: Ensure all paths are relative to the repository. **Never include absolute system paths** (e.g., `/home/user/...`).
- **Safety Script**: Run `.agents/skills/commit/scripts/check_commit_safety.sh` after staging each group. The script uses exit codes: **`exit 0`** means no issues; **`exit 1`** means warnings were found. Check the exit code — do **not** rely on parsing stdout.
- **Intentional False Positives**: The safety script is intentionally strict and does **not** support automated exceptions (white-lists), as this could lead to security gaps. Expect false positives in documentation, component names (e.g., `ftoken`), or security logic. If a warning occurs, you **must** analyze the output, explain why it is a false positive, and wait for explicit human validation before proceeding.
- **No Side Effects**: 
  - Do NOT use `--no-verify`.
  - Do NOT amend commits.
  - Do NOT revert existing changes.
- **Push Policy**: Do **NOT** perform `git push` unless specifically requested by the user in a separate turn. This skill is only for committing.

## Workflow

1.  **Analyze**: Run the inspection commands mentioned above to understand the pending changes.
2.  **Propose Plan**: Present a plan to the user showing:
    - The proposed commits.
    - The files included in each commit.
    - The proposed commit message for each.
3.  **Validate**: Wait for user confirmation. If there is ambiguity, ask for clarification.
4.  **Execute Commits**: For each group:
    - Add only the specific files (avoid `git add .`): `git add <files>`
    - Verify staged files: `git status`
    - Run safety script: `bash .agents/skills/commit/scripts/check_commit_safety.sh`
    - If the script **exits with code 1**, **stop immediately, analyze the output for false positives, and show them to the user**. Do not proceed or commit without explicit user confirmation that the warnings are safe to ignore.
    - Create the commit: `git commit -m "<type>(<scope>): <subject>"`
5.  **Summarize**: Provide a summary of the commits created.

## Best Practices

- Use the imperative mood in the subject line (e.g., "add feature" instead of "added feature").
- Keep the first line short (under 50 characters if possible).
- Use component names (e.g., `cmp_0200_mail`), `core`, `config`, or `docs` as scopes when applicable.
- If no specific scope applies, use the format `<type>: <subject>` (omit the parentheses).
- Use the repository's existing commit style as a reference.
