# Roadmap

## Estado general

MVP funcional. Proyectos, aplicaciones, templates, infraestructura,
mini-DNS, frameworks/RTOS por chip, IA local (Ollama/Open WebUI/
Pipelines/ComfyUI/Whisper) — todo operativo. Lo que queda es deuda
técnica identificada y features declaradas pero sin definir a fondo.

---

## Pendiente — prioridad alta

### 1. `PATCH /projects/{id}/env`
Hoy el `.env` de un proyecto se genera una sola vez al crearlo. Si
cambias de placa/puerto después, hay que editar el archivo a mano en
el filesystem. Falta un endpoint que actualice variables puntuales
del `.env` desde el dashboard, sin recrear el proyecto.

### 2. Hub de agentes IA — ahora sí tiene sentido definirlo
`GET /agents` sigue siendo un stub (`[]`). Se dejó pendiente
originalmente por falta de infraestructura real — eso ya no aplica:
hoy hay Ollama + Open WebUI + Pipelines corriendo. Definir qué es
el "hub": ¿lista de modelos disponibles en Ollama? ¿links directos
a cada modelo en Open WebUI? ¿registro de agentes con tools/roles
específicos armados en Flowise? El modelo `Agent` y el endpoint ya
existen esperando la decisión de alcance.

### 3. Git automático al crear proyectos
`GitService.init()` corre `git init` pero nunca hay un primer commit.
Falta: commit automático de los archivos generados (`.env`,
`compose.yml`, `Makefile`, `.gitignore`, `README.md`) al crear el
proyecto. El remote (GitHub hoy, Gitea a futuro) se sigue
configurando manualmente por proyecto — Clauboard no gestiona el
remote, solo el repo local.

---

## Pendiente — prioridad media / deuda técnica conocida

### Migración de DockerService a DockerComposeService
Las apps tipo `service` usan el SDK de Python (`DockerService`), los
proyectos usan el CLI (`DockerComposeService`). Pausado a propósito
("dejar el 3 fuera por ahora") — no bloquea nada hoy, pero implica
mantener dos rutas de código para gestionar contenedores. Revisar
cuando el mantenimiento doble empiece a doler de verdad.

### Automatización de bases de datos por proyecto
El campo `requires_db` en el modelo `Application` existe pero no se
usa. Cuando un template lo declare, `ApplicationManager` debería
crear automáticamente la base de datos/usuario/permisos en el motor
correspondiente. Hoy es manual (ver `infra/postgres/init/README.md`).

---

## Pendiente — prioridad baja / exploratorio

### Marketplace de templates de terceros
Hoy todos los templates son locales. Eventualmente: índice remoto
de templates compatibles con el formato de Clauboard, instalables
con un click.

### Debugging real con GDB
STM32 ya tiene `openocd`+`stlink-tools` instalados en sus imágenes
— el debug con breakpoints ya es técnicamente posible, solo falta
documentar/exponer el flujo (hoy solo se usa para flashear).

### Testing unitario sin hardware
Zephyr (`native_sim`) y Pico SDK soportan compilar/correr pruebas
en la laptop sin la placa conectada. Útil para CI o iterar lógica
pura rápido. No evaluado en profundidad todavía.

### Proyecto separado: micro-tools
Calculadoras standalone (fuses AVR, baudrate UART por arquitectura,
PLL STM32, PWM ESP32/Pico, bit field visualizer, utilidades de
electrónica general). Decidido explícitamente como **proyecto aparte**,
no como pestaña de Clauboard — ver `micro_tools_contexto.md` en el
chat correspondiente para el detalle completo (fórmulas verificadas,
estructura de archivos, por qué no ImHex).

---

## Decisiones de diseño tomadas (no reabrir sin razón)

- **Sin base de datos propia** — el sistema de archivos es la fuente de verdad
- **Sin Traefik** — mini-DNS con nginx estático + resolver interno de Docker (`127.0.0.11`), por incompatibilidad de versión de API Docker con instalación snap
- **Sin terminal en el navegador** — los toolchains se usan desde la terminal local del host (`docker compose run --rm`, comando copiable desde el dashboard)
- **Sin MQTT Panel** — Serial Studio/TSMaster cubren el monitoreo serial y MQTT mejor
- **Sin Kokoro TTS / sin voz** — no hacía falta para el caso de uso real
- **Gazebo nativo** — se instala en el host, no en contenedor (rendimiento/GPU/X11)
- **Basys2 FPGA excluido** — Xilinx ISE tiene licencia propietaria, no hay imagen redistribuible legalmente
- **Sin plugins de "acción"** (ej. flashear desde un botón) — herramientas dedicadas ya cubren el caso mejor
- **`restart: unless-stopped`** en todos los contenedores del stack principal e infra — para sobrevivir reinicios de laptop sin `docker compose down`
- **ROS2 con servicios independientes**, no en cadena de herencia — cada imagen (`ros2-cv`, `ros2-realsense`, `ros2-gazebo`) parte directo de `ros2-base`, se combinan como servicios de compose según lo que el proyecto necesite, no como capas forzadas
- **Framework/RTOS por chip, no checkboxes de componentes** — la composición de piezas de un toolchain se resuelve en build-time (una imagen por combinación) o en servicios de compose separados, nunca generando Dockerfiles dinámicamente en runtime
- **micro-ROS como checkbox combinable**, no como framework más — es una librería que se agrega a FreeRTOS/Zephyr existentes, no una alternativa a ellos
- **AVR y STM32 sin dispositivo fijo por default** — usan programadores USB genéricos (USBasp, ST-Link), no un puerto serie predecible; el contenedor corre `privileged: true` en su lugar

---

## Sprints / sesiones completadas

| Sesión | Contenido |
|---|---|
| 0-1 | API base, arquitectura, workspace, repositories |
| 2 | Corrección de errores del scaffold inicial |
| 3 | DockerComposeService (up/down/restart/logs/status por proyecto) |
| 4 | Frontend HUD cyberpunk (4 pestañas, cards con LED de status) |
| 5 | Templates embebidos (AVR/MSP430/STM32/ESP32/Yocto/ROS2/OpenCV) |
| 6 | Infraestructura compartida separada (Postgres/Mongo/InfluxDB/Redis/MinIO/Mosquitto/Grafana) |
| 7 | Plugins (manifest + botón "Abrir ↗" cuando status=running) |
| 8 | Agentes IA declarados (stub) |
| 9 | Mini-DNS nginx, imágenes ROS2 propias, catálogo de aplicaciones extendido |
| 10 | Ciclo de vida toolchain desde dashboard (botón Shell), device dinámico en formulario |
| 11 | Clonar proyectos, LED de estado en cards de proyecto |
| 12 | Barra de progreso de instalación (SSE), ComfyUI, Whisper |
| 13 | Open WebUI: RAG con vault de Obsidian, Pipelines + MarkItDown |
| 14 | Framework/arch/microros por chip (AVR/MSP430/STM32/ESP32/Pico), ROS2 achatado a servicios independientes |
| 15 | Auditoría del repo (import roto, huecos de código), fixes, Makefiles con variable `DEVICE` |