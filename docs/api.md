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
| POST | `/projects/{id}/compose/up` | Levanta el stack del proyecto |
| POST | `/projects/{id}/compose/down` | Baja el stack del proyecto |
| POST | `/projects/{id}/compose/restart` | Reinicia el stack |
| GET | `/projects/{id}/compose/logs?tail=200` | Logs del stack |
| GET | `/projects/{id}/compose/status` | Estado de los contenedores |

### POST /projects/ — body

```json
{
  "id": "mi-proyecto",
  "name": "Mi Proyecto",
  "description": "opcional",
  "template": "esp32",
  "path": "/projects/ruta-custom"
}
```

El backend completa: `path` (si no se especifica), `version`, `created`, `applications`, `agents`, `tags`.  
El `path` debe estar dentro de `CLAUBOARD_PROJECTS_DIR` — rutas fuera dan 400.

## Applications (type: service)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/applications` | Lista apps tipo `service` con status real |
| GET | `/applications/{id}` | Obtiene una app |
| POST | `/applications/{id}/install` | Instala (crea el contenedor) |
| POST | `/applications/{id}/start` | Arranca el contenedor |
| POST | `/applications/{id}/stop` | Detiene el contenedor |
| POST | `/applications/{id}/restart` | Reinicia el contenedor |
| DELETE | `/applications/{id}` | Desinstala (elimina el contenedor) |

Los toolchains (`type: toolchain`) y la infraestructura (`type: infrastructure`) devuelven 400 si se intenta instalar/desinstalar desde estos endpoints.

## Templates (type: toolchain)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/templates` | Lista toolchains disponibles con status real |

Solo informativo — los toolchains no se instalan como contenedores persistentes. Se usan via `docker compose run --rm` desde el directorio del proyecto.

## Infrastructure (type: infrastructure)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/infrastructure` | Lista servicios de infra con status real |

Start/Stop/Restart se hacen desde el dashboard pero no Install/Uninstall — los servicios de infra los gestiona `infra/compose.yml`.

## Plugins

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/plugins` | Lista plugins disponibles (manifests) |

## Agents

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/agents` | Lista agentes (stub, retorna `[]` por ahora) |

## Códigos de error

| Código | Cuándo |
|---|---|
| 400 | Argumento inválido (ruta fuera de límites, operación no permitida para ese tipo) |
| 404 | App o proyecto no encontrado |
| 409 | Proyecto ya existe |
| 500 | Error de Docker (ver logs del backend) |