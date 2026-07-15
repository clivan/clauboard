from fastapi import APIRouter

router = APIRouter(tags=["Agents"])


@router.get("/agents")
def agents():
    # Sprint 8 declarado, no implementado. Pendiente de decidir
    # alcance (¿hub de links? ¿registro con metadata? ¿algo más?)
    # antes de construir un Repository/Manager real, siguiendo el
    # mismo patrón que Plugins tuvo al inicio.
    return []