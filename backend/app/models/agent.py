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

    # Qué corre detrás del agente, ej. "ollama", "openai-compatible".
    backend: str

    # Modelo específico, ej. "llama3.1:8b". Opcional porque algunos
    # backends no lo requieren (ej. un agente de terceros vía API).
    model: str | None = None

    # Enlace para abrirlo (ej. Open WebUI de tu Jetson Nano),
    # mismo patrón que Plugin.url — un agente puede no tener UI propia.
    url: str | None = None