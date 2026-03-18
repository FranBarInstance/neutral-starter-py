## Mandatory Python Virtual Environment
- Before running any Python-related command (`python`, `pip`, `pytest`, `pylint`, `mypy`, `ruff`, etc.), always activate the local virtual environment.
- Use the single-shell form:
  `source .venv/bin/activate && <command>`
- Do not use global/system Python tools when `.venv` is available.
- For linting, prefer:
  `source .venv/bin/activate && python -m pylint <paths>`
- Check the `.agent/skills/` directory for available skills.
