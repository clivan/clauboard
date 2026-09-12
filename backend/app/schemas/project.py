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

    # Framework y arquitectura, solo relevantes para templates que los
    # definen (ej. rpi-pico, esp32). Se ignoran silenciosamente en el resto.
    framework: str | None = None
    arch: str | None = None

    # Solo aplica si el framework elegido soporta micro-ROS (ver
    # framework_registry.supports_microros). Se ignora si no aplica.
    microros: bool = False

    # Solo para template=ros2: qué servicios opcionales incluir en el
    # compose.yml generado, además del nodo base ('ros2', siempre
    # presente). Valores válidos: "realsense-driver",
    # "vision-processing", "gazebo". None o [] = solo el nodo base.
    ros2_services: list[str] | None = None


class CloneProjectRequest(BaseModel):
    """DTO para clonar un proyecto existente."""

    new_id: str
    new_name: str
    new_path: str | None = None