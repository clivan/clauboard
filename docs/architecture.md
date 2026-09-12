# Arquitectura

## Capas del backend

```
Frontend (HTML/CSS/JS vanilla)
        │  HTTP/REST + SSE (progreso de instalación)
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
        │                  DockerComposeService  ← único que llama docker compose CLI (proyectos)
        │                  DockerService         ← único que usa el SDK de Python (apps de servicio)
        │                  TemplateService
        │                  EnvService
        │                  WorkspaceService
        │                  GitService
        │                  ManifestService
        │                  FrameworkRegistry     ← matriz framework/arch/microros por chip
        │
        └──────────────► Repositories
                           ProjectRepository     ← lee/escribe JSON de proyectos
                           PluginRepository      ← lee manifests de plugins
                              │
                              ▼
                         Sistema de archivos     ← fuente de verdad
```

**Deuda técnica conocida, pausada a propósito:** `DockerService` (SDK) y `DockerComposeService` (CLI) son dos rutas distintas para gestionar contenedores — las apps de servicio usan una, los proyectos usan la otra. Unificar en CLI está identificado como mejora pero no es urgente.

## Tipos de aplicación (`ApplicationType`)

| Tipo | Ciclo de vida | Ejemplo |
|---|---|---|
| `service` | `docker run -d` persistente | Syncthing, Ollama, Open WebUI, ComfyUI |
| `toolchain` | `docker compose run --rm` interactivo | AVR, MSP430, STM32, ESP32, Pico, ROS2 |
| `infrastructure` | `docker compose up` en `infra/` | Postgres, InfluxDB, Redis |

## Frameworks y arquitecturas por microcontrolador

Cada toolchain de chip soporta un subconjunto distinto de frameworks — no todos los RTOS corren en todos los chips. La matriz vive en `backend/app/services/framework_registry.py` y alimenta el dropdown anidado del formulario de "Nuevo proyecto" (Template → Framework → Arquitectura → checkbox micro-ROS).

| Chip | Frameworks disponibles | micro-ROS |
|---|---|---|
| **AVR** | bare metal, FreeRTOS | No (8-bit insuficiente) |
| **MSP430** | bare metal, FreeRTOS | No (no soportado) |
| **STM32** | bare metal, FreeRTOS, Zephyr, MicroPython | Sí, en FreeRTOS y Zephyr |
| **ESP32** | bare metal (=FreeRTOS, ESP-IDF ya lo incluye), Zephyr (soporte parcial), MicroPython | Sí, en las 3 variantes con RTOS |
| **RPi Pico 2 (RP2350)** | bare metal (ARM/RISC-V), MicroPython (ARM/RISC-V), FreeRTOS (básico, ARM), Zephyr (básico, ARM) | Sí, solo bare metal, solo transporte Serial |

Notas importantes documentadas también en los propios Dockerfiles:
- **Zephyr no soporta AVR ni MSP430** — excluido explícitamente de su matriz de soporte oficial
- **MicroPython no soporta AVR ni MSP430** — no están entre sus puertos oficiales (arquitecturas de 8/16-bit fuera de su alcance)
- **ESP32 "bare metal" y "FreeRTOS" son la misma imagen** — ESP-IDF ya usa FreeRTOS como kernel interno
- **Zephyr en ESP32 tiene soporte parcial** según el propio proyecto Zephyr — puede que WiFi/Bluetooth no funcionen completos
- **FreeRTOS/Zephyr en Pico son templates básicos** — funcionan pero menos pulidos que bare metal/MicroPython (decisión consciente: se usan "por si acaso", no en proyectos activos)
- **micro-ROS no es un framework por sí solo** — es una librería en C que se compila junto con FreeRTOS o Zephyr existentes, de ahí que sea un checkbox combinable y no una opción más en la lista de frameworks

La imagen final se resuelve en tiempo de creación del proyecto (`resolve_image()` en `framework_registry.py`) y se guarda como `MICRO_IMAGE` en el `.env` del proyecto, que el `compose.yml` del template consume vía `${MICRO_IMAGE}`.

## Catálogo de aplicaciones (`registry/applications/`)

### Services
- `syncthing` — sincronización de archivos
- `ollama` — runtime de LLMs locales (RTX 3050 6GB: `qwen2.5-coder:3b` para código, `llama3.2:3b` para texto, `nomic-embed-text` para embeddings)
- `webui` (Open WebUI) — UI para Ollama, con vault de Obsidian montado de solo lectura para RAG vía Knowledge
- `openwebui-pipelines` — framework de plugins de Open WebUI; usado para el filtro de MarkItDown (convierte documentos adjuntos a Markdown antes de mandarlos al LLM, ahorra tokens)
- `comfyui` — generación de imágenes (SD 1.5 cómodo en 6GB VRAM, SDXL con `--lowvram`)
- `whisper` — transcripción de audio, API compatible con OpenAI, conectable a Open WebUI
- `node-red` — programación por flujos
- `flowise` — constructor visual de agentes LLM
- `espconnect` — flasheo de ESP32/ESP8266 vía Web Serial (requiere Chrome)
- `adminer` — cliente web para Postgres
- `mongo-express` — cliente web para MongoDB
- `redisinsight` — cliente web para Redis
- `uptime-kuma` — monitor de disponibilidad

### Toolchains
- `avr` — avr-gcc + avr-as + avrdude (privileged para USBasp; sin device fijo)
- `msp430` — msp430-elf-gcc + as (device: `/dev/ttyACM0`)
- `stm32` — arm-none-eabi-gcc/as + st-link (privileged para ST-Link; sin device fijo)
- `esp32` — ESP-IDF oficial (device: `/dev/ttyUSB0`)
- `rpi-pico` — Pico SDK / MicroPython / FreeRTOS / Zephyr para RP2350 (device: `/dev/ttyACM0`)
- `opencv` — OpenCV standalone sin ROS2
- `ros2` — ROS2 Humble; ver sección de servicios independientes abajo
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

Tres scripts de build, uno por familia:

```bash
backend/app/registry/templates/build-all.sh          # ROS2 + OpenCV
backend/app/registry/templates/build-micro-images.sh # AVR/MSP430/STM32/ESP32 (todas las combinaciones)
backend/app/registry/templates/build-pico-images.sh  # RPi Pico (todas las combinaciones)
```

**ROS2 / visión** (jerarquía achatada — todas hermanas de `ros2-base`, no en cadena):
```
clauboard/ros2-base:humble        ← base con todos los paquetes comunes de ROS2
clauboard/ros2-cv:humble          ← base + OpenCV + cv_bridge (independiente)
clauboard/ros2-realsense:humble   ← base + librealsense2 + realsense2_camera (independiente, YA NO requiere cv)
clauboard/ros2-gazebo:humble      ← base + ros-gz (simulación)
clauboard/opencv:latest           ← standalone, sin ROS2
```
El proyecto ROS2 (`backend/templates/ros2/compose/compose.yml`) define 4 servicios independientes (`ros2`, `realsense-driver`, `vision-processing`, `gazebo`) — comenta/quita el que no necesites en tu proyecto concreto, no vienen forzados juntos.

**Microcontroladores** (una imagen por combinación chip+framework+arch):
```
clauboard/avr-baremetal, clauboard/avr-freertos
clauboard/msp430-baremetal, clauboard/msp430-freertos
clauboard/stm32-baremetal, clauboard/stm32-freertos, clauboard/stm32-zephyr, clauboard/stm32-micropython
clauboard/esp32-baremetal, clauboard/esp32-freertos, clauboard/esp32-zephyr, clauboard/esp32-micropython
clauboard/esp32-freertos-microros                     ← ejemplo de combinación con micro-ROS
clauboard/rpi-pico-baremetal-arm, clauboard/rpi-pico-baremetal-riscv
clauboard/rpi-pico-micropython-arm, clauboard/rpi-pico-micropython-riscv
clauboard/rpi-pico-freertos, clauboard/rpi-pico-zephyr
```

## Mini-DNS (`proxy/conf.d/`)

nginx como reverse proxy — un `.conf` por app, patrón `<nombre>.localhost`.  
Resolver interno de Docker (`127.0.0.11`) para resolución perezosa: nginx no crashea si el contenedor no existe todavía (usa `resolver` + variable `set $upstream`, no un `proxy_pass` directo al hostname).

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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
```bash
docker exec clauboard-proxy nginx -s reload
```
Los headers de `Upgrade`/`Connection` son necesarios para apps que usan WebSocket (Node-RED, Open WebUI, Flowise, Uptime Kuma).

## Proyectos

Cada proyecto se crea en `CLAUBOARD_PROJECTS_DIR` (configurable en `.env` raíz, default `./clauboard-projects` dentro del repo).

**Estructura generada, varía por template** (definida en `WorkspaceService`, no es fija):

```
mi-proyecto-avr/            mi-proyecto-ros2/          mi-proyecto-cv/
  src/                        src/                       src/
  include/                    build/                     data/
  build/                      install/                   output/
  compose/compose.yml         log/                       compose/compose.yml
  Makefile                    compose/compose.yml        .env
  .gitignore                  .env                       README.md
  .env                        README.md
  README.md
```

Todos comparten: `compose/` (el `compose.yml` copiado del template), `.env` (generado por `EnvService`), `README.md`, `.clauboard/project.yaml` (manifest).

**El `.env` incluye, según template:**
- `PROJECT_ID`, `PROJECT_NAME`, `TZ` — siempre
- `DEVICE` — si el template/formulario lo especifica
- `MICRO_IMAGE` — si el template tiene frameworks (avr/msp430/stm32/esp32/rpi-pico), resuelto según framework+arch+microros elegidos
- `ROS_DOMAIN_ID` (derivado del hash del project_id, evita colisiones entre proyectos) y `DISPLAY` — solo para ROS2

**Makefiles generados** (AVR y MSP430 los usan de forma no trivial):
- Ambos leen `DEVICE` del `.env` del proyecto vía `$(shell grep DEVICE ../.env ...)`, así que cambiar el dispositivo en el `.env` alimenta directo el `make flash` sin tocar el Makefile.
- AVR trae además un target `fuses` (valores de ejemplo, hay que ajustarlos al chip real — ver `engbedded.com/fusecalc`) y una variable `PROGRAMMER` (default `usbasp`).

**Ejecutar el toolchain:** desde la card del proyecto, botón **Shell** → devuelve el comando `docker compose run --rm <servicio>` ya resuelto con `--env-file` y `-f` correctos. No hay terminal en el navegador — se copia y se corre en tu terminal local, donde tu `src/` ya está montado.

## Plugins

Los plugins son accesos directos a UIs de apps ya corriendo.  
Cada plugin tiene un `manifest.yml` en `plugins/applications/<id>/`.  
Cuando la app tiene `status: running`, aparece el botón "Abrir ↗" en su card.

Descartado (decisión consciente, no pendiente): plugins de "acción" (ej. flashear firmware desde un botón) — Serial Studio/TSMaster ya cubren el caso de monitoreo/flasheo mejor que reconstruirlo dentro de Clauboard.

## Redes

Todos los contenedores viven en `clauboard-net` (red externa, creada por el compose principal).  
`infra/compose.yml` la declara como `external: true` — por eso el compose principal debe levantarse primero (`start.sh` ya maneja este orden).

**Recuperación de red huérfana:** si haces `docker compose down` + `up` (recreando la red con un ID nuevo), los contenedores de apps creados antes quedan huérfanos. `DockerService.start()` detecta el error "network not found" y reconecta automáticamente a la red actual antes de reintentar — no hace falta reinstalar manualmente.

## Barra de progreso de instalación

Para apps pesadas (Ollama, ComfyUI), `GET /applications/{id}/install/progress` expone un stream SSE con el progreso del `docker pull` capa por capa (MB descargados, porcentaje). El frontend lo consume con `EventSource` y muestra una barra fija en la parte inferior del dashboard mientras dura la instalación.