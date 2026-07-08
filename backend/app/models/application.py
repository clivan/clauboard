from pydantic import BaseModel, Field

from app.models.application_status import ApplicationStatus


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

    image: str
    container_name: str

    restart: str = "unless-stopped"

    ports: list[PortMapping] = Field(default_factory=list)
    volumes: list[VolumeMapping] = Field(default_factory=list)

    environment: dict[str, str] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)

    icon: str | None = None

    status: ApplicationStatus = ApplicationStatus.UNKNOWN