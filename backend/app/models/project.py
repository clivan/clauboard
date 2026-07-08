from pydantic import BaseModel, Field

from datetime import datetime


class Project(BaseModel):

    id: str

    name: str

    description: str = ""

    template: str

    path: str

    created: str = Field(
        default_factory=lambda:
        datetime.now().isoformat()
    )

    version: int = 1

    applications: list[str] = []

    agents: list[str] = []

    tags: list[str] = []