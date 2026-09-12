from pydantic import BaseModel

class Agent(BaseModel):
    """
    Declarado para Sprint 8 (hub de agentes IA), sin implementar
    todavía. Pendiente de definir alcance real antes de construir
    lógica — ver nota en /docs o conversación de diseño.
    """
    id: str
    name: str
    description: str = ""
    backend: str
    model: str | None = None
    url: str | None = None