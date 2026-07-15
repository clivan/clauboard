from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    """
    DTO de entrada para crear un proyecto.
    El backend completa: path, version, created, applications, agents, tags.
    """

    id: str
    name: str
    description: str = ""
    template: str
