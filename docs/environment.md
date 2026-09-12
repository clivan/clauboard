# Variables de entorno

Dos archivos `.env` separados, cada uno con su propio `.env.example`
versionado en git — los `.env` reales **nunca se commitean** (están
en `.gitignore`).

## `.env` (raíz del repo) — stack principal

Usado por `compose.yml` (proxy, backend, frontend).

| Variable | Default si se omite | Descripción |
|---|---|---|
| `CLAUBOARD_PROJECTS_DIR` | `./clauboard-projects` (dentro del repo) | Carpeta del host donde se crean los proyectos. Puede apuntar a cualquier ruta absoluta (ej. `/home/claudio/Documentos/Proyectos`) — se monta en `/projects` dentro del backend. |

```bash
cp .env.example .env
nano .env
```

## `infra/.env` — infraestructura compartida

Usado por `infra/compose.yml` (Postgres, MongoDB, InfluxDB, Redis, MinIO, Grafana, Prometheus, cAdvisor, node-exporter). Ninguna tiene default de contraseña — todas son obligatorias (el compose falla explícitamente con `:?define ... en .env` si falta alguna, en vez de arrancar con credenciales vacías).

### Postgres

| Variable | Descripción |
|---|---|
| `POSTGRES_ADMIN_USER` | Usuario admin (default `clauboard_admin` si se omite) |
| `POSTGRES_ADMIN_PASSWORD` | **Obligatoria.** Ver `infra/postgres/init/README.md` para crear DBs/usuarios por proyecto |

### MongoDB

| Variable | Descripción |
|---|---|
| `MONGO_ADMIN_USER` | Usuario admin (default `clauboard_admin`) |
| `MONGO_ADMIN_PASSWORD` | **Obligatoria** |

### InfluxDB

| Variable | Descripción |
|---|---|
| `INFLUXDB_ADMIN_USER` | Usuario admin (default `clauboard_admin`) |
| `INFLUXDB_ADMIN_PASSWORD` | **Obligatoria** |
| `INFLUXDB_INIT_ORG` | Organización inicial (default `clauboard`) |
| `INFLUXDB_INIT_BUCKET` | Bucket inicial (default `default`) |
| `INFLUXDB_ADMIN_TOKEN` | **Obligatorio.** Token de API — genera uno con `openssl rand -hex 32`. No reutilizar como token de proyecto individual (ver README de postgres/init, mismo principio aplica) |

### Redis

| Variable | Descripción |
|---|---|
| `REDIS_PASSWORD` | **Obligatoria** — Redis exige `--requirepass` |

### MinIO

| Variable | Descripción |
|---|---|
| `MINIO_ROOT_USER` | Usuario admin (default `clauboard_admin`) |
| `MINIO_ROOT_PASSWORD` | **Obligatoria** |

### Grafana

| Variable | Descripción |
|---|---|
| `GRAFANA_ADMIN_USER` | Usuario admin (default `clauboard_admin`) |
| `GRAFANA_ADMIN_PASSWORD` | **Obligatoria** |

```bash
cp infra/.env.example infra/.env
nano infra/.env
```

## Variables que NO viven en `.env` (por diseño)

Estas se generan **por proyecto**, automáticamente, dentro de
`clauboard-projects/<id>/.env` — no son configuración global, así
que no tienen entrada en `.env.example`. Ver `docs/architecture.md`,
sección "Proyectos", para el detalle completo de cómo se resuelven:

- `PROJECT_ID`, `PROJECT_NAME`, `TZ`
- `DEVICE` (dispositivo serial/USB, si aplica al template)
- `MICRO_IMAGE` (imagen resuelta según framework/arch/microros elegidos)
- `ROS_DOMAIN_ID`, `DISPLAY` (solo template ROS2)

## Reproducibilidad — checklist para levantar el proyecto en una máquina nueva

1. Clonar el repo
2. `cp .env.example .env` → completar `CLAUBOARD_PROJECTS_DIR` si no se quiere el default
3. `cp infra/.env.example infra/.env` → completar **todas** las contraseñas/tokens (no hay defaults de seguridad, es intencional)
4. `sudo scripts/create-data-dirs.sh` — crea las carpetas de datos en el host con los permisos correctos antes de instalar apps
5. Construir las imágenes propias (`build-all.sh`, `build-micro-images.sh`, `build-pico-images.sh`, `opencv-cuda` — ver README principal)
6. `./start.sh`

Ningún paso de este checklist depende de un valor hardcodeado en el código — todo pasa por estos dos `.env`, que es justo lo que los hace reproducibles entre máquinas distintas.