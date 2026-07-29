# Roadmap

## Estado general

MVP en progreso. La base funciona: proyectos, aplicaciones, templates, infraestructura, mini-DNS.  
Lo que falta para cerrar el MVP está en la sección siguiente.

---

## Para cerrar el MVP

### 1. Ciclo de vida de toolchains desde el dashboard
El template se copia y el `.env` se genera al crear un proyecto, pero todavía no hay forma de *ejecutarlo* desde el dashboard. Falta:
- Endpoint `POST /projects/{id}/compose/run`
- Botón en la card del proyecto que muestre el comando a correr en terminal (o lo copie al portapapeles)
- No se busca una terminal en el navegador — solo el comando correcto con el `--env-file` y el `-f compose/compose.yml` ya resueltos

### 2. Device dinámico en formulario de proyecto
El campo `DEVICE` del `.env` se genera con el valor típico del template (`/dev/ttyUSB0`, `/dev/ttyACM0`, etc.) pero si la placa aparece en otro puerto hay que editarlo a mano. Falta:
- Campo "Dispositivo" en el formulario de "Nuevo proyecto" (pre-rellenado con el default del template, editable)
- Endpoint `PATCH /projects/{id}/env` para actualizar variables del `.env` desde el dashboard sin recrear el proyecto

### 3. Migración de DockerService a DockerComposeService
Deuda técnica: las apps tipo `service` usan el SDK de Python (`DockerService`), los proyectos usan el CLI (`DockerComposeService`). Conviene unificar en CLI. Implica:
- Que cada app del registry tenga su `compose.yml` de un solo servicio
- Que `ApplicationManager` use `DockerComposeService` para todo
- Jubilar `DockerService`

---

## Post-MVP

### Git automático al crear proyectos
`GitService.init()` ya existe y corre `git init`. Falta el primer commit automático con los archivos generados (`.env`, `compose.yml`, `README.md`). El remote (GitHub o Gitea) se configura manualmente por proyecto con `git remote add origin <url>` — Clauboard no necesita gestionar el remote.

### Plugin de acción (one-shot)
Plugins que ejecuten un comando en un contenedor existente (ej. "flashear firmware"). Descartado para MVP porque las herramientas dedicadas (Serial Studio, TSMaster) ya cubren el caso de uso principal. Se reconsidera si el caso aparece frecuentemente en la práctica.

### Automatización de bases de datos por proyecto
Cuando un template declare `requires_db: "postgres"` (o mongo/influx), que `ApplicationManager` cree automáticamente la base de datos, usuario y permisos. Hoy es manual (ver `infra/postgres/init/README.md`).

### Hub de agentes IA
`GET /agents` retorna `[]`. Pendiente de definir qué significa exactamente el "hub" — ¿links a UIs como Open WebUI? ¿registro de modelos disponibles en Ollama? La infraestructura (modelo `Agent`, endpoint, patrón de manifest) ya está declarada esperando la decisión.

### Marketplace de templates de terceros
Hoy todos los templates son locales. Eventualmente: un índice remoto de templates compatibles con el formato de Clauboard que se puedan instalar con un click.

---

## Decisiones de diseño tomadas (no reabrir sin razón)

- **Sin base de datos** — el sistema de archivos es la fuente de verdad
- **Sin Traefik** — mini-DNS con nginx estático + resolver interno de Docker (`127.0.0.11`)
- **Sin terminal en el navegador** — los toolchains se usan desde la terminal local del host
- **Sin MQTT Panel** — Serial Studio/TSMaster cubren el monitoreo serial y MQTT
- **Gazebo nativo** — se instala en el host, no en contenedor (problema de GPU/X11)
- **Basys2 fuera** — Xilinx ISE tiene licencia propietaria, no hay imagen redistribuible
- **`restart: unless-stopped`** en todos los contenedores del stack principal e infra — para sobrevivir reinicios de laptop sin hacer `docker compose down`

---

## Sprints completados

| Sprint | Contenido |
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