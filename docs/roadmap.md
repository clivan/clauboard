# Roadmap

## Estado general

MVP funcional y ampliamente extendido. Proyectos, aplicaciones,
templates, infraestructura (incluyendo monitoreo), mini-DNS,
frameworks/RTOS por chip, gestión de dependencias, debug remoto,
IA local y externa (Ollama + Claude), y una imagen OpenCV completa
con CUDA — todo operativo. Lo que queda es deuda técnica identificada
y exploraciones registradas para otra sesión.

---

## Pendiente — prioridad alta

### 1. `PATCH /projects/{id}/env`
Hoy el `.env` de un proyecto se genera una sola vez al crearlo. Si
cambias de placa/puerto después, hay que editar el archivo a mano en
el filesystem. Falta un endpoint que actualice variables puntuales
del `.env` desde el dashboard, sin recrear el proyecto.

### 2. Modo de solo lectura real para volúmenes (`VolumeMapping.mode`)
Se necesitó montar el vault de Obsidian de solo lectura en Open WebUI
y no fue posible con el esquema actual — `ContainerFactory` fuerza
`mode: "rw"` en todos los volúmenes sin excepción, y el modelo
`VolumeMapping` no tiene campo para especificar el modo. El intento
de poner `:ro` dentro del string de `container` produce un error de
Docker (`invalid volume specification`, modos duplicados). Mientras
tanto, el vault quedó montado en modo lectura-escritura (funciona,
pero sin la protección real). Requiere: agregar campo `mode` a
`VolumeMapping` + que `ContainerFactory` lo respete en vez de
hardcodear `rw`.

### 3. Hub de agentes IA
`GET /agents` sigue siendo un stub (`[]`). Ahora hay bastante más
infraestructura real que antes (Ollama, Open WebUI, Claude
conectado, Flowise) — sigue pendiente decidir qué significa el
"hub": ¿lista de modelos disponibles? ¿links a UIs? ¿registro de
agentes armados en Flowise/LangGraph? Ver también la exploración de
frameworks de agentes (LangChain/LangGraph/Flowise/OpenCode),
documentada aparte, que probablemente informe esta decisión.

---

## Pendiente — prioridad media / deuda técnica conocida

### Migración de DockerService a DockerComposeService
Las apps tipo `service` usan el SDK de Python (`DockerService`), los
proyectos usan el CLI (`DockerComposeService`). Pausado a propósito
— no bloquea nada hoy, pero implica mantener dos rutas de código
para gestionar contenedores.

### Automatización de bases de datos por proyecto
El campo `requires_db` en el modelo `Application` existe pero no se
usa. Hoy es manual (ver `infra/postgres/init/README.md`).

### Reindexación automática de Knowledge Bases
Cada vez que se reinstala Open WebUI, la configuración de Embedding
Model se resetea al default (`sentence-transformers`), y cualquier
Knowledge Base ya indexada necesita **Reindex** manual tras
reconfigurar. Es un paso fácil de olvidar — vale la pena documentarlo
de forma más visible o, a futuro, automatizarlo si Open WebUI expone
un endpoint para eso.

### Variante ARM64/L4T de `opencv-cuda` para Jetson
La imagen `opencv-cuda` construida es x86_64 únicamente (para la
RTX 3050 de la laptop). Para usarla en la Jetson del homelab hace
falta una imagen distinta basada en JetPack/L4T — CUDA de escritorio
y CUDA de Jetson no son intercambiables.

---

## Pendiente — prioridad baja / exploratorio

### Marketplace de templates de terceros
Índice remoto de templates compatibles con el formato de Clauboard,
instalables con un click. No iniciado.

### Debugging con GDB para otros chips además de STM32
El patrón (OpenOCD + puertos publicados + `launch.json` de
Cortex-Debug) ya está resuelto para STM32. Extender a ESP32 (que
también soporta OpenCV/JTAG) no se ha evaluado.

### Testing unitario sin hardware
Zephyr (`native_sim`) y Pico SDK soportan compilar/correr pruebas
en la laptop sin la placa conectada. No evaluado en profundidad.

### Checkbox de componentes opcionales para OpenCV (contrib/CUDA)
Se consideró el mismo patrón de framework/arch (como en los micros)
para elegir entre OpenCV core / contrib / CUDA al crear el proyecto,
pero se descartó: se prefirió una sola imagen completa (`opencv-cuda`,
con todo incluido) construida una vez, en vez de variantes
seleccionables — más simple de mantener, evita repetir el patrón de
"dependencias descubiertas una por una" que costó tiempo con Zephyr.

---

## Decisiones de diseño tomadas (no reabrir sin razón)

- **Sin base de datos propia** — el sistema de archivos es la fuente de verdad
- **Sin Traefik** — mini-DNS con nginx estático + resolver interno de Docker (`127.0.0.11`), por incompatibilidad de versión de API Docker con instalación snap
- **Sin terminal en el navegador** — los toolchains se usan desde la terminal local del host (`docker compose run --rm`, comando copiable desde el dashboard)
- **Sin MQTT Panel** — Serial Studio/TSMaster cubren el monitoreo serial y MQTT mejor
- **Sin Kokoro TTS / sin voz** — no hacía falta para el caso de uso real
- **Sin n8n en Clauboard** — ya existe en el homelab; duplicarlo localmente solo se justificaría para prototipar flujos antes de moverlos ahí (caso concreto: biblioteca personal, Etapa 2), no como instancia permanente paralela
- **Gazebo nativo** — se instala en el host, no en contenedor (rendimiento/GPU/X11)
- **Basys2 FPGA excluido** — Xilinx ISE tiene licencia propietaria, no hay imagen redistribuible legalmente
- **Sin plugins de "acción"** (ej. flashear desde un botón) — herramientas dedicadas ya cubren el caso mejor
- **`restart: unless-stopped`** en todos los contenedores del stack principal e infra — para sobrevivir reinicios de laptop sin `docker compose down`
- **ROS2 con servicios independientes**, seleccionables al crear el proyecto vía checkboxes — no en cadena de herencia de imágenes ni forzados todos juntos
- **Framework/RTOS por chip, no checkboxes de componentes en runtime** — la composición de piezas de un toolchain se resuelve en build-time (una imagen por combinación) o en servicios de compose separados, nunca generando Dockerfiles dinámicamente
- **micro-ROS como checkbox combinable**, no como framework más — es una librería que se agrega a FreeRTOS/Zephyr existentes, no una alternativa a ellos
- **AVR y STM32 sin dispositivo fijo por default** — usan programadores USB genéricos (USBasp, ST-Link), no un puerto serie predecible; el contenedor corre `privileged: true` en su lugar
- **OpenCV: una sola imagen completa (`opencv-cuda`) en vez de variantes seleccionables** — mismo espíritu que la decisión de ROS2/micro-ROS, pero aquí se prefirió simplicidad de mantenimiento sobre flexibilidad de selección, porque contrib/CUDA no son "servicios" sino capacidades de la misma imagen
- **Grafana clasificado como `service`, no `infrastructure`** — el criterio de clasificación es "¿tiene UI que se visita?", no "¿dónde se define el contenedor?"
