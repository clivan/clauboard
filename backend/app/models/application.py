from pydantic import BaseModel, Field

from app.models.application_status import ApplicationStatus
from app.models.application_type import ApplicationType


class PortMapping(BaseModel):
    host: int
    container: int
    protocol: str = "tcp"


class VolumeMapping(BaseModel):
    host: str
    container: str


class Application(BaseModel):

    id: str
    name: str
    description: str

    type: ApplicationType = ApplicationType.SERVICE

    image: str
    container_name: str

    restart: str = "unless-stopped"

    ports: list[PortMapping] = Field(default_factory=list)
    volumes: list[VolumeMapping] = Field(default_factory=list)

    # Passthrough de dispositivos del host, ej. ["/dev/ttyUSB0:/dev/ttyUSB0"].
    # Necesario para toolchains embebidos (AVR/STM32/ESP32) y cámaras (visión).
    devices: list[str] = Field(default_factory=list)

    # Necesario quando el acceso a devices vía --device no basta
    # (ej. algunos casos de USB/JTAG). Úsalo con cautela: da acceso
    # total del host al contenedor.
    privileged: bool = False

    # Puerto interno (dentro del contenedor) usado para armar el
    # alias *.localhost manualmente en proxy/conf.d/ (ver mini-DNS).
    # Solo aplica a type=service.
    primary_port: int | None = None

    environment: dict[str, str] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)

    icon: str | None = None

    status: ApplicationStatus = ApplicationStatus.UNKNOWN