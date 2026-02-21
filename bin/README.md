# Bin Scripts

Este directorio contiene scripts operativos del proyecto (tareas de soporte, mantenimiento y utilidades de desarrollo).

## Regla general

- Usar siempre el entorno virtual local `.venv` para cualquier script Python.
- Comando base recomendado:

```bash
source .venv/bin/activate && python bin/<script>.py
```

En Windows:

```bat
.venv\Scripts\python.exe bin\<script>.py
```

## Script disponible

### `create_user.py`

Crea un usuario en la base de datos usando la lógica interna del proyecto (`core.user.User.create`).

Uso:

```bash
source .venv/bin/activate && python bin/create_user.py "Nombre" "email@dominio.com" "password" "1990-05-20"
```

Opcionales:

- `--locale` (default: `es`)
- `--region`
- `--properties` (JSON)

Ejemplo:

```bash
source .venv/bin/activate && python bin/create_user.py "Ana" "ana@example.com" "MiPass123!" "1992-11-03" --locale es --region ES --properties "{\"role\":\"admin\"}"
```

### `bootstrap_db.py`

Inicializa el esquema base de bases de datos para una instalacion limpia.

Incluye:
- `pwa`: tablas `uid`, `user*`, `pin`, `role`, `user_role` + roles base.
- `safe`: tabla `session`.
- `files`: prueba de conexion/creacion de la base.

Uso basico:

```bash
source .venv/bin/activate && python bin/bootstrap_db.py
```

Con URLs custom (recomendado para pruebas locales):

```bash
source .venv/bin/activate && python bin/bootstrap_db.py \
  --db-pwa-url sqlite:////tmp/neutral-install/pwa.db \
  --db-safe-url sqlite:////tmp/neutral-install/safe.db \
  --db-files-url sqlite:////tmp/neutral-install/files.db
```

## Convención para futuros scripts

- Nombre: `snake_case.py` (ejemplo: `sync_data.py`).
- Entrada única por Python (sin wrappers `.sh`/`.bat`, salvo necesidad real).
- Argumentos con `argparse` y `--help`.
- Validar entradas y devolver códigos de salida claros:
  - `0`: OK
  - `1`: error de ejecución
  - `2`: error de argumentos
- Mantener scripts idempotentes cuando sea posible.
