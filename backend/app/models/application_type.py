from enum import Enum


class ApplicationType(str, Enum):
    SERVICE = "service"           # Contenedor persistente (docker run -d)
    TOOLCHAIN = "toolchain"        # Shell interactiva (docker compose run --rm)
    INFRASTRUCTURE = "infrastructure"  # Singleton compartido (ej. Postgres)