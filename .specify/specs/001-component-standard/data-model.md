# Component Data Model

## Encapsulated Persistence

Each component is responsible for its own data schema and persistence
operations.

## Data Patterns

- **JSON definitions:** SQL queries must live in
  `cmp_NNNN_name/model/*.json`.
- **Dialects:** Provide query variants for supported engines
  (`@sqlite`, `@postgresql`, `@mysql`) or use `@portable` for standard SQL.
- **Transactions:** Complex operations should be defined as arrays of
  statements in JSON for atomic execution.

## Interaction with the Core

- **ID generation:** Use the global core UID system
  (`app.json` -> `uid-create`) to guarantee distributed unique identifiers.
- **Dynamic configuration:** A component may use the `custom` table in the
  configuration database to persist dynamic state or overrides.

## Implementation Rules

1. **No SQL in code:** Embedded SQL strings in `.py` files are forbidden.
2. **Explicit loading:** Component model files must be invoked explicitly via
   `model.exec(..., model_dir=component_path)`.
3. **Migrations:** The component must be able to initialize its own tables
   through a `setup` operation called during `init_component`.
