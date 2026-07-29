# Clauboard

Dashboard local para gestionar entornos de desarrollo dockerizados, con foco en embebidos, robótica y visión por computadora. Inspirado en la idea de combinar Portainer con PlatformIO.

## Idea central

Cada proyecto es un workspace autocontenido con su propio `compose.yml` y `.env`. El dashboard permite inicializar proyectos a partir de templates (AVR, ESP32, ROS2, etc.), encender y apagar entornos, e instalar aplicaciones de servicio (Node-RED, Ollama, Syncthing, etc.) sin tocar la terminal para el día a día.

El desarrollo del código sigue haciéndose en VS Code localmente — el contenedor solo se levanta cuando necesitas compilar, flashear o probar.

## Stack

**Backend:** Python 3.12 + FastAPI + Pydantic  
**Frontend:** HTML + CSS + JavaScript vanilla (sin frameworks)  
**Infraestructura:** Docker Compose  
**Persistencia:** Sistema de archivos + JSON (sin base de datos)

## Estructura del repo

```
clauboard/
  backend/
    app/
      api/          # Endpoints FastAPI (sin lógica)
      managers/     # Orquestan el flujo de negocio
      services/     # Operaciones concretas
      repositories/ # Acceso al sistema de archivos
      models/       # Dominio (Pydantic)
      schemas/      # DTOs de entrada/salida
      registry/
        applications/  # YAML de cada app/toolchain/infra
        templates/     # Dockerfiles de imágenes propias (ROS2, OpenCV)
    templates/      # compose.yml por tipo de proyecto (se copia al crear)
  frontend/
    js/             # api.js, ui.js, project.js, application.js, etc.
  infra/            # compose.yml separado para las bases de datos
  proxy/
    conf.d/         # Un .conf de nginx por app (mini-DNS *.localhost)
  plugins/          # Manifests de plugins (acceso directo a UIs)
  scripts/          # Utilidades: create-data-dirs.sh
  docs/             # Arquitectura, API, roadmap
  start.sh          # Script de arranque completo
```

## Arranque rápido

```bash
# Primera vez
cp .env.example .env
cp infra/.env.example infra/.env
nano infra/.env          # completar contraseñas
sudo scripts/create-data-dirs.sh

# Cada vez (o solo la primera si Docker arranca automático)
./start.sh
```

Dashboard disponible en `http://clauboard.localhost`

## Convenciones de arquitectura

- **Managers** contienen lógica de negocio
- **Services** realizan operaciones concretas
- **Repositories** solo leen/escriben archivos, nunca lógica
- **API** solo expone endpoints, nunca lógica

## Apps y entornos disponibles

Ver `docs/architecture.md` para el catálogo completo.

## Desarrollo futuro

Ver `docs/roadmap.md`.