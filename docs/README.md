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
- **[component-quickstart.md](component-quickstart.md)**: Practical **0-to-working-component** guide with the minimal steps to create, route, render, and test a new component.
- **[model.md](model.md)**: Documentation for the **Data Model layer**. Explains how to define and use SQL queries via JSON files and the central Model executor.
- **[templates-neutrats.md](templates-neutrats.md)**: Comprehensive syntax reference for the **Neutral Template Engine (NTPL)**, including variables, control flow, snippets, and safety features.
- **[dispatcher.md](dispatcher.md)**: Documentation for the **Dispatcher** system.
- **[ajax-neutral-requests.md](ajax-neutral-requests.md)**: Integration notes for AJAX requests and `Requested-With-Ajax`, including behavior when using Neutral fetch vs custom JavaScript.
- **[translation-component.md](translation-component.md)**: Translation workflow for components, including `{:trans; ... :}` best practices, locale file strategy, and the `translate-component` skill.
- **[security-csp.md](security-csp.md)**: Security guide for CSP, security headers, host allow-list validation, and trusted proxy boundaries.
