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
    device: str | None = None
    framework: str | None = None
    arch: str | None = None
    microros: bool = False
    ros2_services: list[str] | None = None


class CloneProjectRequest(BaseModel):
    """DTO para clonar un proyecto existente."""
    new_id: str
    new_name: str
    new_path: str | None = None