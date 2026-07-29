# Arquitectura

## Capas del backend

```
Frontend (HTML/CSS/JS vanilla)
        │  HTTP/REST
        ▼
API (FastAPI)          ← solo expone endpoints
        │
        ▼
Managers               ← orquestan el flujo
  ProjectManager
  ApplicationManager
  PluginManager
        │
        ├──────────────► Services
        │                  DockerComposeService  ← único que llama docker compose CLI
        │                  DockerService         ← único que usa el SDK de Python
        │                  TemplateService
        │                  EnvService
        │                  WorkspaceService
        │                  GitService
        │                  ManifestService
        │
        └──────────────► Repositories
                           ProjectRepository     ← lee/escribe JSON de proyectos
                           PluginRepository      ← lee manifests de plugins
                              │
                              ▼
                         Sistema de archivos     ← fuente de verdad
```

## Tipos de aplicación (`ApplicationType`)

| Tipo | Ciclo de vida | Ejemplo |
|---|---|---|
| `service` | `docker run -d` persistente | Syncthing, Ollama, Node-RED |
| `toolchain` | `docker compose run --rm` interactivo | AVR, ESP32, ROS2 |
| `infrastructure` | `docker compose up` en `infra/` | Postgres, InfluxDB, Redis |

## Catálogo de aplicaciones (`registry/applications/`)

### Services
- `syncthing` — sincronización de archivos
- `ollama` — runtime de LLMs locales
- `open-webui` — UI para Ollama
- `node-red` — programación por flujos
- `flowise` — constructor visual de agentes LLM
- `espconnect` — flasheo de ESP32/ESP8266 vía Web Serial (requiere Chrome)
- `adminer` — cliente web para Postgres
- `mongo-express` — cliente web para MongoDB
- `redisinsight` — cliente web para Redis
- `uptime-kuma` — monitor de disponibilidad

### Toolchains
- `avr` — avr-gcc + avr-as + avrdude (privileged para USBasp)
- `msp430` — msp430-elf-gcc + as (device: `/dev/ttyACM0`)
- `stm32` — arm-none-eabi-gcc + st-link (privileged para ST-Link)
- `esp32` — ESP-IDF oficial (device: `/dev/ttyUSB0`)
- `opencv` — OpenCV standalone sin ROS2
- `ros2` — ROS2 Humble + librealsense + OpenCV (para SR300)
- `yocto` — CROPS/Poky Ubuntu 22.04

### Infrastructure (`infra/compose.yml`)
- `clauboard-postgres` — Postgres 16
- `clauboard-mongodb` — MongoDB 7
- `clauboard-influxdb` — InfluxDB 2 (series de tiempo, telemetría)
- `clauboard-redis` — Redis 7
- `clauboard-minio` — MinIO (objetos: rosbags, firmware, modelos)
- `clauboard-mosquitto` — Broker MQTT (listener 1883 + 9001 WebSockets)
- `clauboard-grafana` — Grafana (visualización de métricas)

## Imágenes propias (`registry/templates/`)

Construir con `backend/app/registry/templates/build-all.sh`:

```
clauboard/opencv:latest
clauboard/ros2-base:humble      ← base con todos los paquetes comunes de ROS2
clauboard/ros2-cv:humble        ← ros2-base + OpenCV + cv_bridge
clauboard/ros2-realsense:humble ← ros2-cv + librealsense2 + realsense2_camera
clauboard/ros2-gazebo:humble    ← ros2-base + ros-gz (simulación)
```

## Mini-DNS (`proxy/conf.d/`)

nginx como reverse proxy — un `.conf` por app, patrón `<nombre>.localhost`.  
Resolver interno de Docker (`127.0.0.11`) para resolución perezosa: nginx no crashea si el contenedor no existe todavía.

Para agregar un alias nuevo:
```nginx
server {
    listen 80;
    server_name miapp.localhost;
    resolver 127.0.0.11 valid=10s;
    location / {
        set $upstream container-name:puerto;
        proxy_pass http://$upstream;
        proxy_set_header Host $host;
    }
}
```
```bash
docker exec clauboard-proxy nginx -s reload
```

## Proyectos

Cada proyecto se crea en `CLAUBOARD_PROJECTS_DIR` (configurable en `.env` raíz).  
Al crearse se generan automáticamente:
```
mi-proyecto/
  compose/
    compose.yml    ← copiado del template elegido
  .env             ← generado con PROJECT_NAME, TZ, DEVICE, ROS_DOMAIN_ID, etc.
  src/             ← código fuente (editar desde VS Code)
  build/           ← cache de compilación (Yocto/ROS2)
  install/         ← artifacts de colcon (ROS2)
  data/
  logs/
  backups/
  .clauboard/
    project.yaml   ← manifest del proyecto
  README.md
```

## Plugins

Los plugins son accesos directos a UIs de apps ya corriendo.  
Cada plugin tiene un `manifest.yml` en `plugins/applications/<id>/`.  
Cuando la app tiene `status: running`, aparece el botón "Abrir ↗" en su card.

## Redes

Todos los contenedores viven en `clauboard-net` (red externa, creada por el compose principal).  
`infra/compose.yml` la declara como `external: true` — por eso el compose principal debe levantarse primero (`start.sh` ya maneja este orden).

## Nota sobre `DockerService` vs `DockerComposeService`

Deuda técnica pendiente: las apps tipo `service` usan `DockerService` (SDK de Python), los proyectos usan `DockerComposeService` (CLI). La migración a CLI unificado queda pendiente para post-MVP.