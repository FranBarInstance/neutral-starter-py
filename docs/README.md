# Documentation Index

## Overview

**Neutral PWA Starter** is a modular, security-focused boilerplate for building Progressive Web Applications. It utilizes **Python (Flask)** for the backend and the **[Neutral TS](https://github.com/FranBarInstance/neutralts)**  for the frontend—a language-agnostic, logic-less templating engine.

Key features include:
- **Component-Based Architecture**: Everything is isolated and modular, allowing for easy extension and overrides.
- **Declarative SQL**: Database queries are defined in JSON files, keeping the Python codebase clean and ensuring database portability.
- **Security-First Design**: Built-in CSRF protection (UTOKEN/LTOKEN), secure-by-default templating, and strict Content Security Policy (CSP) integration.
- **Modular Frontend**: Powerful snippet-based rendering system for dynamic route content.

---

## Document Index

The following documents provide detailed information about the system:

- **[README.md](README.md)**: This index and project overview.
- **[development.md](development.md)**: **The main developer guide.** Explains the high-level architecture, project structure, core concepts, and essential development workflows.
- **[component.md](component.md)**: Deep dive into the **Component System**. Covers naming conventions, file structure, lifecycle, and priority/overriding rules.
- **[model.md](model.md)**: Documentation for the **Data Model layer**. Explains how to define and use SQL queries via JSON files and the central Model executor.
- **[templates-neutrats.md](templates-neutrats.md)**: Comprehensive syntax reference for the **Neutral Template Engine (NTPL)**, including variables, control flow, snippets, and safety features.
