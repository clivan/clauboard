from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):

    id: str
    name: str
    description: str = ""
    template: str

    path: str

    version: str = "0.1.0"
    created: datetime = Field(default_factory=datetime.utcnow)

    applications: list[str] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
