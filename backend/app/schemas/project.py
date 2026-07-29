from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    """
    DTO de entrada para crear un proyecto.
    El backend completa: version, created, applications, agents, tags
    (y path, si no se especifica uno).
    """

    id: str
    name: str
    description: str = ""
    template: str
    path: str | None = None

    # Dispositivo a pasar al contenedor (ej. /dev/ttyUSB0).
    # Si se especifica, sobreescribe el default del template en el .env.
    device: str | None = None


class CloneProjectRequest(BaseModel):
    """DTO para clonar un proyecto existente."""

    new_id: str
    new_name: str
    new_path: str | None = None