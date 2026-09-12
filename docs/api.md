# API Reference

Base URL: `http://localhost:8000`  
Documentación interactiva: `http://localhost:8000/docs`

## Health

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Estado general `{name, status}` |
| GET | `/health` | Health check |

## Projects

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/projects/` | Lista todos los proyectos |
| GET | `/projects/{id}` | Obtiene un proyecto |
| POST | `/projects/` | Crea un proyecto (ver body abajo) |
| DELETE | `/projects/{id}` | Elimina un proyecto |
| POST | `/projects/{id}/clone` | Clona un proyecto existente (ver body abajo) |
| POST | `/projects/{id}/compose/up` | Levanta el stack del proyecto |
| POST | `/projects/{id}/compose/down` | Baja el stack del proyecto (timeout 3s) |
| POST | `/projects/{id}/compose/restart` | Reinicia el stack |
| GET | `/projects/{id}/compose/logs?tail=200` | Logs del stack |
| GET | `/projects/{id}/compose/status` | Estado crudo (`docker compose ps --format json`) |
| GET | `/projects/{id}/stack-status` | Estado simplificado: `running` / `partial` / `stopped` / `no_compose` — el que alimenta el LED de la card |
| GET | `/projects/{id}/compose/run` | Devuelve el comando `docker compose run --rm <servicio>` ya resuelto (no lo ejecuta) |

### POST /projects/ — body

```json
{
  "id": "mi-proyecto",
  "name": "Mi Proyecto",
  "description": "opcional",
  "template": "esp32",
  "path": "/projects/ruta-custom",
  "device": "/dev/ttyUSB0",
  "framework": "freertos",
  "arch": "xtensa",
  "microros": true
}
```

El backend completa: `path` (si no se especifica), `version`, `created`, `applications`, `agents`, `tags`.  
El `path` debe estar dentro de `CLAUBOARD_PROJECTS_DIR` — rutas fuera dan 400.  
`device`, `framework`, `arch`, `microros` son opcionales y se ignoran silenciosamente si el template no los usa. Ver `docs/architecture.md` para qué combinaciones son válidas por chip.

### POST /projects/{id}/clone — body

```json
{
  "new_id": "mi-proyecto-v2",
  "new_name": "Mi Proyecto v2",
  "new_path": "/projects/ruta-opcional"
}
```

Copia la carpeta completa del proyecto origen y reinicializa git (sin el historial del original).

## Templates (type: toolchain)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/templates` | Lista toolchains disponibles con status real |
| GET | `/templates/{id}/frameworks` | Opciones de framework/arquitectura/microros para ese template (`{}` si no aplica) |

Los toolchains no se instalan como contenedores persistentes desde `/applications` — se usan vía `docker compose run --rm` (ver `/projects/{id}/compose/run`).

## Applications (type: service)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/applications` | Lista apps tipo `service` con status real |
| GET | `/applications/{id}` | Obtiene una app |
| POST | `/applications/{id}/install` | Instala (crea el contenedor) |
| GET | `/applications/{id}/install/progress` | Stream SSE con progreso del `docker pull` (MB, porcentaje) |
| POST | `/applications/{id}/start` | Arranca el contenedor (auto-reconecta a `clauboard-net` si quedó huérfano) |
| POST | `/applications/{id}/stop` | Detiene el contenedor |
| POST | `/applications/{id}/restart` | Reinicia el contenedor |
| DELETE | `/applications/{id}` | Desinstala (elimina el contenedor) |

Los toolchains (`type: toolchain`) y la infraestructura (`type: infrastructure`) devuelven 400 si se intenta instalar/desinstalar desde estos endpoints.

## Infrastructure (type: infrastructure)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/infrastructure` | Lista servicios de infra con status real |

Start/Stop/Restart se hacen desde el dashboard (reutiliza los endpoints de `/applications/{id}/...`) pero no Install/Uninstall — los servicios de infra los gestiona `infra/compose.yml`.

## Plugins

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/plugins` | Lista plugins disponibles (manifests) |

## Agents

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/agents` | Lista agentes (stub, retorna `[]` — pendiente de definir alcance real) |

## Códigos de error

| Código | Cuándo |
|---|---|
| 400 | Argumento inválido (ruta fuera de límites, operación no permitida para ese tipo) |
| 404 | App o proyecto no encontrado |
| 409 | Proyecto/id ya existe |
| 500 | Error de Docker (ver logs del backend) |