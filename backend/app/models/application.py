from pydantic import BaseModel

class ContainerInfo(BaseModel):

    id: str

    name: str

    image: str

    status: str