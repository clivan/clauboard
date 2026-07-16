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

    # Ruta absoluta donde crear el proyecto. Si no se especifica,
    # se usa PROJECTS_DIR / id (el default de siempre).
    path: str | None = None