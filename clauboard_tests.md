# Clauboard — Checklist de pruebas de punta a punta

Organizado en el mismo orden en que se usa Clauboard de verdad — de
"¿levanta?" a "¿funciona el flujo completo de un proyecto embebido?".
Cada bloque es independiente, se puede correr en sesiones separadas.

## 0. Arranque del sistema

- [ ] `./start.sh` levanta sin errores (infra → stack principal → nginx reload)
- [ ] `docker ps` muestra `clauboard-proxy`, `clauboard-backend`, `clauboard-frontend` como `Up`
- [ ] `http://clauboard.localhost` carga el dashboard sin error de consola
- [ ] `docker logs clauboard-backend --tail 20` no muestra ningún traceback ni `ImportError`
- [ ] Las 4 pestañas (Proyectos, Aplicaciones, Templates, Infraestructura) cargan sin quedarse en blanco

## 1. Infraestructura (`infra/compose.yml`)

- [ ] Los 7 servicios (Postgres, Mongo, InfluxDB, Redis, MinIO, Mosquitto, Grafana) aparecen en la pestaña Infraestructura
- [ ] Cada uno muestra LED de estado correcto (verde si está `Up`, gris si está detenido)
- [ ] Start/Stop desde el dashboard funciona en al menos 2 de ellos
- [ ] No hay botón de Instalar/Desinstalar visible para infraestructura (por diseño)

## 2. Aplicaciones de servicio

- [ ] Instalar una app ligera (ej. Adminer) — confirma que la barra de progreso aparece y desaparece rápido
- [ ] Instalar Ollama — confirma que la barra de progreso muestra MB reales avanzando (prueba real del SSE con algo pesado)
- [ ] Start/Stop/Restart en una app instalada — LED cambia de color correctamente
- [ ] Desinstalar una app — el contenedor desaparece de `docker ps -a`
- [ ] Intenta instalar dos veces la misma app sin desinstalar — no debe duplicar ni romperse
- [ ] Simula una red huérfana: `docker network rm clauboard-net` seguido de recrearla con `docker compose up`, luego dale Start a una app ya instalada — confirma que se reconecta sola (no debería requerir reinstalar)

## 3. Templates (toolchains) — catálogo

- [ ] Los 5 chips (AVR, MSP430, STM32, ESP32, RPi Pico) más ROS2/OpenCV/Yocto aparecen listados
- [ ] Ninguno muestra botón de Instalar (son informativos, se usan vía proyecto)

## 4. Crear proyectos — uno por cada combinación relevante

Para cada chip, valida que el dropdown de Framework se puebla y el checkbox de micro-ROS aparece/desaparece correctamente:

- [ ] **AVR** — Template AVR → Framework muestra solo `baremetal`/`freertos` (sin Zephyr/MicroPython) → sin Arquitectura (una sola) → sin checkbox micro-ROS → campo Dispositivo vacío por default
- [ ] **MSP430** — mismo patrón que AVR, pero Dispositivo se autocompleta con `/dev/ttyACM0`
- [ ] **STM32** — Framework muestra las 4 opciones → elige Zephyr → checkbox micro-ROS aparece → márcalo, confirma que se manda en el payload
- [ ] **ESP32** — Framework muestra las 4 → elige `baremetal` y `freertos` por separado, confirma que ambos casos crean el proyecto sin error (aunque sean la misma imagen)
- [ ] **RPi Pico** — Framework `baremetal` → Arquitectura muestra ARM/RISC-V → cambia entre ambas, confirma que el `.env` generado trae el sufijo correcto
- [ ] **ROS2** — confirma que no aparece dropdown de Framework (no aplica) y que Dispositivo se autocompleta con `/dev/video0`
- [ ] Crea un proyecto con **Ruta personalizada** — confirma que respeta la ruta si está dentro de `CLAUBOARD_PROJECTS_DIR`, y que rechaza con 400 si está fuera

Para cada proyecto creado, verifica en disco:

```bash
tree clauboard-projects/<id>
cat clauboard-projects/<id>/.env
```

- [ ] La estructura de carpetas corresponde al template (AVR trae `Makefile`+`lib/`, ROS2 trae `build/install/log`, STM32 trae `.vscode/launch.json`, etc.)
- [ ] El `.env` trae `MICRO_IMAGE` con el sufijo correcto de framework/arch/microros cuando aplica
- [ ] `compose/compose.yml` existe y no está vacío
- [ ] `.git` existe (se corrió `git init`)
- [ ] Para AVR/MSP430/STM32: `deps.txt` existe con el comentario de ejemplo

## 5. Ciclo de vida del proyecto

- [ ] Botón **Up** — el LED pasa a verde, `docker ps` muestra el contenedor corriendo
- [ ] Botón **Logs** — muestra output real, no vacío ni error
- [ ] Botón **Shell** — el modal muestra el comando completo y correcto (`--env-file`, `-f`, `-p`, servicio); cópialo y córrelo en tu terminal real, confirma que sí te da una shell dentro del contenedor con `src/` montado
- [ ] Botón **Down** — el LED pasa a gris/parado en menos de 5 segundos (prueba del timeout que agregamos)
- [ ] Botón **Restart** — funciona sin quedarse colgado
- [ ] Para ROS2 específicamente: confirma que puedes bajar `vision-processing` sin afectar `ros2`/`realsense-driver` (servicios independientes, no en cadena)

## 6. Clonar proyecto

- [ ] Clona un proyecto existente con nuevo ID y nombre
- [ ] El proyecto clonado aparece en la lista con status `no_compose`/`stopped` inicial correcto
- [ ] La carpeta clonada tiene todos los archivos del original
- [ ] `.git` del clon es un historial nuevo (no el del original)
- [ ] Intenta clonar a un ID que ya existe — debe dar 409, no crear un desastre parcial

## 7. Eliminar proyecto

- [ ] Elimina un proyecto — confirma que la carpeta completa desaparece de disco (`shutil.rmtree`, no solo el registro)
- [ ] Elimina un proyecto que tiene contenedores corriendo — no debe dejar contenedores huérfanos sin bajar primero (valida manualmente con `docker ps`)

## 8. Flujo de compilación real, de punta a punta (el test más importante)

Elige al menos un chip que tengas físicamente disponible:

- [ ] Crea proyecto → Shell → entra al contenedor → escribe un "hola mundo" real en `src/` → `make build` (o `idf.py build`, `colcon build`, según el chip) compila sin error
- [ ] `make flash` (o equivalente) flashea la placa real conectada
- [ ] Sales del contenedor (`exit`) → confirma que el puerto USB queda libre (abre Serial Studio o `screen /dev/ttyUSB0` sin conflicto)

## 9. Gestión de dependencias (AVR / MSP430 / STM32)

- [ ] Agrega una URL de git real a `deps.txt`
- [ ] `make deps` clona el repo a `lib/`
- [ ] Corre `make deps` una segunda vez — confirma que detecta lo ya clonado y no lo re-clona
- [ ] `lib/` no aparece en `git status` (está en `.gitignore`)
- [ ] `make build` compila incluyendo el include path de `lib/` (flag `-Ilib` presente)

## 10. Debug remoto con GDB (STM32)

- [ ] El `compose.yml` del proyecto STM32 publica los puertos `3333` y `4444`
- [ ] Dentro del contenedor, `make debug` levanta OpenOCD y detecta el ST-Link conectado
- [ ] `.vscode/launch.json` existe y es JSON válido
- [ ] En VS Code, con la extensión Cortex-Debug instalada, la configuración "Debug STM32 (OpenOCD remoto, puerto 3333)" aparece en Run and Debug
- [ ] F5 conecta exitosamente y permite poner al menos un breakpoint real en `src/main.c`
- [ ] Ajustar `target/stm32f4x.cfg` a la familia real del chip si no es F4 — confirmar que el cambio manual funciona

## 11. Open WebUI / IA local

- [ ] Ollama instalado y corriendo, `docker exec ollama ollama list` muestra al menos un modelo
- [ ] Open WebUI conecta a Ollama sin el error de Bearer auth (Settings → Connections → Ollama → Auth: None)
- [ ] Un chat normal con `qwen2.5-coder:3b` responde código real (no un tool-call JSON crudo)
- [ ] Adjunta un PDF/DOCX en el chat — confirma que aparece el mensaje `[MarkItDown: ... reducción de tokens]`
- [ ] Knowledge Base del vault de Obsidian — pregúntale algo que solo esté en una nota tuya, confirma que la encuentra

## 12. Mini-DNS

- [ ] `http://clauboard.localhost`, `http://ollama.localhost` (si aplica), y al menos 3 apps más resuelven sin error de nginx
- [ ] `docker exec clauboard-proxy nginx -t` no muestra errores de configuración

## 13. Casos de fallo intencional (mensajes de error útiles)

- [ ] Intenta crear un proyecto con un `id` que ya existe → 409 claro, no un 500 genérico
- [ ] Intenta instalar un toolchain (ej. `esp32`) desde `/applications/esp32/install` directo por curl → 400 explicando por qué no aplica
- [ ] Apaga Docker a medio proceso de instalación de una app pesada → confirma que el dashboard no se queda "colgado" en la barra de progreso para siempre
