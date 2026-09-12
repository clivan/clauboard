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
        │                  TemplateService        ← filtra servicios opcionales de ROS2 al copiar
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
| `service` | `docker run -d` persistente | Syncthing, Ollama, Open WebUI, ComfyUI, Grafana |
| `toolchain` | `docker compose run --rm` interactivo | AVR, MSP430, STM32, ESP32, Pico, ROS2, OpenCV |
| `infrastructure` | `docker compose up` en `infra/` | Postgres, InfluxDB, Redis, Prometheus |


## Frameworks y arquitecturas por microcontrolador

Cada toolchain de chip soporta un subconjunto distinto de frameworks — no todos los RTOS corren en todos los chips. La matriz vive en `backend/app/services/framework_registry.py` y alimenta el dropdown anidado del formulario de "Nuevo proyecto" (Template → Framework → Arquitectura → checkbox micro-ROS).

| Chip | Frameworks disponibles | micro-ROS |
|---|---|---|
| **AVR** | bare metal, FreeRTOS | No (8-bit insuficiente) |
| **MSP430** | bare metal, FreeRTOS | No (excluido de la matriz de soporte oficial de Zephyr y MicroPython) |
| **STM32** | bare metal, FreeRTOS, Zephyr, MicroPython | Sí, en FreeRTOS y Zephyr |
| **ESP32** | bare metal (=FreeRTOS, ESP-IDF ya lo incluye), Zephyr (soporte parcial), MicroPython | Sí, en las 3 variantes con RTOS |
| **RPi Pico 2 (RP2350)** | bare metal (ARM/RISC-V), MicroPython (ARM/RISC-V), FreeRTOS (básico, ARM), Zephyr (básico, ARM) | Sí, solo bare metal, solo transporte Serial |

Notas importantes documentadas también en los propios Dockerfiles:
- **Zephyr no soporta AVR ni MSP430** — excluido explícitamente de su matriz de soporte oficial
- **MicroPython no soporta AVR ni MSP430** — no están entre sus puertos oficiales (arquitecturas de 8/16-bit fuera de su alcance)
- **ESP32 "bare metal" y "FreeRTOS" son la misma imagen** — ESP-IDF ya usa FreeRTOS como kernel interno
- **Zephyr en ESP32 tiene soporte parcial** según el propio proyecto Zephyr — puede que WiFi/Bluetooth no funcionen completos
- **FreeRTOS/Zephyr en Pico son templates básicos** — funcionan pero menos pulidos que bare metal/MicroPython (decisión consciente: se usan "por si acaso", no en proyectos activos). micro-ROS sobre FreeRTOS en Pico específicamente no tiene soporte oficial confirmado — hay un intento de terceros (`pi-pico-drone`) marcado como Work-In-Progress
- **micro-ROS no es un framework por sí solo** — es una librería en C que se compila junto con FreeRTOS o Zephyr existentes, de ahí que sea un checkbox combinable y no una opción más en la lista de frameworks

La imagen final se resuelve en tiempo de creación del proyecto (`resolve_image()` en `framework_registry.py`) y se guarda como `MICRO_IMAGE` en el `.env` del proyecto, que el `compose.yml` del template consume vía `${MICRO_IMAGE}`.

## Gestión de dependencias (AVR / MSP430 / STM32)

Estos tres templates generan un `deps.txt` (una URL de git por línea) y un target `make deps` en su Makefile — clona cada repo a `lib/` si no existe ya, idempotente. ESP32 y Pico quedan fuera (ESP-IDF ya trae su propio gestor de componentes vía `idf_component.yml`; MicroPython no aplica). `lib/` está en `.gitignore` — las dependencias no se versionan, se re-resuelven con `make deps`.

## Debug remoto con GDB (STM32)

El template STM32 incluye:
- Target `make debug` — lanza OpenOCD (`interface/stlink.cfg` + `target/stm32f4x.cfg`) dentro del contenedor
- Puertos publicados en el `compose.yml` del proyecto: `3333` (GDB remoto) y `4444` (telnet de OpenOCD)
- `.vscode/launch.json` generado automáticamente (extensión Cortex-Debug, `request: attach`, `servertype: external`, apunta a `localhost:3333`)

Ajustar `target/stm32f4x.cfg` a la familia real del chip si no es F4 (`stm32f1x.cfg`, `stm32l4x.cfg`, etc.) — es manual, el template no distingue sub-familias de STM32 automáticamente.

## Selección de servicios ROS2 al crear el proyecto

El `compose.yml` de ROS2 trae 4 servicios independientes: `ros2` (siempre incluido), `realsense-driver`, `vision-processing`, `gazebo` (opcionales). Al crear el proyecto, el formulario muestra 3 checkboxes (Cámara RealSense / Visión OpenCV / Simulación Gazebo) — `TemplateService._apply_ros2_compose()` filtra el `compose.yml` generado para incluir solo los servicios elegidos, sin tocar el resto del flujo de creación. Sin selección explícita (`ros2_services: None`), se copia el archivo completo con los 4 servicios (comportamiento retrocompatible).

## Catálogo de aplicaciones (`registry/applications/`)

### Services
- `syncthing` — sincronización de archivos
- `ollama` — runtime de LLMs locales (RTX 3050 6GB: `qwen2.5-coder:3b` para código, `llama3.2:3b` para texto, `nomic-embed-text` para embeddings)
- `webui` (Open WebUI) — UI para Ollama y Claude (vía conexión OpenAI-compatible de Anthropic), con vault de Obsidian montado para RAG vía Knowledge
- `openwebui-pipelines` — framework de plugins de Open WebUI; usado para el filtro de MarkItDown (convierte documentos adjuntos a Markdown antes de mandarlos al LLM, ahorra tokens)
- `comfyui` — generación de imágenes (SD 1.5 cómodo en 6GB VRAM, SDXL con `--lowvram`); requiere workflow JSON pegado en Open WebUI y al menos un checkpoint descargado en `models/checkpoints/`
- `whisper` — transcripción de audio, API compatible con OpenAI, conectable a Open WebUI (usar engine "OpenAI" ahí, no "Whisper Local", para evitar duplicar el modelo)
- `node-red` — programación por flujos
- `flowise` — constructor visual de agentes LLM (capa visual sobre LangChain)
- `espconnect` — flasheo de ESP32/ESP8266 vía Web Serial (requiere Chrome)
- `adminer` — cliente web para Postgres
- `mongo-express` — cliente web para MongoDB
- `redisinsight` — cliente web para Redis
- `uptime-kuma` — monitor de disponibilidad
- `grafana` — dashboards de métricas (ver nota sobre reclasificación arriba); fuentes de datos: InfluxDB (telemetría empujada por proyectos) y Prometheus (métricas scrapeadas de infraestructura)
- `prometheus` — recolector de métricas por scrape; único de los 3 nuevos de monitoreo con UI propia (los otros dos son solo exporters)

### Toolchains
- `avr` — avr-gcc + avr-as + avrdude (privileged para USBasp; sin device fijo); soporta `deps.txt`
- `msp430` — msp430-elf-gcc + as (device: `/dev/ttyACM0`); soporta `deps.txt`
- `stm32` — arm-none-eabi-gcc/as + st-link (privileged para ST-Link; sin device fijo); soporta `deps.txt` y debug remoto con GDB
- `esp32` — ESP-IDF oficial (device: `/dev/ttyUSB0`)
- `rpi-pico` — Pico SDK / MicroPython / FreeRTOS / Zephyr para RP2350 (device: `/dev/ttyACM0`)
- `opencv` — OpenCV standalone, imagen ligera (core + Python/C++, sin CUDA)
- `ros2` — ROS2 Humble; servicios independientes seleccionables (ver sección arriba)
- `yocto` — CROPS/Poky Ubuntu 22.04

### Infrastructure (`infra/compose.yml`)
- `clauboard-postgres` — Postgres 16
- `clauboard-mongodb` — MongoDB 7
- `clauboard-influxdb` — InfluxDB 2 (series de tiempo, telemetría empujada por proyectos)
- `clauboard-redis` — Redis 7
- `clauboard-minio` — MinIO (objetos: rosbags, firmware, modelos)
- `clauboard-mosquitto` — Broker MQTT (listener 1883 + 9001 WebSockets)
- `clauboard-cadvisor` — métricas de CPU/RAM/red por contenedor Docker (scrapeado por Prometheus, sin UI propia)
- `clauboard-node-exporter` — métricas del host/laptop: CPU, disco, memoria (scrapeado por Prometheus, sin UI propia)

## Imágenes propias (`registry/templates/`)

Scripts de build, uno por familia:

```bash
backend/app/registry/templates/build-all.sh          # ROS2 + OpenCV (ligero)
backend/app/registry/templates/build-micro-images.sh # AVR/MSP430/STM32/ESP32 (todas las combinaciones)
backend/app/registry/templates/build-pico-images.sh  # RPi Pico (todas las combinaciones)
```

`opencv-cuda` se construye aparte (build largo, 20-60 min, no incluido en los scripts anteriores):
```bash
docker build -t clauboard/opencv-cuda:latest ./opencv-cuda
```

**ROS2 / visión** (jerarquía achatada — todas hermanas de `ros2-base`, no en cadena):
```
clauboard/ros2-base:humble        ← base con todos los paquetes comunes de ROS2
clauboard/ros2-cv:humble          ← base + OpenCV + cv_bridge (independiente)
clauboard/ros2-realsense:humble   ← base + librealsense2 + realsense2_camera (independiente, YA NO requiere cv)
clauboard/ros2-gazebo:humble      ← base + ros-gz (simulación)
clauboard/opencv:latest           ← standalone, sin ROS2, ligero (sin CUDA)
clauboard/opencv-cuda:latest      ← standalone, completo: core + contrib + CUDA + cuDNN + DNN acelerado
```

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

**Gotchas de build encontrados y resueltos** (dejarlos documentados evita repetir el mismo diagnóstico):
- Los Dockerfiles que hacen `git clone` de un repo HTTPS necesitan `ca-certificates` explícito en el `apt-get install` — sin esto, `git clone` falla con error de verificación de certificado SSL, incluso con la hora del sistema correcta
- Los Dockerfiles de Zephyr necesitan `build-essential` y `python3-dev` — sin estos, `pip install` de dependencias de `west` falla al compilar extensiones nativas de Python (`tree-sitter-cmake`, entre otras) con errores como `Python.h: No such file or directory`

**`opencv-cuda` — específico de hardware, leer antes de reusar:**
- `CUDA_ARCH_BIN=8.6` está fijado para RTX 30xx (confirmado para RTX 3050) — ajustar si se usa con otra GPU (RTX 40xx=8.9, RTX 20xx/GTX 16xx=7.5)
- Requiere NVIDIA Container Toolkit instalado en el host — verificar con `docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi` antes de construir
- El `compose.yml` del proyecto necesita el bloque `deploy.resources.reservations.devices` con `driver: nvidia` para que el contenedor tenga acceso real a la GPU en runtime
- Build largo (20-60 min, compila OpenCV completo desde fuente — no existe wheel de pip con soporte CUDA)
- Pendiente: una variante ARM64/L4T para correr en la Jetson del homelab — la imagen actual es x86_64 únicamente, no es intercambiable con Jetson (JetPack/L4T usa una base de CUDA distinta a la de escritorio)

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

Cada proyecto se crea en `CLAUBOARD_PROJECTS_DIR` (configurable en `.env` raíz — puede apuntar a cualquier carpeta del host, no tiene que vivir dentro del repo).

**Estructura generada, varía por template** (definida en `WorkspaceService`, no es fija):

```
mi-proyecto-avr/            mi-proyecto-ros2/          mi-proyecto-cv/
  src/                        src/                       src/
  include/                    build/                     data/
  build/                      install/                   output/
  lib/  (deps.txt)             log/                       compose/compose.yml
  compose/compose.yml         compose/compose.yml         .env
  Makefile                    .env                        README.md
  .gitignore                  README.md
  .env
  README.md

mi-proyecto-stm32/  (además de lo de arriba)
  .vscode/launch.json    ← debug remoto con Cortex-Debug
```

Todos comparten: `compose/` (el `compose.yml` copiado del template), `.env` (generado por `EnvService`), `README.md`, `.clauboard/project.yaml` (manifest).

**El `.env` incluye, según template:**
- `PROJECT_ID`, `PROJECT_NAME`, `TZ` — siempre
- `DEVICE` — si el template/formulario lo especifica
- `MICRO_IMAGE` — si el template tiene frameworks (avr/msp430/stm32/esp32/rpi-pico), resuelto según framework+arch+microros elegidos
- `ROS_DOMAIN_ID` (derivado del hash del project_id, evita colisiones entre proyectos) y `DISPLAY` — solo para ROS2

**Ejecutar el toolchain:** desde la card del proyecto, botón **Shell** → devuelve el comando `docker compose run --rm <servicio>` ya resuelto con `--env-file` y `-f` correctos. No hay terminal en el navegador — se copia y se corre en tu terminal local, donde tu `src/` ya está montado.

**Clonar proyectos:** botón **Clonar** en la card → copia la carpeta completa (código, `.env`, `compose.yml`) a un nuevo id/ruta, reinicializa git sin el historial del original.

**Status en tiempo real:** cada card de proyecto consulta `GET /projects/{id}/stack-status` (estado simplificado: `running`/`partial`/`stopped`/`no_compose`) y muestra un LED — se actualiza automáticamente tras cada Up/Down/Restart.

## Integraciones de IA (Open WebUI)

- **Ollama**: conexión nativa, `http://ollama:11434`, sin autenticación (Auth: None — un Bearer/API Key configurado por error da `Missing bearer authentication`)
- **Claude (Anthropic)**: vía la capa de compatibilidad OpenAI de Anthropic — se agrega en `Admin → Settings → Connections → OpenAI API` (no en la sección de Ollama, son protocolos distintos), URL `https://api.anthropic.com/v1`. No incluye features Claude-nativas (PDFs nativos, prompt caching, extended thinking) por ser la capa de compatibilidad, no la API real de Anthropic
- **Embeddings (RAG del vault de Obsidian)**: `Admin → Settings → Documents → Embedding`, engine `Ollama`, modelo `nomic-embed-text`. Se resetea a `sentence-transformers` (default) cada vez que se reinstala el contenedor de Open WebUI — hay que reconfigurar después de cada reinstalación. Cambiar el modelo de embeddings requiere **Reindex** de cualquier Knowledge Base ya creada
- **Whisper (STT)**: `Admin → Settings → Audio`, engine `OpenAI` (no "Whisper Local", que ejecuta un Whisper interno separado del contenedor `whisper`), URL `http://whisper:9000/v1`, modelo `whisper-1`
- **ComfyUI (imágenes)**: `Admin → Settings → Images`, engine `ComfyUI`, URL `http://comfyui:8188`, requiere pegar un workflow JSON (formato API de ComfyUI) y mapear nodos (prompt/model/width/height/steps/seed) a sus IDs de nodo
- **Pipelines + MarkItDown**: contenedor `openwebui-pipelines` agregado como conexión OpenAI API (`http://openwebui-pipelines:9099`); el pipeline `markitdown_filter.py` se coloca en el volumen de pipelines y convierte adjuntos a Markdown antes de mandarlos al LLM

## Plugins

Los plugins son accesos directos a UIs de apps ya corriendo.  
Cada plugin tiene un `manifest.yml` en `plugins/applications/<id>/`.  
Cuando la app tiene `status: running`, aparece el botón "Abrir ↗" en su card.

Cobertura actual: syncthing, adminer, espconnect, flowise, mongo-express, node-red, redisinsight, webui, grafana, prometheus. cAdvisor y node-exporter no llevan plugin — no tienen UI propia, solo exponen `/metrics` para Prometheus.

Descartado (decisión consciente, no pendiente): plugins de "acción" (ej. flashear firmware desde un botón) — Serial Studio/TSMaster ya cubren el caso de monitoreo/flasheo mejor que reconstruirlo dentro de Clauboard.

## Redes

Todos los contenedores viven en `clauboard-net` (red externa, creada por el compose principal).  
`infra/compose.yml` la declara como `external: true` — por eso el compose principal debe levantarse primero (`start.sh` ya maneja este orden).

**Recuperación de red huérfana:** si haces `docker compose down` + `up` (recreando la red con un ID nuevo), los contenedores de apps creados antes quedan huérfanos. `DockerService.start()` detecta el error "network not found" y reconecta automáticamente a la red actual antes de reintentar — no hace falta reinstalar manualmente.

## Barra de progreso de instalación

Para apps pesadas (Ollama, ComfyUI), `GET /applications/{id}/install/progress` expone un stream SSE con el progreso del `docker pull` capa por capa (MB descargados, porcentaje). El frontend lo consume con `EventSource` y muestra una barra fija en la parte inferior del dashboard mientras dura la instalación.