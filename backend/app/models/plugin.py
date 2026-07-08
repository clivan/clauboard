from pydantic import BaseModel


class Plugin(BaseModel):
    id: str
    type: str
    name: str
    container: str
    icon: str
    url: str